#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.util as myu
import piper.mayapy.convert as convert


def exists(node, attributes, error=False):
    """
    Gets whether the given node has the given attributes.

    Args:
        node (pm.nodetypes.DependNode): Node to check whether it has given attributes or not.

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
        attribute (pm.general.Attribute): Attribute to lock and hide.
    """
    pm.setAttr(attribute, k=False, lock=True)


def nonKeyable(attribute):
    """
    Makes the given attribute non keyable in the channel box.

    Args:
        attribute (pm.general.Attribute): Attribute to make not keyable.
    """
    pm.setAttr(attribute, k=False, cb=True)


def attributeCompound(transform, action, attributes=None, axes=None):
    """
    Locks and hides several compound attributes with several axis.

    Args:
        transform (pm.nodetypes.DependNode): Transform with attribute(s) to hide all of its the given axis.

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
        transform (pm.nodetypes.DependNode): Transform with attribute(s) to hide all of its the given axis.

        attributes (list): Compound attributes to hide. If None given, will hide t, r, and s.

        axes (list): All axis to hide.
    """
    attributeCompound(transform, lockAndHide, attributes=attributes, axes=axes)


def nonKeyableCompound(transform, attributes=None, axes=None):
    """
    Makes given transform's given attributes with given axis non keyable

    Args:
        transform (pm.nodetypes.DependNode): Transform with attribute(s) to make non keyable for given attributes.

        attributes (list): Compound attributes to make non keyable. If None given, will use t, r, and s.

        axes (list): All axis to make non keyable.
    """
    attributeCompound(transform, nonKeyable, attributes=attributes, axes=axes)


def uniformScale(transform, axis=None):
    """
    Connects the given axis to drive the other scale axis. Locks and hides the other scale axis.

    Args:
        transform (pm.nodetypes.Transform): Transform to lock and hide other axis to make uniform scale.

        axis (string): Name of axis that will drive uniform scale.
    """
    if not axis:
        axis = 'y'

    tri_axis = convert.axisToTriAxis(axis, absolute=True)
    for lock_axis in tri_axis[1:]:
        attribute_to_lock = transform.attr('s' + lock_axis)
        transform.attr('s' + tri_axis[0]) >> attribute_to_lock
        lockAndHide(attribute_to_lock)


def bindConnect(transform, ctrl, ctrl_parent=None, fail_display=pm.warning):
    """
    Connects the transform's bind attributes onto the given ctrl's offsetParentMatrix to offset the ctrl.

    Args:
        transform (pm.nodetypes.Transform): Transform that holds bindMatrix and bindInverseMatrix attributes.

        ctrl (pm.nodetypes.Transform): Transform that will be offset by given transform's attributes.

        ctrl_parent (pm.nodetypes.Transform): Transform that will drive given ctrl.

        fail_display (method): How to display a failed connection.
    """
    bind_transform = convert.toBind(transform, fail_display)
    mult_matrix = pm.createNode('multMatrix', n=transform.name(stripNamespace=True) + ' bindMatrix_MM')
    bind_transform.worldMatrix >> mult_matrix.matrixIn[0]

    if ctrl_parent:
        bind_transform.parentInverseMatrix >> mult_matrix.matrixIn[1]
        ctrl_parent.worldMatrix >> mult_matrix.matrixIn[2]

    mult_matrix.matrixSum >> ctrl.offsetParentMatrix


def addSeparator(transform, character=pcfg.separator_character):
    """
    Adds the given character attribute to help visually separate attributes in channel box to specified transform.

    Args:
        transform (string or pm.nodetypes.DependNode): transform node to add given character attribute to.

        character (string): Character to use to visually separate attributes in channel box.
    """
    transform = pm.PyNode(transform)
    separator_count = []
    separator = character

    # get all the attributes with '_' in the transform's attributes
    for full_attribute in transform.listAttr():
        attribute = full_attribute.split(str(transform))
        if character in attribute[1]:
            separator_count.append(attribute[1].count(character))

    # make an underscore that is one '_' longer than the longest underscore
    if separator_count:
        separator = (separator * max(separator_count)) + separator

    # make the attribute
    pm.addAttr(transform, longName=separator, k=True, at='enum', en=character)
    transform.attr(separator).lock()


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


def getNextAvailableIndex(node, attribute_name, default, start_index=0):
    """
    Gets the first available index in which the given attribute is open and equal to the given default.

    Args:
        node (pm.nodetypes.DependNode): Node to get index of attribute.

        attribute_name (string): Name of attribute with "[{}]" so that index search can occur.

        default (any): Default value to attribute will have to know it is available.

        start_index (integer): index to start searching for the available attribute..

    Returns:
        (integer): First available attribute index.
    """
    i = start_index
    max_iterations = 65535  # typical c++ unsigned int range

    while i < max_iterations:
        attribute = node.attr(attribute_name.format(str(i)))
        plug = pm.connectionInfo(attribute, sfd=True)
        if not plug and attribute.get() == default:
            return i

        i += 1

    return 0


def getNextAvailableMultiplyInput(node, start_index=0):
    """
    Gets the first available input attribute from the given node.

    Args:
        node (pm.nodetypes.DependNode): Node to get next available input attribute.

        start_index (int): Index in which search will start.

    Returns:
        (pm.general.Attribute): Available attribute to plug in.
    """
    i = getNextAvailableIndex(node, 'input[{}]', 1, start_index)
    return node.attr('input[{}]'.format(str(i)))


def getNextAvailableTarget(node, start_index=0):
    """
    Gets the first available target attribute that is equal to the identity matrix.
    Usually used in matrix blend nodes.

    Args:
        node (pm.nodetypes.DependNode): Node to get target[i].targetMatrix of.

        start_index (integer): index to start searching for the available target matrix.

    Returns:
        (pm.general.Attribute): First available target attribute.
    """
    i = getNextAvailableIndex(node, 'target[{}].targetMatrix', pm.dt.Matrix(), start_index)
    return node.attr('target[{}]'.format(str(i)))
