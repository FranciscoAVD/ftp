"""
FTP client implementation.

Supports:
- USER / PASS
- PWD / CWD / CDUP
- LIST through PASV or PORT data connection
- PASV
- PORT
- RETR
- STOR
- TYPE
- MODE
- STRU
- NOOP
- HELP
- QUIT
"""

import socket
import re
import os
import random

from config import (
    HOST,
    CONTROL_PORT,
    FILE_TRANSFER_BUFFER_SIZE,
    DOWNLOAD_FOLDER,
    UPLOAD_FOLDER,
    ACTIVE_HOST,
    ACTIVE_PORT_MIN,
    ACTIVE_PORT_MAX,
    MAX_ACTIVE_PORT_ATTEMPTS
)


def receive_response(sock):
    """
    Receives and prints one server response.
    """

    response = sock.recv(
        FILE_TRANSFER_BUFFER_SIZE
    ).decode()

    print(response, end="")

    return response


def parse_pasv_response(response):
    """
    Parses PASV response and extracts host and port.
    """

    match = re.search(
        r"\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)",
        response
    )

    if not match:
        return None, None

    h1, h2, h3, h4, p1, p2 = match.groups()

    data_host = f"{h1}.{h2}.{h3}.{h4}"
    data_port = (int(p1) * 256) + int(p2)

    return data_host, data_port


def create_active_socket():
    """
    Creates an active mode socket.
    Client opens a port and waits for server to connect.
    """

    for attempt in range(MAX_ACTIVE_PORT_ATTEMPTS):

        active_port = random.randint(
            ACTIVE_PORT_MIN,
            ACTIVE_PORT_MAX
        )

        try:
            active_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            active_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            active_socket.bind(
                (
                    ACTIVE_HOST,
                    active_port
                )
            )

            active_socket.listen(1)

            return active_socket, active_port

        except OSError:
            active_socket.close()

    return None, None


def build_port_argument(host, port):
    """
    Converts host and port into FTP PORT command format.
    """

    h1, h2, h3, h4 = host.split(".")

    p1 = port // 256
    p2 = port % 256

    return f"{h1},{h2},{h3},{h4},{p1},{p2}"


def receive_data_from_socket(data_socket, output_path=None):
    """
    Receives data from a data socket.
    If output_path is provided, saves data to a file.
    Otherwise, prints it to the screen.
    """

    data_conn, _ = data_socket.accept()

    if output_path:

        with open(output_path, "wb") as file:

            while True:

                chunk = data_conn.recv(
                    FILE_TRANSFER_BUFFER_SIZE
                )

                if not chunk:
                    break

                file.write(chunk)

    else:

        chunks = []

        while True:

            chunk = data_conn.recv(
                FILE_TRANSFER_BUFFER_SIZE
            )

            if not chunk:
                break

            chunks.append(chunk)

        print(
            b"".join(chunks).decode(),
            end=""
        )

    data_conn.close()
    data_socket.close()


def download_pasv(data_host, data_port, filename):
    """
    Downloads file using PASV mode.
    """

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    output_path = os.path.join(
        DOWNLOAD_FOLDER,
        os.path.basename(filename)
    )

    data_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        data_socket.connect((data_host, data_port))

        with open(output_path, "wb") as file:

            while True:

                chunk = data_socket.recv(
                    FILE_TRANSFER_BUFFER_SIZE
                )

                if not chunk:
                    break

                file.write(chunk)

        print(f"Downloaded file saved as: {output_path}")

    finally:
        data_socket.close()


def upload_pasv(data_host, data_port, filename):
    """
    Uploads file using PASV mode.
    """

    input_path = os.path.join(
        UPLOAD_FOLDER,
        os.path.basename(filename)
    )

    if not os.path.isfile(input_path):
        print(f"Client error: file not found in {UPLOAD_FOLDER}")
        return False

    data_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        data_socket.connect((data_host, data_port))

        with open(input_path, "rb") as file:

            while True:

                chunk = file.read(
                    FILE_TRANSFER_BUFFER_SIZE
                )

                if not chunk:
                    break

                data_socket.sendall(chunk)

        print(f"Uploaded file from: {input_path}")
        return True

    finally:
        data_socket.close()


def list_pasv(data_host, data_port):
    """
    Receives LIST data using PASV mode.
    """

    data_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        data_socket.connect((data_host, data_port))

        chunks = []

        while True:

            chunk = data_socket.recv(
                FILE_TRANSFER_BUFFER_SIZE
            )

            if not chunk:
                break

            chunks.append(chunk)

        print(b"".join(chunks).decode(), end="")

    finally:
        data_socket.close()


