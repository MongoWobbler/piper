#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.core.util as pcu
from piper.mayapy.pipe.store import store


def setProject(directory):
    """
    Sets the maya project. Will create a directory if one does not already exist.

    Args:
        directory (string): path where project will be set to.
    """
    pcu.validateDirectory(directory)
    pm.workspace(directory, o=True)
    pm.workspace(fr=['scene', directory])


def setStartupProject():
    """
    Sets the art directory project
    """
    art_directory = store.get('art_directory')

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


def loadRender():
    """
    Sets the viewport's render engine to DirectX11 and the tone map to use Stingray
    """
    pm.mel.eval('setRenderingEngineInModelPanel "DirectX11";')
    pm.colorManagementPrefs(e=True, vtn='Stingray tone-map')


def startup():
    """
    To called when Maya starts up.
    """
    if store.get('use_piper_units'):
        loadDefaults()

    setStartupProject()
    loadRender()
