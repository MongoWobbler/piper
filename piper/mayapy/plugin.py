#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm
import piper.core.util as pcu


def load(plugin):
    """
    Loads given plugin

    Args:
        plugin (string): plugin to load
    """
    if not pm.pluginInfo(plugin, q=True, loaded=True):
        pm.loadPlugin(plugin, qt=True)
        pm.pluginInfo(plugin, e=True, autoload=True)


def unload(plugin):
    """
    CUnloads given plugin

    Args:
        plugin (string): plugin to unload
    """
    if pm.pluginInfo(plugin, q=True, loaded=True):
        pm.pluginInfo(plugin, e=True, autoload=False)
        pm.unloadPlugin(plugin)


def loadAll(version=True):
    """
    Loads all the plug-ins in the plug-ins directory inside Piper.

    Args:
        version (boolean): If True, will only load plugins with version number extension at the end of file name.
    """
    piper_directory = pcu.getPiperDirectory()
    plugins_directory = os.path.join(piper_directory, 'plug-ins')
    extension = str(pm.about(version=True)) if version else ''
    extension += '.mll'
    plugins = pcu.getAllFilesEndingWithWord(extension, plugins_directory)
    [load(os.path.basename(plugin)) for plugin in plugins]
