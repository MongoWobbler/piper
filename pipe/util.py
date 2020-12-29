#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import sys


def getCurrentPath():
    """
    Gets the path to the file that is calling the function.
    Takes into account whether it is being called by an executable or python script.

    Returns:
        (string): Path to file calling the getCurrentPath function.
    """
    return sys.executable if getattr(sys, 'frozen', False) else __file__.replace('\\', '/')


def getAllFilesEndingWithWord(word, starting_directory):
    """
    Gets all the files that end with the given word. Searches from the given starting_directory downwards.

    Args:
        word (string or tuple): Word to filter search.

        starting_directory (string): Name of directory to start search at.

    Returns:
        (list): All files that end with given word inside given starting_directory.
    """
    matched_files = []

    for directory, _, files in os.walk(starting_directory):
        for file_name in files:
            if file_name.lower().endswith(word):
                directory = directory.replace('\\', '/')
                matched_files.append(os.path.join(directory, file_name))

    return matched_files


def deleteCompiledScripts(directory=None):
    """
    Deletes all compiled python files (.pyc) from the given directory and all its subdirectories.

    Args:
        directory (string): Name of directory to delete .pyc files from.
    """

    if not directory:
        current_file = getCurrentPath()
        directory = os.path.dirname(current_file)

    compiled_scripts = getAllFilesEndingWithWord('.pyc', directory)

    if compiled_scripts:
        print('Deleting all compiled python scripts (.pyc) in: ' + directory + '\n')

    [os.remove(script) for script in compiled_scripts]
