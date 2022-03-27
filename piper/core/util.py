#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import re
import sys
import json
import time
import getpass
import inspect
import operator
import platform
import sysconfig
import functools
import subprocess
import webbrowser
import collections
from weakref import proxy
import piper_config as pcfg


operators = {'< ': operator.lt,
             '<=': operator.le,
             '==': operator.eq,
             '!=': operator.ne,
             '>=': operator.ge,
             '> ': operator.gt}


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


def listFullDirectory(directory):
    """
    Convenience method for getting the full path from listing a directory.

    Args:
        directory (string): Directory to list paths from.

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


def getSide(name):
    """
    Gets the full name of the side associated with the given name suffix.

    Args:
        name (string): Name to get side of from suffix.

    Returns:
        (string): Full name of side.
    """
    if name.endswith(pcfg.left_suffix):
        return 'left'
    elif name.endswith(pcfg.right_suffix):
        return 'right'
    else:
        return ''


def getApp():
    """
    Gets the application that is running the current python script.

    Returns:
        (string): Maya, Houdini, UnrealEngine, or 3dsMax.
    """
    path = sysconfig.get_path('scripts')

    if 'Maya' in path:
        return pcfg.maya_name
    elif 'HOUDIN' in path:
        return pcfg.houdini_name
    elif 'UnrealEnginePython' in path:
        return pcfg.unreal_name
    elif '3ds' in path and 'Max' in path:
        return pcfg.max_3ds_name
    else:
        raise ValueError('No compatible software found in ' + path + '. Please see piper_config for compatible DCCs.')


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
    os.startfile(path)


def parametrized(decorator):
    """
    A decorator for decorators that allows decorators to have parameters.

    Args:
        decorator (method): Decorator that will allows parameters.

    Returns:
        (method): Decorator parametrized.

    Examples:
        @parametrized
        def multiply(method, n=2):
            def wrapper(*args, **kwargs):
                return n * method(*args, **kwargs)
            return wrapper

        @multiply(n=3)
        def function(a):
            return 10 + a

        print(function(3))  #  multiply method takes kwarg of 3, so (10 + 3) * 3 = 39
        >>> 39
    """
    def layer(*args, **kwargs):
        def replicated(method):
            return decorator(method, *args, **kwargs)
        return replicated
    return layer


def measureTime(method):
    """
    Decorator for measuring how long the given function took to execute.
    Credit to: https://thenextweb.com/news/decorators-in-python-make-code-better-syndication

    Args:
        method (function): Function to measure time to execute.
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = method(*args, **kwargs)
        end_time = time.perf_counter()
        print(method.__name__ + ' took ' + str(round((end_time - start_time), 3)) + ' seconds.')
        return result

    return wrapper


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
        [matched.append(os.path.join(directory, fn).replace('\\', '/')) for fn in files if fn.endswith(word)]

    return matched


def removePrefixes(word, prefixes):
    """
    Attempts to remove the given prefixes from the given word.

    Args:
        word (string): Word to remove prefixes from.

        prefixes (collections.Iterable or string): Prefixes to remove from given word.

    Returns:
        (string): Word with prefixes removed.
    """
    if isinstance(prefixes, str):
        return word.split(prefixes)[-1]

    for prefix in prefixes:
        word = word.split(prefix)[-1]

    return word


def removeSuffixes(word, suffixes):
    """
    Attempts to remove the given suffixes from the given word.

    Args:
        word (string): Word to remove suffixes from.

        suffixes (collections.Iterable or string): Suffixes to remove from given word.

    Returns:
        (string): Word with suffixes removed.
    """
    if isinstance(suffixes, str):
        return word.split(suffixes)[0]

    for suffix in suffixes:
        word = word.split(suffix)[0]

    return word


def toSentenceCase(text):
    """
    Converts the given text to sentence case.

    Args:
        text (string): Text to convert to sentence case.

    Returns:
        (string): Sentence case version of given text.
    """
    return re.sub(r"(?<=\w)([A-Z])", r" \1", text).title()


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
    return re.sub(r'{a}|{b}'.format(a=first, b=second), lambda w: first if w.group() == second else second, text)


def flatten(laundry):
    """
    Flattens a list

    Args:
        laundry (iterable): list to flatten

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

    median_index = int((length - 1) / 2)
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
    webbrowser.open(pcfg.documentation_link, new=2)


def getWelcomeMessage():
    """
    Convenience method for welcoming user to piper.
    """
    return getpass.getuser() + '\'s Piper is ready to use with ' + getApp()


class Link(object):
    __slots__ = 'prev', 'next', 'key', '__weakref__'


class OrderedSet(collections.MutableSet):
    # Set the remembers the order elements were added
    #
    # Thanks to: https://github.com/ActiveState/code/blob/3b27230f418b714bc9a0f897cb8ea189c3515e99/recipes/Python
    # /576696_OrderedSet_with_Weakrefs/recipe-576696.py
    #
    # Big-O running times for all methods are the same as for regular sets.
    # The internal self.__map dictionary maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # The prev/next links are weakref proxies (to prevent circular references).
    # Individual links are kept alive by the hard reference in self.__map.
    # Those hard references disappear when a key is deleted from an OrderedSet.

    def __init__(self, iterable=None):
        self.__root = root = Link()         # sentinel node for doubly linked list
        root.prev = root.next = root
        self.__map = {}                     # key --> link
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.__map)

    def __contains__(self, key):
        return key in self.__map

    def add(self, key):
        # Store new key in a new link at the end of the linked list
        if key not in self.__map:
            self.__map[key] = link = Link()
            root = self.__root
            last = root.prev
            link.prev, link.next, link.key = last, root, key
            last.next = root.prev = proxy(link)

    def update(self, iterable):
        [self.add(key) for key in iterable]

    def discard(self, key):
        # Remove an existing item using self.__map to find the link which is
        # then removed by updating the links in the predecessor and successors.
        if key in self.__map:
            link = self.__map.pop(key)
            link.prev.next = link.next
            link.next.prev = link.prev

    def __iter__(self):
        # Traverse the linked list in order.
        root = self.__root
        curr = root.next
        while curr is not root:
            yield curr.key
            curr = curr.next

    def __reversed__(self):
        # Traverse the linked list in reverse order.
        root = self.__root
        curr = root.prev
        while curr is not root:
            yield curr.key
            curr = curr.prev

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = next(reversed(self)) if last else next(iter(self))
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return not self.isdisjoint(other)
