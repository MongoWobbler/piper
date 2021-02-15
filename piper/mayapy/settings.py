#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
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
    art_directory = store.get(pcfg.art_directory)

    if art_directory:
        setProject(art_directory)


def loadDefaults():
    """
    Loads the settings to use in Maya
    """
    # change grid, time, units, and playback options
    pm.currentUnit(time=pcfg.maya_default_time)
    pm.grid(size=1200, spacing=500, divisions=5)
    pm.playbackOptions(min=0, max=30)
    pm.currentTime(0)
    pm.currentUnit(linear=pcfg.maya_default_length)


def loadRender():
    """
    Sets the viewport's render engine to DirectX11 and the tone map to use Stingray
    """
    pm.mel.eval('setRenderingEngineInModelPanel "{}";'.format(pcfg.maya_default_rendering_api))
    pm.colorManagementPrefs(e=True, vtn=pcfg.maya_default_tone_map)
    pm.modelEditor('modelPanel4', e=True, vtn=pcfg.maya_default_tone_map)


def startup():
    """
    To called when Maya starts up.
    """
    if store.get(pcfg.use_piper_units):
        loadDefaults()

    setStartupProject()
    loadRender()
