#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import sys
import json
import inspect
import operator
import platform
import sysconfig
import functools
import subprocess
import webbrowser


def getCurrentPath():
    """
    Gets the path to the file that is calling the function.
    Takes into account whether it is being called by an executable or python script.

    Returns:
        (string): Path to file calling the getCurrentPath function.
    """
    return sys.executable if getattr(sys, 'frozen', False) else __file__.replace('\\', '/')


def getPiperDirectory():
    """
    Convenience method for getting the piper directory.

    Returns:
        (string): Path to piper directory.
    """
    return os.environ['PIPER_DIR']


def validateDirectory(directory):
    """
    Creates the given directory if it does not already exist.

    Args:
        directory (string): Directory to create.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def getApp():
    """
    Gets the application that is running the current python script.

    Returns:
        (string): Maya or Houdini.
    """
    path = sysconfig.get_path('scripts')

    if 'Maya' in path:
        return 'Maya'
    elif 'HOUDIN' in path:
        return 'Houdini'
    elif 'UnrealEnginePython' in path:
        return 'UE4'
    else:
        raise ValueError('Current compatible software is Maya or Houdini')


def openWithOS(path):
    """
    Opens the given path with the OS. Useful for opening windows in Explorer or such.

    Args:
        path (string): Path to open.
    """
    path = os.path.normpath(path)
    subprocess.call('explorer "{0}"'.format(path))


def writeJson(file_name, data):
    """
    Writes given dict data to given file_name as json.

    Args:
        file_name (string): Path to write data to.

        data (dict): dict to write to given file_name.

    Returns:
        (string): full path where json file is.
    """
    # create directory if it does not exist
    directory_name = os.path.dirname(file_name)
    validateDirectory(directory_name)

    with open(file_name, 'w') as open_file:
        json.dump(data, open_file, indent=4)

    return file_name


def readJson(file_name, hook=None):
    """
    Gets the dictionary data from the given json file.

    Args:
        file_name (string): Path to json file.

        hook (orderedDict): if orderedDict is passed, json loads dict in order.

    Returns:
        (dict): Data loaded from given file_name.
    """
    with open(file_name, 'r') as open_file:
        data = json.load(open_file, object_pairs_hook=hook)

    return data


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


def flatten(laundry):
    """
    Flattens a list

    Args:
        laundry (list): list to flatten

    Returns:
        (list): Flattened list.
    """
    return functools.reduce(operator.iconcat, laundry, [])


def getMedian(laundry):
    """
    Gets the median item in the given list.

    Args:
        laundry (list): Items to get middle item from.

    Returns:
        (Any): The median item in the list.
    """
    length = len(laundry)

    if length == 0:
        return None

    median_index = (length - 1) / 2
    return laundry[median_index]


def copyToClipboard(text):
    """
    Copies the given text to the clipboard

    Args:
        text (string): Text to copy to clipboard.
    """
    operating_system = platform.system()
    command = 'echo ' + text.strip()

    if operating_system == 'Darwin':  # macOS
        command += '|pbcopy'
    else:
        command += '|clip'  # Windows

    return subprocess.check_call(command, shell=True)


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


def removeModules(path=None, exclude_path=None, print_debug=True):
    """
    Thanks to Nicholas Rodgers for the script.
    https://medium.com/@nicholasRodgers/sidestepping-pythons-reload-function-without-restarting-maya-2448bab9476e
    Removes all the modules under given path that are currently loaded in memory.

    Args:
        path (string): Path to remove loaded modules under.

        exclude_path (string): Name of path to NOT remove.

        print_debug (boolean): If true, will print all the modules that were removed.
    """
    import sys

    if path is None:
        path = os.path.dirname(__file__)

    path = path.lower()
    to_delete = []

    for key, module in sys.modules.items():
        try:
            modules_path = inspect.getfile(module).lower()

            if exclude_path:
                if not modules_path.startswith(exclude_path.lower()) and modules_path.startswith(path):

                    if print_debug:
                        print("Removing: %s" % key)

                    to_delete.append(key)
            else:
                if modules_path.startswith(path):

                    if print_debug:
                        print("Removing: %s" % key)

                    to_delete.append(key)
        except TypeError:
            pass

    import sys  # have to reimport sys here in case we delete self
    for module in to_delete:
        del (sys.modules[module])


def openDocumentation():
    """
    Opens the documentation for piper in the default web browser.
    """
    webbrowser.open('https://github.com/MongoWobbler/piper', new=2)


def welcome():
    """
    Convenience method for welcoming user to piper.
    """
    print(os.environ['USER'] + '\'s Piper is ready to use with ' + getApp()),
    print('\n')
