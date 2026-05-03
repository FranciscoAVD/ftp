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


# 🔥 NUEVO (para FTP Windows)
def handle_syst(conn, session, argument):
    send_response(conn, FTPStatus.COMMAND_OK, "UNIX Type: L8")


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
        send_response(conn, FTPStatus.USERNAME_OK_NEED_PASSWORD,
                      "User name okay, need password")
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

        send_response(conn, FTPStatus.USER_LOGGED_IN,
                      "User logged in successfully")
    else:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Login incorrect")


def handle_pwd(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    path = get_virtual_path(session["user_home"], session["current_dir"])

    send_response(conn, FTPStatus.PATHNAME_CREATED, f'"{path}"')


def handle_cwd(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    new_path = safe_path(
        session["user_home"], session["current_dir"], argument
    )

    if new_path and os.path.isdir(new_path):
        session["current_dir"] = new_path
        send_response(conn, FTPStatus.REQUESTED_FILE_ACTION_OK,
                      "Directory changed successfully")
    else:
        send_response(conn, FTPStatus.FILE_UNAVAILABLE,
                      "Directory does not exist")


def handle_list(conn, session, argument):
    if not session["logged_in"]:
        send_response(conn, FTPStatus.NOT_LOGGED_IN, "Please login first")
        return

    send_response(conn, FTPStatus.FILE_STATUS_OK_OPENING_DATA_CONNECTION,
                  "Opening data connection")

    data_conn = get_data_connection(session)

    if data_conn is None:
        send_response(conn, FTPStatus.CANNOT_OPEN_DATA_CONNECTION,
                      "Use PASV or PORT first")
        return

    items = list_directory(session["current_dir"])
    listing = "\n".join(items) + "\n"

    data_conn.sendall(listing.encode())
    data_conn.close()

    finish_data_connection(session)

    send_response(conn, FTPStatus.TRANSFER_COMPLETE,
                  "Directory send OK")


def handle_quit(conn, session, argument):
    reset_data_mode(session)
    send_response(conn, FTPStatus.SERVICE_CLOSING, "Goodbye")
    session["should_close"] = True


def handle_help(conn, session, argument):
    send_response(conn, FTPStatus.COMMAND_OK,
                  "Commands: USER PASS PWD CWD LIST QUIT")


# 🔥 IMPORTANTE: aliases para Windows FTP
COMMAND_HANDLERS = {
    "USER": handle_user,
    "PASS": handle_pass,

    "PWD": handle_pwd,
    "XPWD": handle_pwd,

    "CWD": handle_cwd,
    "XCWD": handle_cwd,

    "LIST": handle_list,
    "NLST": handle_list,

    "SYST": handle_syst,

    "QUIT": handle_quit,
    "HELP": handle_help,
}
