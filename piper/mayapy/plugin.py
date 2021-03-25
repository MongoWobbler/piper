#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm
import piper_config as pcfg
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
    Unloads given plugin

    Args:
        plugin (string): plugin to unload
    """
    if pm.pluginInfo(plugin, q=True, loaded=True):
        pm.pluginInfo(plugin, e=True, autoload=False)

        try:
            pm.unloadPlugin(plugin)
        except RuntimeError:
            pm.warning(plugin + ' could not be unloaded!')


def unloadUnwanted():
    """
    Unloads all the unwanted Maya plugins defined in piper config.
    """
    [unload(plugin) for plugin in pcfg.maya_unwanted_plugins]


def loadAll():
    """
    Loads all the plug-ins in the plug-ins directory inside Piper.
    """
    piper_directory = pcu.getPiperDirectory()
    plugins_directory = os.path.join(piper_directory, 'maya', 'plug-ins', str(pm.about(version=True)))
    extensions = ('.mll', '.py')
    plugins = pcu.getAllFilesEndingWithWord(extensions, plugins_directory)
    [load(os.path.basename(plugin)) for plugin in plugins]


def loadHoudiniEngine(method):
    """
    Decorator function that attempts to load the houdini engine.
    Houdini plug-in should not be auto-loaded, so use this anytime you need to call a function that use the plug-in.

    Args:
        method (method): Function to call after plugin has loaded.

    Returns:
        (method): Wrapper method.
    """
    def wrapper(*args,  **kwargs):
        try:
            # try to load houdini engine plug-in to make sliding pivot curve
            pm.loadPlugin('houdiniEngine', qt=True)
        except RuntimeError:
            pm.warning('Houdini Engine not found!')
            return

        return method(*args, **kwargs)

    return wrapper
