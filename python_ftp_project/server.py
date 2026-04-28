"""
Author: Uziel E. Santos

Description:
Main FTP server file.
This file starts the server, accepts client connections,
parses FTP commands, and dispatches each command to its handler.
"""

import socket

from config import (
    HOST,
    CONTROL_PORT,
    MAX_PENDING_CONNECTIONS,
    COMMAND_BUFFER_SIZE,
    DEFAULT_TRANSFER_TYPE,
    DEFAULT_TRANSFER_MODE,
    DEFAULT_FILE_STRUCTURE
)

from command_parser import parse_command
from commands import COMMAND_HANDLERS, send_response
from status_codes import FTPStatus


def create_session():
    """
    Creates a new session state for each connected client.
    """

    return {
        "logged_in": False,
        "username": None,
        "user_home": None,
        "current_dir": None,
        "data_socket": None,
        "data_port": None,
        "active_host": None,
        "active_port": None,
        "transfer_type": DEFAULT_TRANSFER_TYPE,
        "transfer_mode": DEFAULT_TRANSFER_MODE,
        "file_structure": DEFAULT_FILE_STRUCTURE,
        "should_close": False,
    }


def handle_client(conn, addr):
    """
    Handles one connected client.
    """

    print(f"Connection from {addr}")

    session = create_session()

    send_response(
        conn,
        FTPStatus.SERVICE_READY,
        "FTP Server ready"
    )

    while not session["should_close"]:

        data = conn.recv(
            COMMAND_BUFFER_SIZE
        ).decode().strip()

        if not data:
            break

        print(f"Client: {data}")

        command, argument = parse_command(data)

        handler = COMMAND_HANDLERS.get(command)

        if handler is None:
            send_response(
                conn,
                FTPStatus.COMMAND_NOT_IMPLEMENTED,
                "Command not implemented yet"
            )
            continue

        handler(conn, session, argument)

    conn.close()


def start_server():
    """
    Starts the FTP server.
    """

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (
            HOST,
            CONTROL_PORT
        )
    )

    server_socket.listen(
        MAX_PENDING_CONNECTIONS
    )

    print(
        f"FTP Server running on {HOST}:{CONTROL_PORT}"
    )

    while True:

        conn, addr = server_socket.accept()

        handle_client(conn, addr)


if __name__ == "__main__":
    start_server()