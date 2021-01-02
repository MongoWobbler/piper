#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm
import piper.mayapy.pipe.store as store


def setProject(directory):
    """
    Sets the maya project. Will create a directory if one does not already exist.

    Args:
        directory (string): path where project will be set to.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    pm.workspace(directory, o=True)
    pm.workspace(fr=['scene', directory])


def setStartupProject():
    """
    Sets the art directory project
    """
    art_directory = store.enter().get('art_directory')

    if art_directory:
        setProject(art_directory)


def loadDefaults():
    """
    Loads the settings to use in Maya
    """
    # change grid, time, units, and playback options
    pm.currentUnit(time='ntsc')
    pm.grid(size=1200, spacing=500, divisions=5)
    pm.playbackOptions(min=0, max=30)
    pm.currentTime(0)
    pm.currentUnit(linear='cm')


def startup():
    """
    To called when Maya starts up.
    """
    loadDefaults()
    setStartupProject()
