#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import stat
import platform
import subprocess


def clearReadOnlyFlag(path):
    """
    Clears the read only flag of the given file path.

    Args:
        path (string): Name of file to clear read only flag of.
    """
    os.chmod(path, stat.S_IWUSR | stat.S_IREAD)


def getFileSize(path, accuracy=3, string=True):
    """
    Gets the size of the given file at the path in megabytes.

    Args:
        path (string): Path of file to get size of.

        accuracy (int): How many decimal points to round up to.

        string (boolean): If true, will return a string, else a float.

    Returns:
        (string or float): Size of file in Megabytes.
    """
    size = os.path.getsize(path)
    size = round(size / 1048576.0, accuracy)  # 1048576 is (1024 * 1024).  1024 is the amount of bytes in a kilobyte
    return str(size) + ' MB' if string else size


def openWithOS(path):
    """
    Opens the given path with the OS. Useful for opening windows in Explorer or such.

    Args:
        path (string): Path to open.
    """
    path = os.path.normpath(path)
    subprocess.Popen(r'explorer /select,"{}"'.format(path))


def copyToClipboard(text):
    """
    Copies the given text to the clipboard

    Args:
        text (string): Text to copy to clipboard.
    """
    operating_system = platform.system()

    if operating_system == 'Darwin':  # macOS
        command = 'pbcopy'
    else:
        command = 'clip'  # Windows

    return subprocess.run(command, universal_newlines=True, input=text, shell=True)


def pickText(path, start, end, start_exclude=None):
    """
    Gets all the text in the given file between the given start and end strings.

    Args:
        path (string): Path to file to read lines from.

        start (string): Text that is in line that starts the picking.

        end (string): Text that is in line that ends the picking.

        start_exclude (string): Text to remove from the start of the string and keep the latter.

    Returns:
        (list): Lines between the given start and end strings.
    """
    lines = []
    copy = False
    with open(path) as open_file:
        for line in open_file:
            if start == line.strip():
                copy = True
                continue
            elif end in line.strip():
                break
            elif copy:
                lines.append(line.strip().split(start_exclude)[-1])

    return lines
