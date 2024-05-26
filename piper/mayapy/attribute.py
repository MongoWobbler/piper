#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.config.maya as mcfg
import piper.mayapy.selection as selection
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


def freezeTransformations(transform, history=True):
    """
    Convenience method for making current transform the identity matrix.

    Args:
        transform (string or PyNode): Transform to freeze transformations on

        history (boolean): If True, will delete construction history of given transform.
    """
    pm.makeIdentity(transform, apply=True, t=True, r=True, s=True)

    if history:
        pm.delete(transform, ch=True)


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
    Performs the given action on the given transform's given compound attributes with the given axis.

    Args:
        transform (pm.nodetypes.DependNode): Transform with attribute(s) to hide all the given axis.

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
        transform (pm.nodetypes.DependNode): Transform with attribute(s) to hide all the given axis.

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

    if ctrl_parent:
        mult_matrix = pm.createNode('multMatrix', n=ctrl.name(stripNamespace=True) + mcfg.bind_matrix_suffix)
        bind_transform.matrix >> mult_matrix.matrixIn[0]
        ctrl_parent.worldMatrix >> mult_matrix.matrixIn[1]
        mult_matrix.matrixSum >> ctrl.offsetParentMatrix
    else:
        bind_transform.worldMatrix >> ctrl.offsetParentMatrix


def addSeparator(transform, character=mcfg.separator_character):
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
    Adds a "delete" attribute to the given transforms that marks them to be deleted on export.

    Args:
        transforms (list): List of pm.nodetypes.transform to add "delete" attribute to.
    """
    transforms = selection.validate(transforms, display=pm.warning)

    for transform in transforms:
        addSeparator(transform)
        transform.addAttr(mcfg.delete_node_attribute, at='bool', k=True, dv=1, max=1, min=1)
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
    if not source.hasAttr(mcfg.message_source):
        source.addAttr(source_message, at='message')

    if not target.hasAttr(mcfg.message_target):
        target.addAttr(target_message, at='message')

    source.attr(source_message) >> target.attr(target_message)


def addDrivenMessage(source, target):
    """
    Connects the given source to the given target with a message attribute to store driven connection.

    Args:
        source (pm.nodetypes.DependNode): Node that will have the source attribute added to it.

        target (pm.nodetypes.DependNode): Node that will have the target attribute added to it.
    """
    addMessage(source, target, mcfg.message_source, mcfg.message_target)


def addSpaceMessage(source, target):
    """
    Connects the given source to the given target with a space message attribute to store space blender connections.

    Args:
        source (pm.nodetypes.DependNode): Node that will have the space blender attribute added to it.

        target (pm.nodetypes.DependNode): Node that will have the space target attribute added to it.
    """
    addMessage(source, target, mcfg.message_space_blender, mcfg.message_space_target)


def addReverseMessage(source, target):
    """
    Connects the given source to the given target with a message attribute to store reverse driven connection.

    Args:
        source (pm.nodetypes.DependNode): Node that will have the source attribute added to it.

        target (pm.nodetypes.DependNode): Node that will have the target attribute added to it.
    """
    addMessage(source, target, mcfg.message_reverse_driver, mcfg.message_reverse_target)


def getMessagedReverseTarget(reverse_driver):
    """
    Gets the target node associated with the given reverse driver.

    Args:
        reverse_driver (pm.nodetypes.DependNode): Node that is driving the reverse target.

    Returns:
        (pm.nodetypes.DependNode): Node being driven by reverse driver.
    """
    return reverse_driver.attr(mcfg.message_reverse_driver).connections(scn=True, source=False)[0]


def getMessagedTarget(driver):
    """
    Gets the target node associated with the given driver.

    Args:
        driver (pm.nodetypes.DependNode): Node that is driving the target.

    Returns:
        (pm.nodetypes.DependNode): Node being driven by driver.
    """
    return driver.attr(mcfg.message_source).connections(scn=True, source=False)[0]


def getMessagedSpacesBlender(target):
    """
    Gets the blender matrix node from the given target.

    Args:
        target (pm.nodetypes.DependNode): Node to get blender matrix node connected to it.

    Returns:
        (pm.nodetypes.DependNode): Blender matrix node if target has attribute and is connected, else None.
    """
    if not target.hasAttr(mcfg.message_space_target):
        return None

    connection = target.attr(mcfg.message_space_target).connections(scn=True, plugs=True, destination=False)
    return connection[0].node() if connection else None


def getSourcePlug(attribute):
    """
    Convenience method for getting the source plug attribute of given attribute.

    Args:
        attribute (pm.general.Attribute): Attribute to see if it's connected or not and get its source connection.

    Returns:
        (pm.general.Attribute): Attribute that is connected to drive given attribute.
    """
    return attribute.connections(scn=True, p=True, d=False)[0] if attribute.isDestination() else None


def getDestinationNode(attribute, node_type=''):
    """
    Convenience method for getting the source plug attribute of given attribute.

    Args:
        attribute (pm.general.Attribute): Attribute to see if it's connected or not and get its source connection.

        node_type (string): Type to filter node.

    Returns:
        (pm.general.Attribute): Attribute that is connected to drive given attribute.
    """
    node = attribute.connections(scn=False, d=True, type=node_type) if attribute.isSource() else None
    return node[0] if node else None


def getDecomposeMatrix(attribute):
    """
    Gets the decomposed matrix of the given attribute if exists, else creates one.

    Args:
        attribute (pm.general.Attribute): Matrix attribute that is connected or will be connected to a decomposed matrix

    Returns:
        (pm.nodetypes.DecomposeMatrix): Decompose matrix connected to given attribute.
    """
    decompose = getDestinationNode(attribute, 'decomposeMatrix')

    if decompose:
        return decompose

    name = attribute.name().split(':')[-1].split('[')[0].replace('.', '_') + mcfg.decompose_matrix_suffix
    decompose = pm.createNode('decomposeMatrix', name=name)
    attribute >> decompose.inputMatrix
    return decompose


def getNextAvailableIndex(node, attribute_name, start_index=0):
    """
    Gets the first available index in which the given attribute is open.

    Args:
        node (pm.nodetypes.DependNode): Node to get index of attribute.

        attribute_name (string): Name of attribute with "[{}]" so that index search can occur.

        start_index (integer): index to start searching for the available attribute.

    Returns:
        (integer): First available attribute index.
    """
    i = start_index
    max_iterations = 65535  # typical c++ unsigned int range

    while i < max_iterations:
        attribute = node.attr(attribute_name.format(str(i)))
        plug = pm.connectionInfo(attribute, sfd=True)

        if not plug:
            return i

        i += 1

    return 0


def getNextAvailableIndexDefault(node, attribute_name, default, start_index=0):
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
    i = getNextAvailableIndexDefault(node, 'input[{}]', 1, start_index)
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
    i = getNextAvailableIndexDefault(node, 'target[{}].targetMatrix', pm.dt.Matrix(), start_index)
    return node.attr('target[{}]'.format(str(i)))
