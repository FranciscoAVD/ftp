"""
File system helper functions for the FTP server.
This file manages user folders, safe paths, virtual paths, and directory listing.
"""

import os


# Default folders required for each FTP user
DEFAULT_DIRECTORIES = ["docs", "images", "misc"]

# Number of default files created inside each default folder
FILES_PER_DIRECTORY = 5


def create_user_filesystem(user_home):
    """
    Creates the required folder and file structure for a user.
    """

    # Convert user home to absolute path
    user_home = os.path.abspath(user_home)

    # Create user's home directory
    os.makedirs(user_home, exist_ok=True)

    # Create default folders and files
    for folder in DEFAULT_DIRECTORIES:

        # Build folder path
        folder_path = os.path.join(user_home, folder)

        # Create folder
        os.makedirs(folder_path, exist_ok=True)

        # Create five sample files
        for i in range(1, FILES_PER_DIRECTORY + 1):

            # Build file path
            file_path = os.path.join(folder_path, f"file{i}.txt")

            # Only create file if it does not exist
            if not os.path.exists(file_path):

                # Write sample content
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(
                        f"This is file {i} inside the {folder} directory.\n"
                    )


def safe_path(user_home, current_dir, requested_path):
    """
    Validates that a requested path stays inside the user's home directory.
    Prevents directory traversal attacks such as ../../Admin.
    """

    # Convert home to absolute path
    user_home = os.path.abspath(user_home)

    # If FTP absolute path is used, start from user home
    if requested_path.startswith("/"):
        new_path = os.path.join(user_home, requested_path.lstrip("/"))

    # Otherwise start from current directory
    else:
        new_path = os.path.join(current_dir, requested_path)

    # Convert requested path to absolute path
    new_path = os.path.abspath(new_path)

    # Make sure new path stays inside user home
    if os.path.commonpath([user_home, new_path]) != user_home:
        return None

    # Return validated path
    return new_path


def get_virtual_path(user_home, current_dir):
    """
    Converts a real system path into a virtual FTP path.
    """

    # Get relative path from user home
    relative_path = os.path.relpath(current_dir, user_home)

    # Root directory appears as /
    if relative_path == ".":
        return "/"

    # Convert Windows separators to FTP separators
    return "/" + relative_path.replace("\\", "/")


def list_directory(current_dir):
    """
    Returns a formatted directory listing.
    """

    # Read items in current directory
    items = os.listdir(current_dir)

    # Store formatted output
    result = []

    # Format each item
    for item in items:

        # Get full path
        item_path = os.path.join(current_dir, item)

        # Mark directories
        if os.path.isdir(item_path):
            result.append(f"[DIR]  {item}")

        # Mark files
        else:
            result.append(f"[FILE] {item}")

    # Return listing
    return result