#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys

import piper.config as pcfg
import piper.core.util as pcu


def getPath():
    """
    Gets the path to the vendor directory. This is usually piper/vendor/py...

    Returns:
        (string): Incomplete path to vendor directory.
    """
    piper_directory = pcu.getPiperDirectory()
    return os.path.join(piper_directory, 'vendor', 'py')


def getVersionedPath():
    """
    Gets the path to the directory that holds all vendors supported by the current python version.
    Such as piper/vendor/py3

    Returns:
        (string): Complete path to vendor directory for current python version.
    """
    path = getPath()
    return path + '2' if sys.version.startswith('2') else path + '3'


def getVersionLessPath():
    """
    Gets the path to the directory that holds all vendors supported by all python versions.
    Should return the full path of piper/vendor/pyx

    Returns:
        (string): Complete path to vendor directory that supports all python versions.
    """
    return getPath() + 'x'


def getAll():
    """
    Gets all the vendor directories under vendor that are supported by current python version and all apps.

    Returns:
        (list): full path to vendor directories that all apps use.
    """
    versioned_path = getVersionedPath()
    versioned_paths = pcu.listFullDirectory(versioned_path)

    version_less_path = getVersionLessPath()
    version_less_paths = pcu.listFullDirectory(version_less_path)

    return filter(lambda path: os.path.isdir(path), versioned_paths + version_less_paths)


def getMatchingPaths(directory, error=True):
    """
    Gets all the directories that exist in the given directory with names matched by the piper_config and current app.

    Args:
        directory (string): Path to search for directory names.

        error (boolean): Raises ValueError if no valid DCC app found.

    Returns:
        (list): Full path to directories that exist within given directory and are part of the app's piper_config.
    """
    paths = []
    app = pcu.getApp(error=error)
    vendors = set(pcfg.vendors.get(app, []) + pcfg.vendors[pcfg.dcc_agnostic_name])

    for vendor in vendors:
        path = os.path.join(directory, vendor)
        if os.path.exists(path):
            paths.append(path)

    return paths


def getVersionedPaths(error=True):
    """
    Gets all the paths to the vendors that only support the currently used python version in the current app.

    Args:
        error (boolean): Raises ValueError if no valid DCC app found.

    Returns:
        (list): Full path to vendor directories that current python version supports in current app.
    """
    versioned_path = getVersionedPath()
    return getMatchingPaths(versioned_path, error=error)


def getVersionLessPaths(error=True):
    """
    Gets all the paths to the vendors that support all python versions in the current app.

    Args:
        error (boolean): Raises ValueError if no valid DCC app found.

    Returns:
        (list): Full path to vendor directories that support all python versions and supports in current app.
    """
    version_less_path = getVersionLessPath()
    return getMatchingPaths(version_less_path, error=error)


def getPaths(error=True):
    """
    Gets the full paths to the vendor directories that are meant to be loaded in the current app.

    Args:
        error (boolean): Raises ValueError if no valid DCC app found.

    Returns:
        (list): All vendor directories that are supported by current app and python version.
    """
    versioned_paths = getVersionedPaths(error=error)
    version_less_paths = getVersionLessPaths(error=error)
    return versioned_paths + version_less_paths


def addPaths(error=True):
    """
    Adds all the vendor directories that current app and python version support to the sys.path.

    Args:
        error (boolean): Raises ValueError if no valid DCC app found.

    Returns:
        (list): Paths added.
    """
    paths = getPaths(error=error)
    [sys.path.append(path) for path in paths if path not in sys.path]
    return paths
