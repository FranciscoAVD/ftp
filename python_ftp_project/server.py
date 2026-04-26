"""
Author: Uziel E. Santos
Description: This is a simple FTP server implementation in Python.
 It supports basic FTP commands such as USER, PASS, PWD, CWD, CDUP, LIST, MKD, and QUIT. 
 The server uses a predefined set of users with their respective passwords and home directories. 
 The server ensures that users can only access their own home directories and prevents directory traversal attacks.
 Date: 4/25/2026
 """

# Import socket library for TCP communication
import socket

# Import os library for file and path operations
import os

# Import user accounts from users.py
from users import USERS

# Import file system helper functions from filesystem.py
from filesystem import create_user_filesystem, safe_path, get_virtual_path, list_directory


# Localhost IP address
HOST = "127.0.0.1"

# Server port number
PORT = 2121


# Function used to send FTP-style responses to the client
def send_response(conn, code, message):

    # Build the response using an FTP reply code and message
    response = f"{code} {message}\r\n"

    # Encode the response and send it through the TCP connection
    conn.sendall(response.encode())


# Function that handles a connected FTP client
def handle_client(conn, addr):

    # Print the address of the connected client
    print(f"Connection from {addr}")

    # Variable that tracks if the user is logged in
    logged_in = False

    # Variable that stores the current username
    username = None

    # Variable that stores the user's private home directory
    user_home = None

    # Variable that stores the user's current working directory
    current_dir = None

    # Send the initial FTP welcome message
    send_response(conn, 220, "FTP Server ready")

    # Keep receiving commands while the client is connected
    while True:

        # Receive data from the client, decode it, and remove extra spaces
        data = conn.recv(1024).decode().strip()

        # If no data is received, close the loop
        if not data:
            break

        # Print the received client command on the server side
        print(f"Client: {data}")

        # Split the command into command name and argument
        parts = data.split(" ", 1)

        # Store the command in uppercase to make it case-insensitive
        command = parts[0].upper()

        # Store the argument if it exists; otherwise use an empty string
        argument = parts[1].strip() if len(parts) > 1 else ""

        # ---------------- USER COMMAND ----------------
        if command == "USER":

            # Check if the username argument is missing
            if argument == "":

                # Send syntax error because username is required
                send_response(conn, 501, "Username required")

                # Continue waiting for the next command
                continue

            # Check if the username exists in the USERS dictionary
            if argument in USERS:

                # Store the username temporarily
                username = argument

                # Ask the client for the password
                send_response(conn, 331, "User name okay, need password")

            else:

                # Send error if the username does not exist
                send_response(conn, 530, "Invalid username")

        # ---------------- PASS COMMAND ----------------
        elif command == "PASS":

            # Check if USER was not entered first
            if username is None:

                # Tell the client to send USER before PASS
                send_response(conn, 503, "Login with USER first")

                # Continue waiting for next command
                continue

            # Check if the password argument is missing
            if argument == "":

                # Send syntax error because password is required
                send_response(conn, 501, "Password required")

                # Continue waiting for next command
                continue

            # Compare entered password with the stored password
            if argument == USERS[username]["password"]:

                # Mark user as logged in
                logged_in = True

                # Get the absolute path of the user's private home directory
                user_home = os.path.abspath(USERS[username]["home"])

                # Set the current directory to the user's home directory
                current_dir = user_home

                # Create the user's required file system structure
                create_user_filesystem(user_home)

                # Send successful login response
                send_response(conn, 230, "User logged in successfully")

            else:

                # Send error if password is incorrect
                send_response(conn, 530, "Login incorrect")

        # ---------------- PWD COMMAND ----------------
        elif command == "PWD":

            # Check if user is not logged in
            if not logged_in:

                # Send authentication required error
                send_response(conn, 530, "Please login first")

                # Continue waiting for next command
                continue

            # Get the virtual FTP path
            display_path = get_virtual_path(user_home, current_dir)

            # Check if user is at home directory
            if display_path == "/":

                # Send home directory response
                send_response(conn, 257, '"Home Directory (/)"')

            else:

                # Send current virtual path
                send_response(conn, 257, f'"{display_path}"')

        # ---------------- CWD COMMAND ----------------
        elif command == "CWD":

            # Check if user is not logged in
            if not logged_in:

                # Send authentication required error
                send_response(conn, 530, "Please login first")

                # Continue waiting for next command
                continue

            # Check if directory argument is missing
            if argument == "":

                # Send syntax error because directory name is required
                send_response(conn, 501, "Directory name required")

                # Continue waiting for next command
                continue

            # Validate the requested directory path
            new_path = safe_path(user_home, current_dir, argument)

            # Check if path is safe and points to a real directory
            if new_path and os.path.isdir(new_path):

                # Change the current working directory
                current_dir = new_path

                # Send success response
                send_response(conn, 250, "Directory changed successfully")

            else:

                # Send error if access is denied or directory does not exist
                send_response(conn, 550, "Access denied or directory does not exist")

        # ---------------- CDUP COMMAND ----------------
        elif command == "CDUP":

            # Check if user is not logged in
            if not logged_in:

                # Send authentication required error
                send_response(conn, 530, "Please login first")

                # Continue waiting for next command
                continue

            # Check if the user is already at home directory
            if current_dir == user_home:

                # Tell the user they are already at home
                send_response(conn, 200, "Already at home directory")

                # Continue waiting for next command
                continue

            # Validate the parent directory path
            parent_path = safe_path(user_home, current_dir, "..")

            # Check if the parent path is safe and exists
            if parent_path and os.path.isdir(parent_path):

                # Move to the parent directory
                current_dir = parent_path

                # Send success response
                send_response(conn, 200, "Moved to parent directory")

            else:

                # Send access denied response
                send_response(conn, 550, "Access denied")

        # ---------------- LIST COMMAND ----------------
        elif command == "LIST":

            # Check if user is not logged in
            if not logged_in:

                # Send authentication required error
                send_response(conn, 530, "Please login first")

                # Continue waiting for next command
                continue

            # Get formatted directory listing
            items = list_directory(current_dir)

            # Check if the directory is empty
            if not items:

                # Send empty directory response
                send_response(conn, 226, "Directory is empty")

            else:

                # Join directory items into one text block
                listing = "\n".join(items)

                # Send directory listing response
                send_response(conn, 226, f"\n{listing}")

        # ---------------- MKD COMMAND ----------------
        elif command == "MKD":

            # Check if user is not logged in
            if not logged_in:

                # Send authentication required error
                send_response(conn, 530, "Please login first")

                # Continue waiting for next command
                continue

            # Check if directory name is missing
            if argument == "":

                # Send syntax error because directory name is required
                send_response(conn, 501, "Directory name required")

                # Continue waiting for next command
                continue

            # Validate the new directory path
            new_dir = safe_path(user_home, current_dir, argument)

            # Check if the new directory path is safe
            if new_dir:

                # Try to create the directory
                try:

                    # Create the new directory
                    os.makedirs(new_dir, exist_ok=False)

                    # Send directory created response
                    send_response(conn, 257, "Directory created")

                # Handle error if directory already exists
                except FileExistsError:

                    # Send directory already exists response
                    send_response(conn, 550, "Directory already exists")

            else:

                # Send access denied response
                send_response(conn, 550, "Access denied")

        # ---------------- QUIT COMMAND ----------------
        elif command == "QUIT":

            # Send goodbye response
            send_response(conn, 221, "Goodbye")

            # Exit the command loop
            break

        # ---------------- UNKNOWN COMMAND ----------------
        else:

            # Send command not implemented response
            send_response(conn, 502, "Command not implemented yet")

    # Close the TCP connection with the client
    conn.close()


# Function that starts the FTP server
def start_server():

    # Create a TCP socket using IPv4
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow the socket address to be reused
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the selected host and port
    server_socket.bind((HOST, PORT))

    # Start listening for client connections
    server_socket.listen(5)

    # Print server running message
    print(f"FTP Server running on {HOST}:{PORT}")

    # Keep server running forever
    while True:

        # Accept a new client connection
        conn, addr = server_socket.accept()

        # Handle the connected client
        handle_client(conn, addr)


# Run the server only if this file is executed directly
if __name__ == "__main__":

    # Start the FTP server
    start_server()