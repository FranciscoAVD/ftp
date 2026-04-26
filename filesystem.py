# Import os library to work with files, folders, and paths
import os


# Default directories required for each FTP user
DEFAULT_DIRECTORIES = ["docs", "images", "misc"]

# Number of files that will be created inside each default directory
FILES_PER_DIRECTORY = 5


# Function that creates the required file system for each user
def create_user_filesystem(user_home):

    # Convert the user's home directory into an absolute path
    user_home = os.path.abspath(user_home)

    # Create the user home directory if it does not exist
    os.makedirs(user_home, exist_ok=True)

    # Loop through each default directory name
    for folder in DEFAULT_DIRECTORIES:

        # Create the full path for the current folder
        folder_path = os.path.join(user_home, folder)

        # Create the folder if it does not already exist
        os.makedirs(folder_path, exist_ok=True)

        # Create five files inside each folder
        for i in range(1, FILES_PER_DIRECTORY + 1):

            # Create the full file path
            file_path = os.path.join(folder_path, f"file{i}.txt")

            # Only create the file if it does not already exist
            if not os.path.exists(file_path):

                # Open the file in write mode
                with open(file_path, "w", encoding="utf-8") as file:

                    # Write sample content inside the file
                    file.write(f"This is file {i} inside the {folder} directory.\n")


# Function that validates paths to prevent unauthorized access
def safe_path(user_home, current_dir, requested_path):

    # Convert the user's home directory into an absolute path
    user_home = os.path.abspath(user_home)

    # Check if the requested path starts from the virtual FTP root
    if requested_path.startswith("/"):

        # Build a path starting from the user's private home directory
        new_path = os.path.join(user_home, requested_path.lstrip("/"))

    else:

        # Build a path starting from the user's current directory
        new_path = os.path.join(current_dir, requested_path)

    # Convert the new path into an absolute path
    new_path = os.path.abspath(new_path)

    # Check if the new path is still inside the user's home directory
    if os.path.commonpath([user_home, new_path]) != user_home:

        # Return None if the user is trying to leave their allowed directory
        return None

    # Return the safe path if it is valid
    return new_path


# Function that converts a real system path into a virtual FTP path
def get_virtual_path(user_home, current_dir):

    # Get the path relative to the user's home directory
    relative_path = os.path.relpath(current_dir, user_home)

    # If the relative path is ".", the user is at the FTP root
    if relative_path == ".":

        # Return FTP virtual root
        return "/"

    # Return the path using FTP-style forward slashes
    return "/" + relative_path.replace("\\", "/")


# Function that lists files and folders inside the current directory
def list_directory(current_dir):

    # Get all items inside the current directory
    items = os.listdir(current_dir)

    # Create an empty list to store formatted results
    result = []

    # Loop through each item
    for item in items:

        # Create the full path of the item
        item_path = os.path.join(current_dir, item)

        # Check if the item is a directory
        if os.path.isdir(item_path):

            # Add directory label
            result.append(f"[DIR]  {item}")

        else:

            # Add file label
            result.append(f"[FILE] {item}")

    # Return the formatted directory list
    return result