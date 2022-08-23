#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys


def getCurrent():
    """
    Gets the path to the file that is calling the function.
    Takes into account whether it is being called by an executable or python script.

    Returns:
        (string): Path to file calling the getCurrentPath function.
    """
    return sys.executable if getattr(sys, 'frozen', False) else __file__.replace('\\', '/')


def listFullDirectory(directory):
    """
    Convenience method for getting the full path to all the files found in the given directory.

    Args:
        directory (string): Directory to get files from.

    Returns:
        (list): Full path of files and directories in given directory.
    """
    return [os.path.join(directory, path) for path in os.listdir(directory)]


def validateDirectory(directory):
    """
    Creates the given directory if it does not already exist.

    Args:
        directory (string): Directory to create.

    Returns:
        (string): Directory created if it did not already exist.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory


def getAllFilesEndingWithWord(word, starting_directory):
    """
    Gets all the files that end with the given word. Searches from the given starting_directory downwards.

    Args:
        word (string or tuple): Word to filter search.

        starting_directory (string): Name of directory to start search at.

    Returns:
        (list): All files that end with given word inside given starting_directory.
    """
    matched = []

    for directory, _, files in os.walk(starting_directory):
        [matched.append(os.path.join(directory, fn).replace('\\', '/')) for fn in files if fn.endswith(word)]

    return matched


def deleteCompiledScripts(directory=None):
    """
    Deletes all compiled python files (.pyc) from the given directory and all its subdirectories.

    Args:
        directory (string): Name of directory to delete .pyc files from.
    """

    if not directory:
        current_file = getCurrent()
        directory = os.path.dirname(current_file)

    compiled_scripts = getAllFilesEndingWithWord('.pyc', directory)

    if compiled_scripts:
        print('Deleting all compiled python scripts (.pyc) in: ' + directory + '\n')

    [os.remove(script) for script in compiled_scripts]
