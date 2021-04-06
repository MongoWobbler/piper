#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.util as myu


def exists(node, attributes, error=False):
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


def addMessage(source, target, source_message, target_message):
    """
    Connects the given source to the given target with the given message attributes.

    Args:
        source (pm.nodetypes.DependNode): Node that will have the source attribute added to it.

        target (pm.nodetypes.DependNode): Node that will have the target attribute added to it.

        source_message (string): Name of source message attribute to add.

        target_message (string): Name of target message attribute to add.
    """
    if not source.hasAttr(pcfg.message_source):
        source.addAttr(source_message, at='message')

    if not target.hasAttr(pcfg.message_target):
        target.addAttr(target_message, at='message')

    source.attr(source_message) >> target.attr(target_message)


def addDrivenMessage(source, target):
    """
    Connects the given source to the given target with a message attribute to store driven connection.

    Args:
        source (pm.nodetypes.DependNode): Node that will have the source attribute added to it.

        target (pm.nodetypes.DependNode): Node that will have the target attribute added to it.
    """
    addMessage(source, target, pcfg.message_source, pcfg.message_target)


def addReverseMessage(source, target):
    """
    Connects the given source to the given target with a message attribute to store reverse driven connection.

    Args:
        source (pm.nodetypes.DependNode): Node that will have the source attribute added to it.

        target (pm.nodetypes.DependNode): Node that will have the target attribute added to it.
    """
    addMessage(source, target, pcfg.message_reverse_driver, pcfg.message_reverse_target)


def getMessagedReverseTarget(reverse_driver):
    """
    Gets the target node associated with the given reverse driver.

    Args:
        reverse_driver (pm.nodetypes.DependNode): Node that is driving the reverse target.

    Returns:
        (pm.nodetypes.DependNode): Node being driven by reverse driver.
    """
    return reverse_driver.attr(pcfg.message_reverse_driver).connections(scn=True, source=False)[0]


def getMessagedTarget(driver):
    """
    Gets the target node associated with the given driver.

    Args:
        driver (pm.nodetypes.DependNode): Node that is driving the target.

    Returns:
        (pm.nodetypes.DependNode): Node being driven by driver.
    """
    return driver.attr(pcfg.message_source).connections(scn=True, source=False)[0]


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
