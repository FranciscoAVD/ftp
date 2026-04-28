"""
Configuration constants for the FTP Client-Server project.
This file removes arbitrary numbers from the code and gives them clear names.
"""

# Server network configuration
HOST = "127.0.0.1"
CONTROL_PORT = 2121

# Socket configuration
MAX_PENDING_CONNECTIONS = 5
COMMAND_BUFFER_SIZE = 1024
FILE_TRANSFER_BUFFER_SIZE = 4096

# Passive mode port range
PASSIVE_PORT_MIN = 49152
PASSIVE_PORT_MAX = 65535
MAX_PASSIVE_PORT_ATTEMPTS = 100

# Client folders
DOWNLOAD_FOLDER = "client_downloads"
UPLOAD_FOLDER = "client_uploads"

# Active mode configuration
ACTIVE_HOST = "127.0.0.1"
ACTIVE_PORT_MIN = 49152
ACTIVE_PORT_MAX = 65535
MAX_ACTIVE_PORT_ATTEMPTS = 100

# Default FTP transfer settings
DEFAULT_TRANSFER_TYPE = "A"
DEFAULT_TRANSFER_MODE = "S"
DEFAULT_FILE_STRUCTURE = "F"