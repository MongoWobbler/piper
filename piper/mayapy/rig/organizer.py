#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import piper.mayapy.pipernode as pipernode


def getMeshes():
    """
    Gets all the meshes inside all the piper skinned nodes in the scene.

    Returns:
        (set): Piper transforms that hold mesh shapes grouped under piper skinned nodes.
    """
    nodes = pipernode.get('piperSkinnedMesh')
    return {mesh.getParent() for skin in nodes for mesh in skin.getChildren(ad=True, type='mesh') if mesh.getParent()}


def lockMeshes():
    """
    Locks all the transforms under piper skinned nodes that have mesh shapes.
    """
    meshes = getMeshes()
    for mesh in meshes:
        mesh.overrideEnabled.set(1)
        mesh.overrideDisplayType.set(2)


def unlockMeshes():
    """
    Unlocks all the transforms under piper skinned nodes that have mesh shapes.
    """
    meshes = getMeshes()
    for mesh in meshes:
        mesh.overrideEnabled.set(1)
        mesh.overrideDisplayType.set(0)
