#  Copyright (c) Christian Corsica. All Rights Reserved.

import maya.OpenMaya as om
import pymel.core as pm

import piper.config as pcfg
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
from piper.core.store import piper_store
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
    [om.MEventMessage.removeCallback(callback) for callback in callbacks]
    callbacks = []


def setProject(directory):
    """
    Sets the maya project. Will create a directory if one does not already exist.

    Args:
        directory (string): path where project will be set to.
    """
    pather.validateDirectory(directory)
    pm.workspace(directory, o=True)
    pm.workspace(fr=['scene', directory])


def setStartupProject():
    """
    Sets the art directory project
    """
    art_directory = piper_store.get(pcfg.art_directory)

    if art_directory:
        setProject(art_directory)


def loadDefaults():
    """
    Loads the settings to use in Maya
    """
    # change grid, time, units, and playback options
    pm.currentUnit(time=mcfg.default_time)
    pm.grid(size=1200, spacing=500, divisions=5)
    pm.playbackOptions(min=0, max=30)
    pm.currentTime(0)
    pm.currentUnit(linear=mcfg.default_length)


def loadRender():
    """
    Sets the viewport's render engine to DirectX11 and the tone map to use Stingray
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


def onSceneOpened(*args):
    """
    Called AFTER a scene is opened and all references have been loaded, usually through a callback registed on startup.
    """
    # reloading references breaks references during headless mode, so don't.
    if not pm.about(batch=True):
        pm.evalDeferred(pipernode.reloadRigReferences, lp=True)


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
    if piper_store.get(pcfg.use_perforce) and piper_store.get(pcfg.p4_add_after_save):
        perforce.makeAvailable()


def registerCallbacks():
    """
    Registers all the callbacks to the global callbacks list.
    """
    global callbacks

    callback = om.MEventMessage.addEventCallback('NewSceneOpened', onNewSceneOpened)
    callbacks.append(callback)

    callback = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, onSceneOpened)
    callbacks.append(callback)

    callback = om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeSave, onBeforeSave)
    callbacks.append(callback)

    callback = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterSave, onAfterSave)
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

    setStartupProject()
    registerCallbacks()

    if has_gui:
        piper.ui.openPrevious()
