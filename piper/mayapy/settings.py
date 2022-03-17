#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import maya.OpenMaya as om
import pymel.core as pm
import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.util as myu
import piper.mayapy.plugin as plugin
import piper.mayapy.pipernode as pipernode
from piper.mayapy.pipe.store import store


# DX11 required for rendering engine
plugin.load('dx11Shader')
callbacks = []


def welcome():
    """
    Displays the welcome message.
    """
    message = pcu.getWelcomeMessage()
    pm.displayInfo(message)


def removeCallbacks():
    """
    Deletes/removes all callbacks that piper has registered.
    """
    global callbacks
    [om.MEventMessage.removeCallback(callback) for callback in callbacks]
    callbacks = []


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
    tone_maps = pm.colorManagementPrefs(q=True, vts=True)

    if pcfg.maya_default_tone_map not in tone_maps:
        return

    pm.colorManagementPrefs(e=True, vtn=pcfg.maya_default_tone_map)
    pm.modelEditor('modelPanel4', e=True, vtn=pcfg.maya_default_tone_map)


@myu.saveSelection
def reloadPiperReferences():
    """
    Used to reload any sub-references of a Piper Rig reference that is not part of the BIND namespace.
    Mostly used for a 2022 bug where a few piper rigs don't finish loading their references correctly.
    """
    rigs = pipernode.get('piperRig')

    for rig in rigs:
        namespace = rig.namespace()

        if not namespace:
            continue

        ref = pm.FileReference(namespace=namespace)
        [sub_ref.load() for namespace, sub_ref in ref.subReferences().items() if pcfg.bind_namespace not in namespace]


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


def onNewSceneOpened(*args):
    """
    Called when a new scene is opened, usually through a callback registed on startup.
    """
    if store.get(pcfg.use_piper_units):
        loadDefaults()

    if store.get(pcfg.use_piper_render):
        loadRender()


def onSceneOpened(*args):
    """
    Called AFTER a scene is opened and all references have been loaded, usually through a callback registed on startup.
    """
    pm.evalDeferred(reloadPiperReferences, lp=True)


def startup():
    """
    To be called when Maya starts up.
    """
    global callbacks

    if store.get(pcfg.use_piper_units):
        loadDefaults()

    if store.get(pcfg.unload_unwanted):
        plugin.unloadUnwanted()

    if store.get(pcfg.use_piper_render):
        loadRender()

    setStartupProject()

    callback = om.MEventMessage.addEventCallback('NewSceneOpened', onNewSceneOpened)
    callbacks.append(callback)

    callback = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, onSceneOpened)
    callbacks.append(callback)
