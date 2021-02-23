#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import re
import sys
import json
import inspect
import operator
import platform
import sysconfig
import functools
import subprocess
import webbrowser
import piper_config as pcfg


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
    matched = []

    for directory, _, files in os.walk(starting_directory):
        [matched.append(os.path.join(directory, fn).replace('\\', '/')) for fn in files if fn.lower().endswith(word)]

    return matched


def removeSuffixes(word, suffixes):
    """
    Attempts to remove th given suffixes from the given word.

    Args:
        word (string): Word to remove suffixes from.

        suffixes (collections.iterable): Suffixes to remove from given word.

    Returns:
        (string): Word with suffixes removed.
    """
    for suffix in suffixes:
        word = word.rstrip(suffix)

    return word


def swapText(text, first=pcfg.left_suffix, second=pcfg.right_suffix):
    """
    Swaps the given first and seconds strings with each other in the given text.

    Args:
        text (string): Text to look for given first and second string to swap with each other.

        first (string): Text to swap with the second string.

        second (string): Text to swap with the first string.

    Returns:
        (string): Text with strings swapped if they were found. Else same text as before.
    """
    return re.sub(r'{}|{}'.format(first, second), lambda w: first if w.group() == second else second, text)


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
