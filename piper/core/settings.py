#  Copyright (c) Christian Corsica. All Rights Reserved.

import piper.config as pcfg
import piper.core
import piper.core.filer as filer
import piper.core.pather as pather
from piper.core.store import piper_store


def setArtDirectory():
    """
    Sets the art source directory in the global piper settings

    Returns:
        (string): Art directory that was set.
    """
    starting_directory = piper_store.get(pcfg.art_directory)
    directory = pather.getDirectoryDialog(starting_directory, 'Choose directory to export from', error=False)

    if not directory:
        return

    piper_store.set(pcfg.art_directory, directory)
    return directory


def setGameDirectory():
    """
    Sets the game export directory in the global piper settings

    Returns:
        (string): Game directory that was set.
    """
    starting_directory = piper_store.get(pcfg.game_directory)
    directory = pather.getDirectoryDialog(starting_directory, 'Choose directory to export to', error=False)

    if not directory:
        return

    piper_store.set(pcfg.game_directory, directory)
    return directory


def openArtDirectoryInOS():
    """
    Opens the art directory in OS window.
    """
    filer.openWithOS(piper_store.get(pcfg.art_directory))


def openGameDirectoryInOS():
    """
    Opens the game directory in OS window.
    """
    filer.openWithOS(piper_store.get(pcfg.game_directory))


def openPiperDirectoryInOS():
    """
    Opens the piper toolset directory currently being used in OS window.
    """
    piper_directory = piper.core.getPiperDirectory()
    filer.openWithOS(piper_directory)
