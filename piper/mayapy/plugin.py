#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm

import piper.core
import piper.config.maya as mcfg
import piper.core.pather as pather


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
    [unload(plugin) for plugin in mcfg.unwanted_plugins]


def loadAll():
    """
    Loads all the plug-ins in the plug-ins directory inside Piper.
    """
    piper_directory = piper.core.getPiperDirectory()
    plugins_directory = os.path.join(piper_directory, 'maya', 'plug-ins', str(pm.about(version=True)))
    extensions = ('.mll', '.py')
    plugins = pather.getAllFilesEndingWithWord(extensions, plugins_directory)
    [load(os.path.basename(plugin)) for plugin in plugins]


def runtimeLoad(plugin):
    """
    Decorator function that attempts to load the given plugin_name.
    Plug-in should not be set to autoload, so use this anytime you need to call a function that uses the plug-in.

    Args:
        plugin (string): Name of plugin to load

    Returns:
        (decorator): Decorator with correct argument. 
    """
    def parametrized(method):
        def wrapper(*args,  **kwargs):
            try:
                # try to load houdini engine plug-in to make sliding pivot curve
                pm.loadPlugin(plugin, qt=True)
            except RuntimeError:
                pm.warning(f'{plugin} not found!')
                return

            method(*args, **kwargs)
        return wrapper
    return parametrized
