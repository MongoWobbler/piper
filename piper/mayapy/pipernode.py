#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.util as myu


def get(node_type):
    """
    Gets the selected given node type or all the given node types in the scene if none selected.

    Args:
        node_type (string): Type of node to get.

    Returns:
        (list) All nodes of the given node type.
    """
    selected = pm.selected()
    piper_nodes = pm.ls(selected, type=node_type) if selected else pm.ls(type=node_type)
    return piper_nodes


def create(node_type, color, name=None, parent=None):
    """
    Creates the given node type with the given color and given name/parent.

    Args:
        node_type (string): Node type to create.

        color (string): Name of color to turn outliner text to. Currently supporting:
        cyan, pink.

        name (string): Name of node.

        parent (PyNode or string): Parent of new node.

    Returns:
        (PyNode): Node created.
    """

    if color == 'cyan':
        rgb = [0, 1, 1]
    elif color == 'pink':
        rgb = [1, 0, 1]
    else:
        rgb = None

    name = name if name else node_type
    piper_node = pm.createNode(node_type, name=name, parent=parent, skipSelect=True)
    piper_node.useOutlinerColor.set(True)

    if rgb:
        piper_node.outlinerColor.set(rgb)

    return piper_node


def createMesh():
    """
    Creates a piper mesh group(s) based on whether user has selection, shift held, and scene saved.

    Returns:
        (PyNode or list): Usually PyNode created. If Shift held, will return list or all piperMesh(es) created.
    """
    selected = pm.selected()
    scene_name = pm.sceneName().namebase

    if selected:
        # if shift held, create a a piper mesh for each selected object.
        if myu.isShiftHeld():
            piper_meshes = []
            for node in selected:
                parent = node.getParent()
                name = pcfg.mesh_prefix + node.nodeName()
                piper_mesh = create('piperMesh', 'cyan', name=name, parent=parent)
                pm.parent(node, piper_mesh)
                piper_meshes.append(piper_mesh)

            return piper_meshes
        else:
            # If user selected stuff that is not a mesh, warn the user.
            non_mesh_transforms = [node for node in selected if not myu.hasMeshes(node)]
            if non_mesh_transforms:
                pm.warning('The following are not meshes! \n' + '\n'.join(non_mesh_transforms))

            # Get the parent roots and parent them under the piper mesh node to not mess up any hierarchies.
            name = pcfg.mesh_prefix
            name += scene_name if scene_name else selected[-1].nodeName()
            piper_mesh = create('piperMesh', 'cyan', name=name)
            parents = myu.getRootParents(selected)
            pm.parent(parents, piper_mesh)

            return piper_mesh

    name = '' if scene_name.startswith(pcfg.mesh_prefix) else pcfg.mesh_prefix
    name += scene_name if scene_name else 'piperMesh'
    piper_mesh = create('piperMesh', 'cyan', name=name)
    meshes = pm.ls(type='mesh')
    parents = myu.getRootParents(meshes)
    pm.parent(parents, piper_mesh)

    return piper_mesh


def createSkinnedMesh():
    """
    Creates a skinned mesh node for each root joint found in the skin clusters

    Returns:
        (list): PyNodes of nodes created.
    """
    selected = pm.selected()
    scene_name = pm.sceneName().namebase

    if selected:
        skin_clusters = set()
        skin_clusters.update(set(pm.listConnections(selected, type='skinCluster')))
        skin_clusters.update(set(pm.listHistory(selected, type='skinCluster')))
    else:
        skin_clusters = pm.ls(type='skinCluster')

    if not skin_clusters:
        pm.warning('No skin clusters found!')
        piper_skinned_mesh = create('piperSkinnedMesh', 'pink', name=pcfg.skinned_mesh_prefix + 'piperSkinnedMesh')
        return [piper_skinned_mesh]

    piper_skinned_meshes = []
    skinned_meshes = myu.getSkinnedMeshes(skin_clusters)
    for root_joint, geometry in skinned_meshes.items():
        name = '' if scene_name.startswith(pcfg.skinned_mesh_prefix) else pcfg.skinned_mesh_prefix
        name += scene_name if scene_name else next(iter(geometry)).nodeName()
        piper_skinned_mesh = create('piperSkinnedMesh', 'pink', name=name)
        piper_skinned_meshes.append(piper_skinned_mesh)
        geometry_parents = myu.getRootParents(geometry)
        pm.parent(root_joint, geometry_parents, piper_skinned_mesh)

    return piper_skinned_meshes


def createAnimation():
    # animation should be dark green (0, .7, 0)
    pass
