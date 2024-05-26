#  Copyright (c) Christian Corsica. All Rights Reserved.

import maya.OpenMaya as om
import pymel.core as pm

import piper.config as pcfg
import piper.config.maya as mcfg
import piper.mayapy.hierarchy as hierarchy
import piper.mayapy.selection as selection


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
        (list): mesh_name.vtx[i] of all vertices that have given height in y-axis.
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


def getAttributed(parent=None):
    """
    Gets the mesh named accordingly to have export attributes written on to it.
    Export attributes are mostly used with metadata in engine.

    Args:
        parent (pm.nodetypes.Transform): Node to get children of to find mesh with export name.

    Returns:
        (pm.nodetypes.Transform): Transform with mesh shape named as specified in piper config.
    """
    children = parent.getChildren(ad=True, type='mesh') if parent else pm.ls(type='mesh')

    for child in children:
        transform = child.getParent()

        if transform.name(stripNamespace=True) == pcfg.mesh_with_attribute_name:
            return transform

    pm.error('No meshes with name: "{}". Please name one mesh as such.'.format(pcfg.mesh_with_attribute_name))


def assignCollisions(transforms=None):
    """
    Assigns the selected transforms as collisions to the LAST selected/given transform by
    renaming and parenting the transforms. Also creates and assigns Collision display layer.

    Args:
        transforms (pm.nodetypes.Transform): Nodes to assign as transforms. Last in list will be used for name/group.
    """
    transforms = selection.validate(transforms)
    mesh = transforms[-1]
    mesh_parent = mesh.getParent()
    collisions = transforms[:-1]

    if mesh_parent:
        pm.parent(collisions, mesh_parent)

    # maya automatically handles the index number renaming for us :)
    {pm.rename(collision, f"{mcfg.collision_prefix}{mesh.name()}_01") for collision in collisions}

    if pm.objExists(mcfg.collision_layer_name):
        collision_layer = pm.PyNode(mcfg.collision_layer_name)
    else:
        collision_layer = pm.createDisplayLayer(name=mcfg.collision_layer_name)
        collision_layer.displayType.set(1)

    # adds the collision objects to the display layer
    pm.editDisplayLayerMembers(collision_layer, collisions)
