"""
FTP status codes used by the server.
Using named constants makes the code more readable than using raw numbers.
"""

from enum import IntEnum


class FTPStatus(IntEnum):
    # 1xx Positive Preliminary replies
    FILE_STATUS_OK_OPENING_DATA_CONNECTION = 150

    # 2xx Positive Completion replies
    COMMAND_OK = 200
    SERVICE_READY = 220
    SERVICE_CLOSING = 221
    DATA_CONNECTION_OPEN = 225
    TRANSFER_COMPLETE = 226
    ENTERING_PASSIVE_MODE = 227
    USER_LOGGED_IN = 230
    REQUESTED_FILE_ACTION_OK = 250
    PATHNAME_CREATED = 257

    # 3xx Positive Intermediate replies
    USERNAME_OK_NEED_PASSWORD = 331

    # 4xx Transient Negative Completion replies
    CANNOT_OPEN_DATA_CONNECTION = 425
    REQUESTED_ACTION_ABORTED = 451

    # 5xx Permanent Negative Completion replies
    SYNTAX_ERROR = 501
    COMMAND_NOT_IMPLEMENTED = 502
    BAD_SEQUENCE = 503
    PARAMETER_NOT_IMPLEMENTED = 504
    NOT_LOGGED_IN = 530
    FILE_UNAVAILABLE = 550