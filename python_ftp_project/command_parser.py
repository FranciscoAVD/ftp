"""
Command parser for FTP commands.
This separates command parsing from server logic.
"""


def parse_command(data):
    """
    Parses raw client input into command and argument.

    Example:
    Input:  "USER Uziel"
    Output: ("USER", "Uziel")
    """

    # Remove extra spaces and line endings
    data = data.strip()

    # Split command from argument once
    parts = data.split(" ", 1)

    # First part is always the command
    command = parts[0].upper()

    # Second part is optional argument
    argument = parts[1].strip() if len(parts) > 1 else ""

    # Return parsed command and argument
    return command, argument