def print_menu():
    """
    Prints available FTP commands.
    """

    print("Commands available:")
    print("USER username")
    print("PASS password")
    print("PWD")
    print("LIST")
    print("CWD foldername")
    print("CDUP")
    print("MKD foldername")
    print("TYPE A")
    print("TYPE A N")
    print("MODE S")
    print("STRU F")
    print("NOOP")
    print("PASV")
    print("PORT")
    print("RETR filename")
    print("STOR filename")
    print("HELP")
    print("QUIT")
    print()


def start_client():
    """
    Starts the FTP client.
    """

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    data_host = None
    data_port = None
    active_socket = None

    try:
        client_socket.connect((HOST, CONTROL_PORT))

        receive_response(client_socket)

        print_menu()

        while True:

            command = input("ftp> ")

            if command.strip() == "":
                continue

            parts = command.split(" ", 1)
            command_name = parts[0].upper()
            argument = parts[1].strip() if len(parts) > 1 else ""

            # PASV
            if command_name == "PASV":

                client_socket.sendall(
                    (command + "\r\n").encode()
                )

                response = receive_response(client_socket)

                data_host, data_port = parse_pasv_response(response)
                active_socket = None

                if data_host and data_port:
                    print(
                        f"Passive data connection ready at "
                        f"{data_host}:{data_port}"
                    )

                continue

            # PORT
            if command_name == "PORT":

                if active_socket is not None:
                    active_socket.close()
                    active_socket = None

                active_socket, active_port = create_active_socket()

                if active_socket is None:
                    print("Client error: could not open active port")
                    continue

                port_argument = build_port_argument(
                    ACTIVE_HOST,
                    active_port
                )

                port_command = f"PORT {port_argument}"

                client_socket.sendall(
                    (port_command + "\r\n").encode()
                )

                receive_response(client_socket)

                data_host = None
                data_port = None

                print(
                    f"Active data port ready at "
                    f"{ACTIVE_HOST}:{active_port}"
                )

                continue

            # LIST
            if command_name == "LIST":

                client_socket.sendall(
                    (command + "\r\n").encode()
                )

                response = receive_response(client_socket)

                if response.startswith("150"):

                    if active_socket is not None:
                        receive_data_from_socket(active_socket)
                        active_socket = None

                    elif data_host is not None and data_port is not None:
                        list_pasv(data_host, data_port)

                    receive_response(client_socket)

                data_host = None
                data_port = None
                continue

            # RETR
            if command_name == "RETR":

                if argument == "":
                    print("Client error: filename required")
                    continue

                os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

                output_path = os.path.join(
                    DOWNLOAD_FOLDER,
                    os.path.basename(argument)
                )

                client_socket.sendall(
                    (command + "\r\n").encode()
                )

                response = receive_response(client_socket)

                if response.startswith("150"):

                    if active_socket is not None:
                        receive_data_from_socket(
                            active_socket,
                            output_path
                        )
                        active_socket = None
                        print(f"Downloaded file saved as: {output_path}")

                    elif data_host is not None and data_port is not None:
                        download_pasv(
                            data_host,
                            data_port,
                            argument
                        )

                    receive_response(client_socket)

                data_host = None
                data_port = None
                continue

            # STOR
            if command_name == "STOR":

                if argument == "":
                    print("Client error: filename required")
                    continue

                input_path = os.path.join(
                    UPLOAD_FOLDER,
                    os.path.basename(argument)
                )

                if not os.path.isfile(input_path):
                    print(f"Client error: file not found in {UPLOAD_FOLDER}")
                    continue

                client_socket.sendall(
                    (command + "\r\n").encode()
                )

                response = receive_response(client_socket)

                if response.startswith("150"):

                    if active_socket is not None:

                        data_conn, _ = active_socket.accept()

                        with open(input_path, "rb") as file:

                            while True:

                                chunk = file.read(
                                    FILE_TRANSFER_BUFFER_SIZE
                                )

                                if not chunk:
                                    break

                                data_conn.sendall(chunk)

                        data_conn.close()
                        active_socket.close()
                        active_socket = None

                        print(f"Uploaded file from: {input_path}")

                    elif data_host is not None and data_port is not None:

                        upload_pasv(
                            data_host,
                            data_port,
                            argument
                        )

                    receive_response(client_socket)

                data_host = None
                data_port = None
                continue

            # NORMAL COMMANDS
            client_socket.sendall(
                (command + "\r\n").encode()
            )

            response = receive_response(client_socket)

            if command_name == "QUIT":
                break

    except ConnectionRefusedError:
        print("ERROR: Server is not running.")
        print("Run server.py first.")

    except KeyboardInterrupt:
        print("\nClient closed.")

    finally:

        if active_socket is not None:
            active_socket.close()

        client_socket.close()


if __name__ == "__main__":
    start_client()