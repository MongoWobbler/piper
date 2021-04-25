#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.ui.window as uiwindow
import piper.mayapy.pipernode as pipernode
import piper.mayapy.pipe.paths as paths

from . import bone


def getMeshes():
    """
    Gets all the meshes inside all the piper skinned nodes in the scene.

    Returns:
        (set): Piper transforms that hold mesh shapes grouped under piper skinned nodes.
    """
    nodes = pipernode.get('piperSkinnedMesh')
    return {mesh.getParent() for skin in nodes for mesh in skin.getChildren(ad=True, type='mesh') if mesh.getParent()}


def setLockOnMeshes(lock):
    """
    Locks or unlocks all the transforms under piper skinned nodes that have mesh shapes.

    Args:
        lock (int): Mode to set on meshes. 0 is unlocked, 1 is locked.
    """
    meshes = getMeshes()
    for mesh in meshes:
        try:
            mesh.overrideEnabled.set(1)
            mesh.overrideDisplayType.set(lock)
        except RuntimeError as error:
            pm.warning('Can\'t set lock on mesh! ' + str(error))


def lockMeshes():
    """
    Locks all the transforms under piper skinned nodes that have mesh shapes.
    """
    setLockOnMeshes(2)


def unlockMeshes():
    """
    Unlocks all the transforms under piper skinned nodes that have mesh shapes.
    """
    setLockOnMeshes(0)


def prepare():
    """
    Prepares the scene for a rig.

    Returns:
        (pm.nodetypes.Transform): Rig transform that holds all skinned meshes referenced.
    """
    # getRelativeArt checks if scene is saved
    skeleton_path = paths.getRelativeArt()
    rig_name, _ = os.path.splitext(os.path.basename(skeleton_path))
    rig_name = rig_name.split(pcfg.skinned_mesh_prefix)[-1]

    # if scene is modified, ask user if they would like to save, not save, or cancel operation
    if not uiwindow.save():
        pm.error('Scene not saved.')

    # perform a bone health check before referencing to emphasize any possible errors
    bone.health()

    # create new file, reference the skeleton into the new file, create rig group
    pm.newFile(force=True)
    rig_grp = pipernode.createRig(name=rig_name)
    pm.createReference(skeleton_path, namespace=pcfg.skeleton_namespace)
    pm.createReference(skeleton_path, namespace=pcfg.bind_namespace)
    skinned_meshes = pipernode.get('piperSkinnedMesh')
    [node.visibility.set(False) for node in skinned_meshes if node.name().startswith(pcfg.bind_namespace)]
    pm.parent(skinned_meshes, rig_grp)
    lockMeshes()

    return rig_grp
