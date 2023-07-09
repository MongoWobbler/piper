#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys
import json
import time
import inspect
import operator
import functools
from _weakref import proxy


if sys.version_info > (3, 7):
    from collections.abc import MutableSet
else:
    from collections import MutableSet


operators = {'< ': operator.lt,
             '<=': operator.le,
             '==': operator.eq,
             '!=': operator.ne,
             '>=': operator.ge,
             '> ': operator.gt}


def methodToStringCommand(method):
    """
    Converts the given method to a string command that can execute the given method if passed to exec().

    Args:
        method (method): Method to turn to string command.

    Returns:
        (string): String that imports the method's module and then executes the method.
    """
    module = method.__module__
    full_method = module + '.' + method.__name__
    return f'import {module}; {full_method}()'


def parametrized(decorator):
    """
    A decorator for decorators that allows decorators to have parameters.

    Args:
        decorator (method): Decorator that will allow parameters.

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
    directory = os.path.dirname(file_name)

    # create directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

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

    path = path.lower().replace('\\', '/')
    to_delete = []

    for key, module in sys.modules.items():
        try:
            modules_path = inspect.getfile(module).lower().replace('\\', '/')

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


class Link(object):
    __slots__ = 'prev', 'next', 'key', '__weakref__'


class OrderedSet(MutableSet):
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
