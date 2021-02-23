#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm


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


def freezeTransformations(transform):
    """
    Convenience method for making current transform the identity matrix.

    Args:
        transform (string or PyNode): Transform to freeze transformations on
    """
    pm.makeIdentity(transform, apply=True, t=True, r=True, s=True)


def validateSelect(nodes=None, minimum=0, maximum=0, find=None, parent=False, display=pm.error):
    """
    Validates the nodes given. If None given, will try to use selected nodes. Will throw error if validation fails.

    Args:
        nodes (collections.iterable): Nodes to validate.

        minimum (int): Minimum amount of nodes that we need.

        maximum (int): Maximum amount of nodes that we can operate on.

        find (string): Type of node to look for if no nodes given and nothing selected.

        parent (boolean): Used with the find kwarg. If True, will return the parent of the find type. Useful for shapes.

        display (method): How to display a bad validation.

    Returns:
        (list): Nodes that are ready to be operated on.
    """
    # If user chooses not to display anything, we must pass an empty function
    if not display:

        def _nothing(*args):
            pass  # using a function instead of a lambda one-liner because PEP-8

        display = _nothing

    if not nodes:
        nodes = pm.selected()

    if not nodes and find:
        nodes = pm.ls(type=find)

        if parent:
            nodes = list({node.getParent() for node in nodes})

    if not nodes:
        display('Nothing selected!')
        return []

    if len(nodes) < minimum:
        display('Not enough selected. Please select at least ' + str(minimum) + ' objects.')
        return []

    if 1 < maximum < len(nodes):
        display('Too many objects selected. Please select up to ' + str(maximum) + ' objects.')
        return []

    return nodes


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


def getFirstTypeParent(start, node_type):
    """
    Gets the first type of parent found in all of the parents from the given start.

    Args:
        start (pm.nodetypes.Transform): Transform to find type of parent.

        node_type (string): Type of transform to find.

    Returns:
        (pm.nodetypes.Transform or None): First parent in of given node type if found, else None.
    """
    parents = start.getAllParents()
    for parent in parents:
        if parent.nodeType() == node_type:
            return parent

    return None


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


def hasAttributes(node, attributes, error=False):
    """
    Gets whether the given node has the given attributes.

    Args:
        node (PyNode): Node to check whether it has given attributes or not.

        attributes (list): Strings of attributes to check whether they are in node or not.

        error (boolean): If True and an attribute is NOT found, will raise error.

    Returns:
        (boolean): True if given node has ALL the given attributes, False if node is one attribute.
    """
    for attribute in attributes:
        if not node.hasAttr(attribute):
            return pm.error(node + ' is missing the ' + attribute + ' attribute!') if error else False

    return True


def hasMeshes(node):
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


def getManipulatorPosition(transform):
    """
    Gets position of move manipulator where control is.

    Args:
        transform (string, PyNode, list, tuple, or set): Name of object(s) to get position from.

    Returns:
        (list): [x, y, z], World position of object in three coordinates.
    """
    pm.select(transform)
    pm.setToolTo('Move')
    position = pm.manipMoveContext('Move', q=1, p=1)
    pm.select(clear=True)
    return position


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


def cycleManipulatorSpace():
    """
    Cycles through the different manipulator spaces. Usually parent, world, and object.
    """
    validateSelect()
    current_context = pm.currentCtx()
    context_title = pm.contextInfo(current_context, t=True)

    if 'Move' in context_title:
        context_mode = pm.manipMoveContext('Move', q=True, mode=True)
        if context_mode == 0:
            pm.manipMoveContext('Move', edit=True, mode=context_mode + 1)
            pm.displayInfo('In Parent space.')
        elif context_mode == 1:
            pm.manipMoveContext('Move', edit=True, mode=context_mode + 1)
            pm.displayInfo('In World space.')
        else:
            pm.manipMoveContext('Move', edit=True, mode=0)
            pm.displayInfo('In Object space.')

    elif 'Rotate' in context_title:
        context_mode = pm.manipRotateContext('Rotate', q=True, mode=True)
        if context_mode == 0:
            pm.manipRotateContext('Rotate', edit=True, mode=context_mode + 1)
            pm.displayInfo('In World space.')
        elif context_mode == 1:
            pm.manipRotateContext('Rotate', edit=True, mode=context_mode + 1)
            pm.displayInfo('In Gimbal space.')
        else:
            pm.manipRotateContext('Rotate', edit=True, mode=0)
            pm.displayInfo('In Object space.')

    elif 'Scale' in context_title:
        context_mode = pm.manipScaleContext('Scale', q=True, mode=True)
        if context_mode == 0:
            pm.manipScaleContext('Scale', edit=True, mode=context_mode + 1)
            pm.displayInfo('In Parent space.')
        elif context_mode == 1:
            pm.manipScaleContext('Scale', edit=True, mode=context_mode + 1)
            pm.displayInfo('In World space.')
        else:
            pm.manipScaleContext('Scale', edit=True, mode=0)
            pm.displayInfo('In Object space.')
