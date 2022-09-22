#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.core.pythoner as python
import piper.mayapy.hierarchy as hierarchy


def validate(nodes=None, minimum=0, maximum=0, find=None, parent=False, display=pm.error):
    """
    Validates the nodes given. If None given, will try to use selected nodes. Will throw error if validation fails.

    Args:
        nodes (collections.iterable): Nodes to validate.

        minimum (int): Minimum amount of nodes that we need.

        maximum (int): Maximum amount of nodes that we can operate on.

        find (string): Type of node to look for if no nodes given and nothing selected. Will also filter for these only.

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

    if find and not parent:
        nodes = pm.ls(nodes, type=find)

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


@python.parametrized
def save(method, clear=False):
    """
    Decorator for saving selection but clearing it out when calling function.

    Args:
        method (function): Function to save selection when called.

        clear (boolean): If True, will clear selection before calling function.
    """
    def wrapper(*args, **kwargs):
        selection = pm.selected()
        pm.select(cl=clear)
        result = method(*args, **kwargs)
        pm.select(selection)
        return result

    return wrapper


def get(node_type, ignore=None, search=True):
    """
    Gets the selected given node type or all the given node types in the scene if none selected.

    Args:
        node_type (string): Type of node to get.

        ignore (string): If given and piper node is a child of given ignore type, do not return the piper node.

        search (boolean): If True, and nothing is selected, will attempt to search the scene for all the given type.

    Returns:
        (list) All nodes of the given node type.
    """
    nodes = []
    selected = pm.selected()

    if selected:
        # get only the piper nodes from selection
        nodes = pm.ls(selected, type=node_type)

        # traverse hierarchy for piper nodes
        if not nodes:
            nodes = set()
            for node in selected:
                first_type_parent = hierarchy.getFirstTypeParent(node, node_type)
                nodes.add(first_type_parent) if first_type_parent else None

    # search the whole scene for the piper node
    elif search:
        nodes = pm.ls(type=node_type)

    # don't include any nodes that are a child of the given ignore type
    if ignore:
        nodes = [node for node in nodes if not hierarchy.getFirstTypeParent(node, ignore)]

    return nodes

