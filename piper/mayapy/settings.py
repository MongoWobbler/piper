#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.plugin as plugin
from piper.mayapy.pipe.store import store


# DX11 required for rendering engine
plugin.load('dx11Shader')


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


def hotkeys():
    """
    Creates hotkeys that make use of piper scripts.
    """
    # make a custom key set since Maya's default is locked.
    if not pm.hotkeySet(pcfg.hotkey_set_name, exists=True):
        pm.hotkeySet(pcfg.hotkey_set_name, source='Maya_Default')

    # set the current hotkey set to be piper's hotkey set
    pm.hotkeySet(pcfg.hotkey_set_name, current=True, edit=True)

    # CLEAR EXISTING HOTKEY(s)
    # if key is being used, clear it so we can assign a new one.
    if pm.hotkeyCheck(key='c', alt=True):
        pm.hotkey(k='c', alt=True, n='', rn='')

    # ASSIGN NEW HOTKEY(s)
    # create command and assign it to a hotkey
    python_command = 'python("import piper.mayapy.util as myu; myu.cycleManipulatorSpace()")'
    command = pm.nameCommand('cycleManipulator', command=python_command, annotation='Cycles Manipulator Space')
    pm.hotkey(keyShortcut='c', alt=True, name=command)

    pm.displayInfo('Assigned Piper Hotkeys')


def startup():
    """
    To called when Maya starts up.
    """
    if store.get(pcfg.use_piper_units):
        loadDefaults()

    if store.get(pcfg.unload_unwanted):
        plugin.unloadUnwanted()

    setStartupProject()
    loadRender()
