"""
FTP command handlers.
Each FTP command has its own function to keep the server clean and modular.
"""

import os
import socket
import random

from users import USERS
from filesystem import (
    create_user_filesystem,
    safe_path,
    get_virtual_path,
    list_directory
)
from status_codes import FTPStatus
from config import *


def send_response(conn, code, message):
    response = f"{int(code)} {message}\r\n"
    conn.sendall(response.encode())


def create_passive_socket():
    for attempt in range(MAX_PASSIVE_PORT_ATTEMPTS):
        data_port = random.randint(PASSIVE_PORT_MIN, PASSIVE_PORT_MAX)

        try:
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            data_socket.bind((HOST, data_port))
            data_socket.listen(1)
            return data_socket, data_port

        except OSError:
            data_socket.close()

    return None, None


def close_passive_socket(session):
    if session["data_socket"] is not None:
        session["data_socket"].close()
        session["data_socket"] = None
        session["data_port"] = None


def reset_data_mode(session):
    close_passive_socket(session)
    session["active_host"] = None
    session["active_port"] = None


def get_data_connection(session):
    if session["data_socket"] is not None:
        data_conn, _ = session["data_socket"].accept()
        return data_conn

    if session["active_host"] is not None and session["active_port"] is not None:
        data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_conn.connect((session["active_host"], session["active_port"]))
        return data_conn

    return None


def finish_data_connection(session):
    close_passive_socket(session)
    session["active_host"] = None
    session["active_port"] = None


def handle_user(conn, session, argument):
    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "Username required")
        return

    if argument in USERS:
        session["username"] = argument
        send_response(
            conn,
            FTPStatus.USERNAME_OK_NEED_PASSWORD,
            "User name okay, need password"
        )
    else:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Invalid username")


def handle_pass(conn, session, argument):
    if session["username"] is None:
        send_response(conn, FTPStatus.BAD_SEQUENCE, "Login with USER first")
        return

    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "Password required")
        return

    username = session["username"]

    if argument == USERS[username]["password"]:
        session["logged_in"] = True
        session["user_home"] = os.path.abspath(USERS[username]["home"])
        session["current_dir"] = session["user_home"]

        create_user_filesystem(session["user_home"])

        send_response(
            conn,
            FTPStatus.USER_LOGGED_IN,
            "User logged in successfully"
        )
    else:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Login incorrect")


def handle_pwd(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    path = get_virtual_path(session["user_home"], session["current_dir"])

    send_response(
        conn,
        FTPStatus.PATHNAME_CREATED,
        f'"{path}"'
    )


def handle_cwd(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "Directory name required")
        return

    new_path = safe_path(
        session["user_home"],
        session["current_dir"],
        argument
    )

    if new_path and os.path.isdir(new_path):
        session["current_dir"] = new_path

        send_response(
            conn,
            FTPStatus.REQUESTED_FILE_ACTION_OK,
            "Directory changed successfully"
        )
    else:
        send_response(
            conn,
            FTPStatus.FILE_UNAVAILABLE,
            "Access denied or directory does not exist"
        )


def handle_cdup(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    if session["current_dir"] == session["user_home"]:
        send_response(
            conn,
            FTPStatus.COMMAND_OK,
            "Already at home directory"
        )
        return

    parent = safe_path(
        session["user_home"],
        session["current_dir"],
        ".."
    )

    if parent and os.path.isdir(parent):
        session["current_dir"] = parent

        send_response(
            conn,
            FTPStatus.COMMAND_OK,
            "Moved to parent directory"
        )
    else:
        send_response(conn, FTPStatus.FILE_UNAVAILABLE, "Access denied")


def handle_mkd(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "Directory name required")
        return

    new_dir = safe_path(
        session["user_home"],
        session["current_dir"],
        argument
    )

    if new_dir is None:
        send_response(conn, FTPStatus.FILE_UNAVAILABLE, "Access denied")
        return

    try:
        os.makedirs(new_dir, exist_ok=False)

        send_response(
            conn,
            FTPStatus.PATHNAME_CREATED,
            "Directory created"
        )

    except FileExistsError:
        send_response(
            conn,
            FTPStatus.FILE_UNAVAILABLE,
            "Directory already exists"
        )


def handle_type(conn, session, argument):
    argument = argument.upper()

    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "Transfer type required")
        return

    if argument == "A" or argument == "A N":
        session["transfer_type"] = "A"

        send_response(
            conn,
            FTPStatus.COMMAND_OK,
            "Type set to ASCII Non-print"
        )
    else:
        send_response(
            conn,
            FTPStatus.PARAMETER_NOT_IMPLEMENTED,
            "Only TYPE A or TYPE A N is supported"
        )


def handle_mode(conn, session, argument):
    argument = argument.upper()

    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "Transfer mode required")
        return

    if argument == "S":
        session["transfer_mode"] = "S"

        send_response(
            conn,
            FTPStatus.COMMAND_OK,
            "Mode set to Stream"
        )
    else:
        send_response(
            conn,
            FTPStatus.PARAMETER_NOT_IMPLEMENTED,
            "Only MODE S is supported"
        )


