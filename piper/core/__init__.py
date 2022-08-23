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
    return pcfg.sides.get(name, '').strip().lower()


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
