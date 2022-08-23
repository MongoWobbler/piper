#  Copyright (c) Christian Corsica. All Rights Reserved.

import maya.OpenMaya as om
import pymel.core as pm
import piper.mayapy.hierarchy as hierarchy


def exists(node):
    """
    Gets whether the given node consists of mesh(es).
    NOTE: You could also do PyNode.getShapes().

    Args:
        node (string or PyNode): node to check whether it hs meshes or not.

    Returns:
        (boolean): True if consists of meshes, False if given node does not consist of meshes.
    """
    meshes = pm.ls(node, dag=True, ap=True, type='mesh')
    return True if meshes else False


def getSkinned(skin_clusters):
    """
    Gets all the skinned meshes as a root joint dictionary associated with the given skin clusters.

    Args:
        skin_clusters (Iterable): SkinCluster to find geometry and influence objects (joints) of.

    Returns:
        (dictionary): Root joint as key, set of geometry being influenced as value.
    """
    skin_info = {}
    for skin_cluster in skin_clusters:
        joints = skin_cluster.influenceObjects()
        root_joint = hierarchy.getRootParent(joints[0])
        geometry = set(skin_cluster.getGeometry())
        skin_info[root_joint] = skin_info[root_joint] | geometry if root_joint in skin_info else geometry

    return skin_info


def getVertexPositions(transform_name):
    """
    Gets all the vertex positions the given transforms has.
    Oddly enough, maya commands are faster than the maya python api.
    https://www.fevrierdorian.com/blog/post/2011/09/27/Quickly-retrieve-vertex-positions-of-a-Maya-mesh-%28English-Translation%29

    Args:
        transform_name (string): Name of transform to get vertices of

    Returns:
        (list): Vertex positions.
    """
    positions = pm.xform('{}.vtx[*]'.format(transform_name), q=True, ws=True, t=True)
    return zip(positions[0::3], positions[1::3], positions[2::3])


def getVerticesAtHeight(mesh_name, height):
    """
    Gets all the vertices that are at the given height (y-axis).

    Args:
        mesh_name (string): Name of mesh to find vertices at given y value

        height (float): Y axis value to find vertices that have that same y value.

    Returns:
        (list): mesh_name.vtx[i] of all vertices that have given height in y axis.
    """
    # Get Api MDagPath for object
    vertices = []
    mesh_path = om.MDagPath()
    mesh_selection = om.MSelectionList()
    mesh_selection.add(mesh_name)
    mesh_selection.getDagPath(0, mesh_path)

    # Iterate over all the mesh vertices and get vertices at the given height
    vertex_i = om.MItMeshVertex(mesh_path)
    while not vertex_i.isDone():

        if vertex_i.position(om.MSpace.kWorld).y == height:
            vertices.append(mesh_name + '.vtx[' + str(vertex_i.index()) + ']')

        next(vertex_i)

    return vertices
