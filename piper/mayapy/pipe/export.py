#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm
import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.plugin as plugin
import piper.mayapy.pipernode as pipernode
from piper.mayapy.pipe.store import store


# FBX plugin needed to export.
plugin.load('fbxmaya')


def fbx(export_path, preset_name):
    """
    Exports selected nodes to the given export path with the given preset_name export settings.

    Args:
        export_path (string): Full path to export .fbx to.

        preset_name (string): Name of preset to load for export options.
    """
    # make export directory if it does not exist already
    export_directory = os.path.dirname(export_path)
    pcu.validateDirectory(export_directory)

    # find export preset path to load our preset settings for exporting.
    piper_directory = pcu.getPiperDirectory()
    preset_path = os.path.join(piper_directory, 'presets', preset_name + '.fbxexportpreset')

    if not os.path.exists(preset_path):
        pm.warning(preset_path + ' does not exist! Exporting with default preset.')
        preset_path = os.path.join(piper_directory, 'presets', 'default.fbxexportpreset')

    if not os.path.exists(preset_path):
        pm.error('Default preset does not exist! Should be found in: ' + preset_path)

    preset_path = preset_path.replace('\\', '/')
    pm.mel.eval('FBXLoadExportPresetFile -f "{}"'.format(preset_path))
    pm.mel.eval('FBXExportFileVersion -v FBX201800')
    pm.mel.eval('FBXExportInAscii -v true')
    pm.mel.eval('FBXExport -f "{}" -s'.format(export_path))

    print('\nExported ' + export_path),


def fbxToSelf(name, preset):
    """
    Exports .fbx of selected nodes to the folder that the current scene is in.
    If file is not saved, will export to root of art directory.

    Args:
        name (string): Name of .fbx file.

        preset (string): Preset to load for export options.
    """
    scene_path = pm.sceneName()
    if scene_path:
        export_directory = os.path.dirname(scene_path)
    else:
        art_directory = store.get('art_directory')
        if not art_directory:
            pm.error('Please save the scene or set the Art Directory before exporting to self.')

        export_directory = art_directory

    export_path = os.path.join(export_directory, name + '.fbx').replace('\\', '/')
    fbx(export_path, preset)


def fbxToGame(name, preset):
    """
    Exports selected nodes to the game directory + the relative directory the file is found in with the given file name.

    Args:
        name (string): Name of .fbx file.

        preset (string): Preset to load for export options.
    """
    scene_path = pm.sceneName()
    game_directory = store.get('game_directory')
    relative_directory = ''

    if not game_directory:
        pm.error('Game directory is not set. Please use "Piper>Export>Set Game Directory" to set export directory.')

    if scene_path:
        source_directory = os.path.dirname(scene_path)
        art_directory = store.get('art_directory')

        # gets the relative path using the art directory
        if scene_path.startswith(art_directory):
            relative_directory = source_directory.lstrip(art_directory)
        else:
            pm.warning(scene_path + ' is not in art directory! Exporting to game directory root.')

    export_path = os.path.join(game_directory, relative_directory, name + '.fbx').replace('\\', '/')
    fbx(export_path, preset)


def mesh(piper_meshes, export_method):
    """
    Exports all or selected piper mesh groups with the given export method.

    Args:
        piper_meshes (list): Piper meshes to export.

        export_method (method): Export function to run on each piper mesh found.
    """
    for piper_mesh in piper_meshes:
        children = piper_mesh.getChildren()
        pm.parent(children, w=True)
        pm.select(children)
        export_method(piper_mesh.nodeName(), pcfg.mesh_preset)
        pm.parent(children, piper_mesh)


def skinnedMesh(skinned_meshes, export_method):
    pass


def piperNodes(export_method):
    """
    Exports all piper nodes from scene.

    Args:
        export_method (method): Export function to run for each piper node.
    """
    piper_meshes = pipernode.get('piperMesh')
    piper_skinned_meshes = pipernode.get('piperSkinnedMesh')

    mesh(piper_meshes, export_method)


def piperNodesToGameAsFBX():
    """
    Convenience method for exporting all piper nodes to the set game directory as .fbx
    """
    piperNodes(fbxToGame)


def piperNodesToSelfAsFBX():
    """
    Convenience method for exporting all piper nodes to the current directory as .fbx
    """
    piperNodes(fbxToSelf)
