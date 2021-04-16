#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.ui.window as uiwindow
import piper.mayapy.pipernode as pipernode

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
    skeleton_path = pm.sceneName()

    # need scene to be saved in order to reference it
    if not skeleton_path:
        pm.error('Scene is not saved! Please save scene')

    # if scene is modified, ask user if they would like to save, not save, or cancel operation
    if not uiwindow.save():
        pm.error('Scene not saved.')

    bone.health()
    skinned_meshes = [pcfg.skeleton_namespace + ':' + node.name() for node in pipernode.get('piperSkinnedMesh')]

    # create new file, reference the skeleton into the new file, create rig group
    pm.newFile(force=True)
    rig_grp = pipernode.createRig()
    pm.createReference(skeleton_path, namespace=pcfg.skeleton_namespace)
    pm.parent(skinned_meshes, rig_grp)
    lockMeshes()

    return rig_grp
