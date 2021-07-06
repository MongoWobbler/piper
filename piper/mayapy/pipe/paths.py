#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm
import piper_config as pcfg
import piper.core.util as pcu
from piper.mayapy.pipe.store import store


def getRelativeArt(path='', name=''):
    """
    Gets the relative art path of given path. If path not given will use current scene path.

    Args:
        path (string): Path to get relative art directory of.

        name (string): If given, will change the name of the file to the given name.

    Returns:
        (string): Path relative to art directory set through settings.
    """
    if not path:
        path = pm.sceneName()

    if not path:
        pm.error('Scene is not saved! ')

    art_directory = store.get(pcfg.art_directory)
    if not path.startswith(art_directory):
        pm.error(path + ' is not in the art directory: ' + art_directory)

    if name:
        directory = os.path.dirname(path)
        old_name, extension = os.path.splitext(os.path.basename(path))
        path = os.path.join(directory, name + extension)

    return path.lstrip(art_directory)


def getSelfExport(name=''):
    """
    Gets the current scene's directory if scene is saved, else uses the art directory.

    Args:
        name (string): Name of file to return.

    Returns:
        (string): Full path with given name.
    """
    scene_path = pm.sceneName()
    if scene_path:
        export_directory = os.path.dirname(scene_path)
    else:
        art_directory = store.get(pcfg.art_directory)
        if not art_directory:
            pm.error('Please save the scene or set the Art Directory before exporting to self.')

        export_directory = art_directory

    export_path = os.path.join(export_directory, name).replace('\\', '/')
    return export_path


def getGameExport(name=''):
    """
    Gets the game path for the given scene. If no scene open, will use game root directory.

    Args:
        name (string): Name of file to return.

    Returns:
        (string): Full path with given name.
    """
    scene_path = pm.sceneName()
    game_directory = store.get(pcfg.game_directory)
    relative_directory = ''

    if not game_directory:
        pm.error('Game directory is not set. Please use "Piper>Export>Set Game Directory" to set export directory.')

    if scene_path:
        source_directory = os.path.dirname(scene_path)
        art_directory = store.get(pcfg.art_directory)

        # gets the relative path using the art directory
        if scene_path.startswith(art_directory):
            relative_directory = source_directory.lstrip(art_directory)
        else:
            pm.warning(scene_path + ' is not in art directory! Returning game directory root.')

    export_path = os.path.join(game_directory, relative_directory, name).replace('\\', '/')
    return export_path


def getGameTextureExport(texture):
    """
    Gets the path to export the given texture to.

    Args:
        texture (string): Full art directory path of texture file.

    Returns:
        (string): Full game directory path of where given texture would export to.
    """
    relative_directory = ''
    art_directory = store.get(pcfg.art_directory)
    game_directory = store.get(pcfg.game_directory)

    if texture.startswith(art_directory):
        relative_directory = texture.lstrip(art_directory)
    else:
        pm.warning(texture + ' is not in art directory! Returning game directory root.')

    export_path = os.path.join(game_directory, relative_directory).replace('\\', '/')
    export_path = export_path.replace(pcfg.art_textures_directory_name, pcfg.game_textures_directory_name)
    return export_path


def getRigPath(path):
    """
    Gets the rig associated with the given path. Could return None if no rig found.

    Args:
        path (string): Starting path to search for rig. Could be directory or full file path.

    Returns:
        (string): Path to rig associated with given path.
    """
    directory = path if os.path.isdir(path) else os.path.dirname(path)
    rigs = pcu.getAllFilesEndingWithWord(pcfg.maya_rig_suffixes, directory)
    return rigs[0] if rigs else None
