#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.core.pythoner as python


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
