#  Copyright (c) Christian Corsica. All Rights Reserved.

import maya.api.OpenMaya as om2
import pymel.core as pm

import piper.config.maya as mcfg

import piper.ui
import piper.core
import piper.core.filer as filer
import piper.core.pather as pather

import piper.mayapy.plugin as plugin
import piper.mayapy.convert as convert
import piper.mayapy.manipulator as manipulator
import piper.mayapy.pipernode as pipernode
import piper.mayapy.pipe.perforce as perforce
import piper.mayapy.ui.window as window
from piper.mayapy.pipe.paths import maya_paths
from piper.mayapy.pipe.store import maya_store


callbacks = []


def welcome():
    """
    Displays the welcome message.
    """
    message = piper.core.getWelcomeMessage()
    pm.displayInfo(message)


def removeCallbacks():
    """
    Deletes/removes all callbacks that piper has registered.
    """
    global callbacks

    om2.MMessage.removeCallbacks(callbacks)
    callbacks.clear()
    callbacks = []


def setWorkspace(directory):
    """
    Sets the maya workspace. Will create a directory if one does not already exist.

    Args:
        directory (string): path where project will be set to.
    """
    pather.validateDirectory(directory)
    pm.workspace(directory, o=True)
    pm.workspace(fr=['scene', directory])


def setStartupWorkspace():
    """
    Uses the current project's art directory to set up the workspace.
    """
    art_directory = maya_paths.getArtDirectory()

    if art_directory:
        setWorkspace(art_directory)


def loadDefaults(force=False):
    """
    Loads the settings to use in Maya

    Args:
        force (boolean): If True, will set the timeline/playback range regardless of scene existing or not.
    """
    # change grid, time, units, and playback options
    pm.currentUnit(time=mcfg.default_time)
    pm.grid(size=1200, spacing=500, divisions=5)

    # it's annoying when you have a scene and you reload and the timeline changes, so don't if scene exists.
    scene_name = pm.sceneName()
    if not scene_name or force:
        pm.playbackOptions(min=0, max=30)

    pm.currentTime(0)
    pm.currentUnit(linear=mcfg.default_length)


def loadRender():
    """
    Sets the viewport's render engine to DirectX11 and the tone map to use the tonemapping set in Piper's Maya config.
    """
    # DX11 required for rendering engine
    plugin.load('dx11Shader')
    pm.mel.eval('setRenderingEngineInModelPanel "{}";'.format(mcfg.default_rendering_api))
    tone_maps = pm.colorManagementPrefs(q=True, vts=True)

    if mcfg.default_tone_map not in tone_maps:
        return

    pm.colorManagementPrefs(e=True, vtn=mcfg.default_tone_map)
    pm.modelEditor('modelPanel4', e=True, vtn=mcfg.default_tone_map)


def hotkeys():
    """
    Creates hotkeys that make use of piper scripts.
    """
    # make a custom key set since Maya's default is locked.
    if not pm.hotkeySet(mcfg.hotkey_set_name, exists=True):
        pm.hotkeySet(mcfg.hotkey_set_name, source='Maya_Default')

    # set the current hotkey set to be piper's hotkey set
    pm.hotkeySet(mcfg.hotkey_set_name, current=True, edit=True)

    # CLEAR EXISTING HOTKEY(s)
    # if key is being used, clear it so we can assign a new one.
    if pm.hotkeyCheck(key='c', alt=True):
        pm.hotkey(k='c', alt=True, n='', rn='')

    # ASSIGN NEW HOTKEY(s)
    # create command and assign it to a hotkey
    python_command = convert.toPythonCommand(manipulator.cycleManipulatorSpace)
    command = pm.nameCommand('cycleManipulator', command=python_command, annotation='Cycles Manipulator Space')
    pm.hotkey(keyShortcut='c', alt=True, name=command)

    pm.displayInfo('Assigned Piper Hotkeys')


def onNewSceneOpened(*args):
    """
    Called when a new scene is opened, usually through a callback registed on startup.
    """
    if maya_store.get(mcfg.use_piper_units):
        loadDefaults()

    if maya_store.get(mcfg.use_piper_render):
        loadRender()


