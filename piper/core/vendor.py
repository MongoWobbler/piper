#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys
import sysconfig
from distutils.version import LooseVersion

import piper.core
import piper.config as pcfg
import piper.core.dcc as dcc
import piper.core.pather as pather


def getPath():
    """
    Gets the path to the vendor directory. This is usually piper/vendor/py...

    Returns:
        (string): Incomplete path to vendor directory.
    """
    piper_directory = piper.core.getPiperDirectory()
    return os.path.join(piper_directory, 'vendor', 'py')


def getVersionedPath():
    """
    Gets the path to the directory that holds all vendors supported by the current python version.
    Such as piper/vendor/py3

    Returns:
        (string): Complete path to vendor directory for current python version.
    """
    path = getPath()
    return path + sysconfig.get_python_version().replace('.', '')


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
    versioned_paths = pather.listFullDirectory(versioned_path)

    version_less_path = getVersionLessPath()
    version_less_paths = pather.listFullDirectory(version_less_path)

    return filter(lambda path: os.path.isdir(path), versioned_paths + version_less_paths)


def isValid(vendor, dcc_version=None):
    """
    Whether the given vendor data is valid based on the given dcc_version. Min/Max values are inclusive.

    Args:
        vendor (dictionary): Data including min, and max string keys with int as values to compare against version.

        dcc_version (string): DCC version number to compare against given vendor data.

    Returns:
        (boolean): True if given dcc version is within the min/max range of the given vendor data.
    """
    if dcc_version is None:
        return True

    dcc_version = LooseVersion(dcc_version)
    minimum = vendor.get('min')
    maximum = vendor.get('max')
    min_result = minimum and dcc_version < LooseVersion(minimum)
    max_result = maximum and dcc_version > LooseVersion(maximum)
    return not (min_result or max_result)


def getMatchingPaths(directory, error=True, dcc_version=None):
    """
    Gets all the directories that exist in the given directory with names matched by the piper_config and current app.

    Args:
        directory (string): Path to search for directory names.

        error (boolean): Raises ValueError if no valid DCC app found.

        dcc_version (string): DCC version number to compare against valid vendors based on piper config.

    Returns:
        (list): Full path to directories that exist within given directory and are part of the app's piper_config.
    """
    paths = []
    app = dcc.get(error=error)
    vendor_data = pcfg.vendors.get(app, []) + pcfg.vendors.get(pcfg.dcc_agnostic_name, [])

    if not vendor_data:
        return []

    vendors = {vendor['name'] for vendor in vendor_data if isValid(vendor, dcc_version)}

    for vendor in vendors:
        path = os.path.normpath(os.path.join(directory, vendor))
        if os.path.exists(path):
            paths.append(path)

    return paths


def getVersionedPaths(error=True, dcc_version=None):
    """
    Gets all the paths to the vendors that only support the currently used python version in the current app.

    Args:
        error (boolean): Raises ValueError if no valid DCC app found.

        dcc_version (string): DCC version number to compare against valid vendors based on piper config.

    Returns:
        (list): Full path to vendor directories that current python version supports in current app.
    """
    versioned_path = getVersionedPath()
    return getMatchingPaths(versioned_path, error=error, dcc_version=dcc_version)


def getVersionLessPaths(error=True, dcc_version=None):
    """
    Gets all the paths to the vendors that support all python versions in the current app.

    Args:
        error (boolean): Raises ValueError if no valid DCC app found.

        dcc_version (string): DCC version number to compare against valid vendors based on piper config.

    Returns:
        (list): Full path to vendor directories that support all python versions and supports in current app.
    """
    version_less_path = getVersionLessPath()
    return getMatchingPaths(version_less_path, error=error, dcc_version=dcc_version)


def getPaths(error=True, dcc_version=None):
    """
    Gets the full paths to the vendor directories that are meant to be loaded in the current app.

    Args:
        error (boolean): Raises ValueError if no valid DCC app found.

        dcc_version (string): DCC version number to compare against valid vendors based on piper config.

    Returns:
        (list): All vendor directories that are supported by current app and python version.
    """
    versioned_paths = getVersionedPaths(error=error, dcc_version=dcc_version)
    version_less_paths = getVersionLessPaths(error=error, dcc_version=dcc_version)
    return versioned_paths + version_less_paths


def addPaths(error=True, dcc_version=None):
    """
    Adds all the vendor directories that current app and python version support to the sys.path.

    Args:
        error (boolean): Raises ValueError if no valid DCC app found.

        dcc_version (string): DCC version number to compare against valid vendors based on piper config.

    Returns:
        (list): Paths added.
    """
    paths = getPaths(error=error, dcc_version=dcc_version)
    [sys.path.append(path) for path in paths if path not in sys.path]
    return paths
