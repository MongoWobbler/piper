#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm


def cycleManipulatorSpace():
    """
    Cycles through the different manipulator spaces. Usually parent, world, and object.
    """
    if not pm.selected():
        pm.warning('Please select something to switch the manipulator space.')
        return

    current_context = pm.currentCtx()
    context_title = pm.contextInfo(current_context, t=True)

    if 'Move' in context_title:
        context_mode = pm.manipMoveContext('Move', q=True, mode=True)
        if context_mode == 0:
            pm.manipMoveContext('Move', edit=True, mode=context_mode + 1)
            print('In Parent space.'),
        elif context_mode == 1:
            pm.manipMoveContext('Move', edit=True, mode=context_mode + 1)
            print('In World space.'),
        else:
            pm.manipMoveContext('Move', edit=True, mode=0)
            print('In Object space.'),

    elif 'Rotate' in context_title:
        context_mode = pm.manipRotateContext('Rotate', q=True, mode=True)
        if context_mode == 0:
            pm.manipRotateContext('Rotate', edit=True, mode=context_mode + 1)
            print('In World space.'),
        elif context_mode == 1:
            pm.manipRotateContext('Rotate', edit=True, mode=context_mode + 1)
            print('In Gimbal space.'),
        else:
            pm.manipRotateContext('Rotate', edit=True, mode=0)
            print('In Object space.'),

    elif 'Scale' in context_title:
        context_mode = pm.manipScaleContext('Scale', q=True, mode=True)
        if context_mode == 0:
            pm.manipScaleContext('Scale', edit=True, mode=context_mode + 1)
            print('In Parent space.'),
        elif context_mode == 1:
            pm.manipScaleContext('Scale', edit=True, mode=context_mode + 1)
            print('In World space.'),
        else:
            pm.manipScaleContext('Scale', edit=True, mode=0)
            print('In Object space.'),


def isShiftHeld():
    """
    Gets whether shift is held or not. Returns false during batch.

    Returns:
        (bool): True if shift is held.
    """
    return False if pm.about(batch=True) else (pm.getModifiers() & 1) > 0


def isCtrlHeld():
    """
    Gets whether CTRL key is held or not. Returns false during batch.

    Returns:
        (bool): True if ctrl is held.
    """
    return False if pm.about(batch=True) else (pm.getModifiers() & 4) > 0


def isAltHeld():
    """
    Gets whether ALT key is held or not. Returns false during batch.

    Returns:
        (bool): True if alt is held.
    """
    return False if pm.about(batch=True) else (pm.getModifiers() & 8) > 0


def getAllParents(start):
    """
    Gets all the parents from the given start node.
    NOTE: You could also do PyNode.getAllParents().

    Args:
        start (PyNode): node to start getting all the parents.

    Returns:
        (generator): Generator of all parents of given start node.
    """
    parent = start.getParent()

    while parent:
        node = parent
        yield parent
        parent = node.getParent()


def getRootParent(node):
    """
    Gets the top most parent of the given node. Note, it could be self.

    Args:
        node (PyNode): Node to get the top most parent of.

    Returns:
        (PyNode): The parent of the given node.
    """
    while True:
        parent = node.getParent()

        if parent:
            node = parent
        else:
            break

    return node


def getRootParents(nodes):
    """
    Gets all the root parents from the given nodes.

    Args:
        nodes (list): Nodes to get root parents of.

    Returns:
        (set): Root parents of given nodes.
    """
    return {getRootParent(node) for node in nodes}


def hasMeshes(node):
    """
    Gets whether the given node consists of mesh(es)

    Args:
        node (string or PyNode): node to check whether it hs meshes or not.

    Returns:
        (boolean): True if consists of meshes, False if given node does not consist of meshes.
    """
    meshes = pm.ls(node, dag=True, ap=True, type='mesh')
    return True if meshes else False


def getSkinnedMeshes(skin_clusters):
    """
    Gets all the skinned meshes as a root join dictionary associated with the given skin clusters.

    Args:
        skin_clusters (list): SkinCluster to find geometry and influence objects (joints) of.

    Returns:
        (dictionary): Root joint as key, set of geometry being influenced as value.
    """
    skin_info = {}
    for skin_cluster in skin_clusters:
        joints = skin_cluster.influenceObjects()
        root_joint = getRootParent(joints[0])
        geometry = set(skin_cluster.getGeometry())
        skin_info[root_joint] = skin_info[root_joint] | geometry if root_joint in skin_info else geometry

    return skin_info


def getConstrainedTargets(driver, constraint_type='parentConstraint'):
    """
    Gets all the transforms the given driver is driving through the giving constraint type.

    Args:
        driver (PyNode): The transform that is driving the other transform(s) through a constraint.

        constraint_type (string): The type of constraint to look for.
        Normally "parentConstraint", "pointConstraint", "orientConstraint", or "scaleConstraint".

    Returns:
        (set): Transform(s) being driven by given driver through given constraint type.
    """
    # Using sets to remove duplicates from list connections because Maya
    constraints = set(driver.listConnections(type=constraint_type))
    targets = set()
    for constraint in constraints:
        targets.update(set(constraint.connections(source=False, destination=True, et=True, type='transform')))

    return targets
