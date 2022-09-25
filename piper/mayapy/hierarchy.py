#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm


def getRootParent(node):
    """
    Gets the top most parent of the given node. Note, it could be self.
    NOTE: This could be done with PyNode.getAllParents()[-1]

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
    Gets the first type of parent found in all the parents from the given start.

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


def getFirstTypeOrEndsWithParent(start, node_type, ends_with):
    """
    Gets the first type of parent found in all the parents from the given start.

    Args:
        start (pm.nodetypes.Transform): Transform to find type of parent.

        node_type (string): Type of transform to find.

        ends_with (string): Suffix to search in parents.

    Returns:
        (pm.nodetypes.Transform or None): First parent in of given node type if found, else None.
    """
    parents = start.getAllParents()
    for parent in parents:
        if parent.nodeType() == node_type or parent.name().endswith(ends_with):
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


def getSingleChildren(start):
    """
    Gets all the children nodes that only have one child as well.

    Args:
        start (PyNode): node to start getting the child nodes that won't branch out.

    Returns:
        (generator): Generator of all nodes with only one child node,
        Last item in list may be empty or have multiple children.
    """
    children = start.getChildren()

    while len(children) == 1:
        child = children[0]
        yield child
        children = child.getChildren()


def save(nodes=None, unparent=True):
    """
    Saves the hierarchy of the given nodes into a dictionary and un-parents all of them to the world.

    Args:
        nodes (list): Nodes to save hierarchy of.

        unparent (boolean): If True, will unparent given nodes to the world.

    Returns:
        (dictionary): Node as key, parent as value.
    """
    hierarchy = {node: node.getParent() for node in nodes if node.getParent()}

    if unparent:
        pm.parent(list(hierarchy.keys()), w=True)

    return hierarchy


def reparent(hierarchy_data, parent_method=pm.parent):
    """
    Re-parents the given hierarchy data using the given parent method.

    Args:
        hierarchy_data (dictionary): Child as key, parent as value.

        parent_method (method): Function that parents child to parent.
    """
    {parent_method([child, parent]) for child, parent in hierarchy_data.items()}
