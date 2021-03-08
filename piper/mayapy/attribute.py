#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.util as myu


def lockAndHide(attribute):
    """
    Locks and hides the given attribute.

    Args:
        attribute (pm.nodetypes.Attribute): Attribute to lock and hide.
    """
    pm.setAttr(attribute, k=False, lock=True)


def nonKeyable(attribute):
    """
    Makes the given attribute non keyable in the channel box.

    Args:
        attribute (pm.nodetypes.Attribute): Attribute to make not keyable.
    """
    pm.setAttr(attribute, k=False, cb=True)


def attributeCompound(transform, action, attributes=None, axes=None):
    """
    Locks and hides several compound attributes with several axis.

    Args:
        transform (PyNode): Transform with attribute(s) to hide all of its the given axis.

        action (method): action that will be performed on given transform attributes.

        attributes (list): Compound attributes to hide. If None given, will hide t, r, and s.

        axes (list): All axis to hide.
    """
    if not attributes:
        attributes = ['t', 'r', 's']

    if not axes:
        axes = ['x', 'y', 'z']

    [action(transform.attr(attribute + axis)) for axis in axes for attribute in attributes]


def lockAndHideCompound(transform, attributes=None, axes=None):
    """
    Locks and hides several compound attributes with several axis.

    Args:
        transform (PyNode): Transform with attribute(s) to hide all of its the given axis.

        attributes (list): Compound attributes to hide. If None given, will hide t, r, and s.

        axes (list): All axis to hide.
    """
    attributeCompound(transform, lockAndHide, attributes=attributes, axes=axes)


def nonKeyableCompound(transform, attributes=None, axes=None):
    """
    Makes given transform's given attributes with given axis non keyable

    Args:
        transform (PyNode): Transform with attribute(s) to make non keyable for given attributes and axis.

        attributes (list): Compound attributes to make non keyable. If None given, will use t, r, and s.

        axes (list): All axis to make non keyable.
    """
    attributeCompound(transform, nonKeyable, attributes=attributes, axes=axes)


def addSeparator(transform):
    """
    Adds a '_' attribute to help visually separate attributes in channel box to specified transform.

    Args:
        transform (string or PyNode): transform node to add a '_' attribute to.
    """
    transform = pm.PyNode(transform)
    underscore_count = []
    underscore = '_'

    # get all the attributes with '_' in the transform's attributes
    for full_attribute in transform.listAttr():
        attribute = full_attribute.split(str(transform))
        if '_' in attribute[1]:
            underscore_count.append(attribute[1].count('_'))

    # make an underscore that is one '_' longer than the longest underscore
    if underscore_count:
        underscore = (underscore * max(underscore_count)) + underscore

    # make the attribute
    pm.addAttr(transform, longName=underscore, k=True, at='enum', en='_')
    transform.attr(underscore).lock()


def addDelete(transforms=None):
    """
    Adds a "delete" attribute to the given transforms that marks them to be delete on export.

    Args:
        transforms (list): List of pm.nodetypes.transform to add "delete" attribute to.
    """
    transforms = myu.validateSelect(transforms, display=pm.warning)

    for transform in transforms:
        addSeparator(transform)
        transform.addAttr(pcfg.delete_node_attribute, at='bool', k=True, dv=1, max=1, min=1)
        nonKeyable(transform.delete)


def getNextAvailableIndexFromTargetMatrix(node, start_index=0):
    """
    Gets the first available index in which the target matrix is open and equal to the identity matrix.
    Usually used in matrix blend nodes.

    Args:
        node (PyNode): Node to get target[i].targetMatrix of.

        start_index (integer): index to start searching for the available target matrix.

    Returns:
        (Attribute): First available target attribute.
    """
    i = start_index
    max_iterations = 1000000

    while i < max_iterations:
        attribute = node.attr('target[{}].targetMatrix'.format(str(i)))
        plug = pm.connectionInfo(attribute, sfd=True)
        if not plug and attribute.get() == pm.dt.Matrix():
            return i

        i += 1

    return 0


def getNextAvailableTarget(node, start_index=0):
    """
    Gets the first available target attribute that is equal to the identity matrix.
    Usually used in matrix blend nodes.

    Args:
        node (PyNode): Node to get target[i].targetMatrix of.

        start_index (integer): index to start searching for the available target matrix.

    Returns:
        (Attribute): First available target attribute.
    """
    i = getNextAvailableIndexFromTargetMatrix(node, start_index)
    return node.attr('target[{}]'.format(str(i)))