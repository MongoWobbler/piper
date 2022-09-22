#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys
import getpass
import webbrowser

import piper.config as pcfg
import piper.core.dcc as dcc


def getPiperDirectory():
    """
    Convenience method for getting the piper directory.

    Returns:
        (string): Path to piper directory.
    """
    return os.environ['PIPER_DIR']


def getTempDirectory(create=True):
    """
    Gets a temp directory. User/dev is responsible for cleaning up this directory!

    Args:
        create (boolean): If True, creates the directory if it does not already exist.

    Returns:
        (string): Full path to temp directory.
    """
    directory = os.path.join(getPiperDirectory(), 'temp').replace('\\', '/')

    if not os.path.exists(directory) and create:
        os.makedirs(directory)

    return directory


def deleteTempDirectory():
    """
    Deletes the temp directory associated with getPiperTempDirectory.
    """
    directory = getTempDirectory(create=False)

    if os.path.exists(directory) and not os.listdir(directory):
        os.rmdir(directory)


def setPiperDirectory():
    """
    Sets the directory for the environment key "PIPER_DIR".

    Returns:
        (string): Path to piper directory.
    """
    is_frozen = getattr(sys, 'frozen', False)
    piper_directory = os.path.dirname(sys.executable) if is_frozen else os.path.abspath(__file__ + '/../../..')
    piper_directory = piper_directory.replace('\\', '/')
    os.environ['PIPER_DIR'] = piper_directory
    return piper_directory


def getSide(name):
    """
    Gets the full name of the side associated with the given name suffix.

    Args:
        name (string): Name to get side of from suffix.

    Returns:
        (string): Full name of side.
    """
    name = name.lower()
    if name.endswith(pcfg.left_suffix):
        return pcfg.left_name.strip().lower()
    elif name.endswith(pcfg.right_suffix):
        return pcfg.right_name.strip().lower()
    else:
        return ''


def openDocumentation():
    """
    Opens the documentation for piper in the default web browser.
    """
    webbrowser.open(pcfg.documentation_link, new=2)


def getWelcomeMessage():
    """
    Convenience method for welcoming user to piper.
    """
    return getpass.getuser() + '\'s Piper is ready to use with ' + dcc.get()