def handle_stru(conn, session, argument):
    argument = argument.upper()

    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "File structure required")
        return

    if argument == "F":
        session["file_structure"] = "F"

        send_response(
            conn,
            FTPStatus.COMMAND_OK,
            "Structure set to File"
        )
    else:
        send_response(
            conn,
            FTPStatus.PARAMETER_NOT_IMPLEMENTED,
            "Only STRU F is supported"
        )


def handle_noop(conn, session, argument):
    send_response(conn, FTPStatus.COMMAND_OK, "OK")


def handle_pasv(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    reset_data_mode(session)

    data_socket, data_port = create_passive_socket()

    if data_socket is None:
        send_response(
            conn,
            FTPStatus.CANNOT_OPEN_DATA_CONNECTION,
            "Cannot open passive connection"
        )
        return

    session["data_socket"] = data_socket
    session["data_port"] = data_port

    p1 = data_port // 256
    p2 = data_port % 256

    ftp_host = ",".join(HOST.split("."))

    send_response(
        conn,
        FTPStatus.ENTERING_PASSIVE_MODE,
        f"Entering Passive Mode ({ftp_host},{p1},{p2})"
    )


def handle_port(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "PORT arguments required")
        return

    try:
        values = argument.split(",")

        if len(values) != 6:
            raise ValueError

        h1, h2, h3, h4, p1, p2 = values

        active_host = f"{h1}.{h2}.{h3}.{h4}"
        active_port = (int(p1) * 256) + int(p2)

        reset_data_mode(session)

        session["active_host"] = active_host
        session["active_port"] = active_port

        send_response(
            conn,
            FTPStatus.COMMAND_OK,
            f"PORT command successful ({active_host}:{active_port})"
        )

    except ValueError:
        send_response(conn, FTPStatus.SYNTAX_ERROR, "Invalid PORT syntax")


def handle_list(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    send_response(
        conn,
        FTPStatus.FILE_STATUS_OK_OPENING_DATA_CONNECTION,
        "Opening data connection for directory list"
    )

    data_conn = get_data_connection(session)

    if data_conn is None:
        send_response(
            conn,
            FTPStatus.CANNOT_OPEN_DATA_CONNECTION,
            "Use PASV or PORT first"
        )
        return

    try:
        items = list_directory(session["current_dir"])
        listing = "\n".join(items) + "\n"

        data_conn.sendall(listing.encode())
        data_conn.close()

        finish_data_connection(session)

        send_response(
            conn,
            FTPStatus.TRANSFER_COMPLETE,
            "Directory send OK"
        )

    except Exception as error:
        finish_data_connection(session)

        send_response(
            conn,
            FTPStatus.REQUESTED_ACTION_ABORTED,
            f"LIST failed: {error}"
        )


def handle_retr(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "File name required")
        return

    file_path = safe_path(
        session["user_home"],
        session["current_dir"],
        argument
    )

    if file_path is None or not os.path.isfile(file_path):
        send_response(
            conn,
            FTPStatus.FILE_UNAVAILABLE,
            "File not found or access denied"
        )
        return

    send_response(
        conn,
        FTPStatus.FILE_STATUS_OK_OPENING_DATA_CONNECTION,
        "Opening data connection for file transfer"
    )

    data_conn = get_data_connection(session)

    if data_conn is None:
        send_response(
            conn,
            FTPStatus.CANNOT_OPEN_DATA_CONNECTION,
            "Use PASV or PORT first"
        )
        return

    try:
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(FILE_TRANSFER_BUFFER_SIZE)

                if not chunk:
                    break

                data_conn.sendall(chunk)

        data_conn.close()

        finish_data_connection(session)

        send_response(
            conn,
            FTPStatus.TRANSFER_COMPLETE,
            "Transfer complete"
        )

    except Exception as error:
        finish_data_connection(session)

        send_response(
            conn,
            FTPStatus.REQUESTED_ACTION_ABORTED,
            f"Transfer failed: {error}"
        )


def handle_stor(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    if argument == "":
        send_response(conn, FTPStatus.SYNTAX_ERROR, "File name required")
        return

    file_path = safe_path(
        session["user_home"],
        session["current_dir"],
        argument
    )

    if file_path is None:
        send_response(conn, FTPStatus.FILE_UNAVAILABLE, "Access denied")
        return

    if os.path.isdir(file_path):
        send_response(
            conn,
            FTPStatus.FILE_UNAVAILABLE,
            "Cannot overwrite a directory"
        )
        return

    send_response(
        conn,
        FTPStatus.FILE_STATUS_OK_OPENING_DATA_CONNECTION,
        "Opening data connection for file upload"
    )

    data_conn = get_data_connection(session)

    if data_conn is None:
        send_response(
            conn,
            FTPStatus.CANNOT_OPEN_DATA_CONNECTION,
            "Use PASV or PORT first"
        )
        return

    try:
        with open(file_path, "wb") as file:
            while True:
                chunk = data_conn.recv(FILE_TRANSFER_BUFFER_SIZE)

                if not chunk:
                    break

                file.write(chunk)

        data_conn.close()

        finish_data_connection(session)

        send_response(
            conn,
            FTPStatus.TRANSFER_COMPLETE,
            "Upload complete"
        )

    except Exception as error:
        finish_data_connection(session)

        send_response(
            conn,
            FTPStatus.REQUESTED_ACTION_ABORTED,
            f"Upload failed: {error}"
        )


def handle_quit(conn, session, argument):
    reset_data_mode(session)

    send_response(
        conn,
        FTPStatus.SERVICE_CLOSING,
        "Goodbye"
    )

    session["should_close"] = True


def handle_help(conn, session, argument):
    help_text = (
        "Available commands: USER, PASS, PWD, CWD, CDUP, LIST, "
        "MKD, TYPE, MODE, STRU, NOOP, PASV, PORT, RETR, STOR, QUIT"
    )

    send_response(conn, FTPStatus.COMMAND_OK, help_text)


COMMAND_HANDLERS = {
    "USER": handle_user,
    "PASS": handle_pass,
    "PWD": handle_pwd,
    "CWD": handle_cwd,
    "CDUP": handle_cdup,
    "MKD": handle_mkd,
    "TYPE": handle_type,
    "MODE": handle_mode,
    "STRU": handle_stru,
    "NOOP": handle_noop,
    "PASV": handle_pasv,
    "PORT": handle_port,
    "LIST": handle_list,
    "RETR": handle_retr,
    "STOR": handle_stor,
    "QUIT": handle_quit,
    "HELP": handle_help,
}