#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import pathlib
import posixpath
import piper.config.unreal as ucfg
import piper.core.pather as pather


def getPluginDirectory(piper_directory):
    """
    Gets the path that holds the Unreal python plug-in.

    Args:
        piper_directory (string): Path to piper's main package folder. Usually same as os.environ['PIPER_DIR'].

    Returns:
        (string): Path to Unreal Piper plug-in directory.
    """
    return posixpath.join(piper_directory, ucfg.plugin_path)


def symlink(piper_directory, path):
    """
    Creates a symlink between the init_unreal.py and setup.py scripts in the piper directory and the Unreal project's
    python directory in the content folder.

    Args:
        piper_directory (string): Path to piper's main package folder. Usually same as os.environ['PIPER_DIR'].

        path (string): Path to unreal project which includes all source code, ending in .uproject.
        Or path to project's Plugins directory, or path to Engine's Plugins/Editor directory.
    """
    if path.endswith('.uproject'):
        path = pathlib.Path(path).resolve()
        path = (path.parents[0] / ucfg.plugins_directory_name).as_posix()

    if ucfg.plugins_directory_name not in path:
        print(f"{ucfg.plugins_directory_name} directory not found in {path}")
        raise ValueError

    pather.validateDirectory(path)
    plugin_directory = getPluginDirectory(piper_directory)
    target_directory = pather.validateSymlink(path, ucfg.plugin_name)

    try:
        os.symlink(plugin_directory, target_directory)
        print(f'Linking {plugin_directory} to {target_directory}')
    except OSError as error:
        print('WARNING: Run piper_installer.exe as administrator to symlink!')
        raise error