def onBeforeOpen(*args):
    """
    Called BEFORE a scene is opened.

    Returns:
        (boolean): If True, load the scene. Else scene will not be loaded.
    """
    if pm.about(batch=True):
        return True

    if not maya_store.get(mcfg.use_perforce):
        return True

    file_object = args[0]
    path = file_object.resolvedFullName()

    # if path doesn't exist (which would be rare), then we won't be able to find it in p4
    if not path:
        return True

    p4 = perforce.PerforceMaya()
    with p4.connect():
        is_latest = p4.isLatest(path=path)

    if is_latest:
        return True

    answer = window.beforeOpen()
    if answer != 'Get Latest':
        return True

    with p4.connect():
        p4.getLatest(path=path)

    return True


def onSceneOpened(*args):
    """
    Called AFTER a scene is opened and all references have been loaded, usually through a callback registed on startup.
    """
    # reloading references breaks references during headless mode, so don't.
    if pm.about(batch=True):
        return

    pm.evalDeferred(pipernode.reloadRigReferences, lp=True)

    if not maya_store.get(mcfg.use_perforce):
        return

    is_checked_out_by_other = False
    p4 = perforce.PerforceMaya()
    with p4.connect():
        result = p4.isCheckedOutByOther()

    if is_checked_out_by_other:
        pm.warning(f'Scene is checked out by {result["other_open"][0]}!')


def onBeforeSave(*args):
    """
    Called before maya saves the scene. Pops up warning if file is not writeable asking to checkout or make writeable.
    """
    answer = window.beforeSave()
    if answer == 'Checkout':
        perforce.makeAvailable()

    elif answer == 'Make Writeable':
        path = pm.sceneName()
        filer.clearReadOnlyFlag(path)


def onAfterSave(*args):
    """
    Called after scene is saved.
    """
    if maya_store.get(mcfg.use_perforce) and maya_store.get(mcfg.p4_add_after_save):
        perforce.makeAvailable()


def registerCallbacks():
    """
    Registers all the callbacks to the global callbacks list.
    """
    global callbacks

    callback = om2.MSceneMessage.addCallback(om2.MSceneMessage.kAfterNew, onNewSceneOpened)
    callbacks.append(callback)

    # must use om2 since addCheckFileCallback only works in om2
    callback = om2.MSceneMessage.addCheckFileCallback(om2.MSceneMessage.kBeforeOpenCheck, onBeforeOpen)
    callbacks.append(callback)

    callback = om2.MSceneMessage.addCallback(om2.MSceneMessage.kAfterOpen, onSceneOpened)
    callbacks.append(callback)

    callback = om2.MSceneMessage.addCallback(om2.MSceneMessage.kBeforeSave, onBeforeSave)
    callbacks.append(callback)

    callback = om2.MSceneMessage.addCallback(om2.MSceneMessage.kAfterSave, onAfterSave)
    callbacks.append(callback)


def openPort():
    """
    Opens a port to listen for commands.
    """
    port = ':' + str(mcfg.port)
    if pm.commandPort(port, query=True):
        return

    pm.commandPort(name=port, sourceType='python')
    pm.displayInfo('Port ' + mcfg.host + port + ' has been opened for Piper.')


def closePort():
    """
    Closes port if is opened.
    """
    port = ':' + str(mcfg.port)
    if not pm.commandPort(port, query=True):
        return

    pm.commandPort(name=port, close=True)
    pm.displayInfo('Port ' + mcfg.host + port + ' has been closed.')

def startup():
    """
    To be called when Maya starts up.
    """
    has_gui = not pm.about(batch=True)

    if maya_store.get(mcfg.use_piper_units):
        loadDefaults()

    if maya_store.get(mcfg.unload_unwanted):
        plugin.unloadUnwanted()

    if has_gui and maya_store.get(mcfg.use_piper_render):
        loadRender()

    # error is raised if port is opened headless
    if has_gui and maya_store.get(mcfg.open_port):
        openPort()

    setStartupWorkspace()
    registerCallbacks()

    if has_gui:
        piper.ui.openPrevious()
