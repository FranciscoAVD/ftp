# Import socket library for TCP communication
import socket


# Server IP address
HOST = "127.0.0.1"

# Server port number
PORT = 2121


# Function that receives and prints server responses
def receive_response(sock):

    # Receive a message from the server and decode it
    response = sock.recv(4096).decode()

    # Print the server response
    print(response, end="")


# Main function for the FTP client
def start_client():

    # Create a TCP socket using IPv4
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Try to connect to the server
    try:

        # Connect to the FTP server
        client_socket.connect((HOST, PORT))

        # Receive the server welcome message
        receive_response(client_socket)

        # Print available commands for the user
        print("Commands available:")

        # Shows USER command
        print("USER username")

        # Shows PASS command
        print("PASS password")

        # Shows PWD command
        print("PWD")

        # Shows LIST command
        print("LIST")

        # Shows CWD command
        print("CWD foldername")

        # Shows CDUP command
        print("CDUP")

        # Shows MKD command
        print("MKD foldername")

        # Shows QUIT command
        print("QUIT")

        # Print empty line
        print()

        # Keep asking the user for FTP commands
        while True:

            # Ask the user to type a command
            command = input("ftp> ")

            # Ignore empty commands
            if command.strip() == "":

                # Continue asking for input
                continue

            # Send the command to the server using CRLF format
            client_socket.sendall((command + "\r\n").encode())

            # Receive and print the server response
            receive_response(client_socket)

            # Check if the user entered QUIT
            if command.upper().startswith("QUIT"):

                # Exit the loop
                break

    # Handle error if server is not running
    except ConnectionRefusedError:

        # Print error message
        print("ERROR: Server is not running.")

        # Tell user how to fix it
        print("Run server.py first.")

    # Handle Ctrl + C
    except KeyboardInterrupt:

        # Print client closed message
        print("\nClient closed.")

    # Always close the socket
    finally:

        # Close the TCP connection
        client_socket.close()


# Run client only if this file is executed directly
if __name__ == "__main__":

    # Start the FTP client
    start_client()