#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.util as myu
import piper.mayapy.convert as convert
import piper.mayapy.pipermath as pipermath


def transformToOffsetMatrix(transform):
    """
    Convenience method for moving the matrix of a transform to the offset matrix and zeroing out the values.
    Similar to makeIdentity or Freeze Transforms, except values end up in offsetParentMatrix.

    Args:
        transform (pm.nodetypes.Transform): Transform to zero out.
    """
    transform.offsetParentMatrix.set(transform.matrix.get())
    pipermath.zeroOut(transform)


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


def addDeleteAttribute(transforms=None):
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


def getChain(start, end=None):
    """
    Gets all the transforms parented between the given start and end transforms, inclusive.

    Args:
        start (pm.nodetypes.Transform): Top parent of the chain.

        end (pm.nodetypes.Transform): The child to end search at. If none given, will return only the given start.

    Returns:
        (list): All the transforms between given start and given end, including the given transforms in order.
    """
    if not end:
        return [start]

    parents = end.getAllParents()

    if start not in parents:
        pm.error(start.nodeName() + ' is not a parent of: ' + end.nodeName())

    parents.reverse()
    start_index = parents.index(start)
    chain = parents[start_index:]
    chain.append(end)
    return chain


def duplicateChain(chain, prefix='new_', color='default'):
    """
    Duplicates the given chain, renames it, and parents it to the world.

    Args:
        chain (list): Transforms to duplicate.

        prefix (string): Prefix to add to duplicate transforms.

        color (string): Color to set the duplicate chain.

    Returns:
        (list): Duplicated transforms with new name.
    """
    new_chain = pm.duplicate(chain, parentOnly=True, renameChildren=True)
    [new_chain[i].rename(prefix + chain[i].nodeName()) for i in range(len(chain))]
    start = new_chain[0]
    pm.parent(start, w=True)
    start.overrideEnabled.set(True)
    start.overrideColor.set(convert.colorToInt(color))
    return new_chain


def parentTransforms(*transforms):
    """
    Parents transforms to the last given transform and gets rid of joint orient values if transform is a joint.

    Args:
        transforms (list or pm.nodetypes.Transform): Transforms to parent. Last transform is the parent of the rest.
        Minimum of two objects.
    """
    transforms = myu.validateSelect(transforms, minimum=2)
    for joint in transforms[:-1]:

        if isinstance(joint, pm.nodetypes.Joint):
            matrix = joint.worldMatrix.get()
            pm.parent(joint, transforms[-1])
            joint.jointOrient.set(0, 0, 0)
            pm.xform(joint, ws=True, m=matrix)
        else:
            pm.parent(joint, transforms[-1])


def mirrorTranslate(transforms=None, axis=pcfg.default_mirror_axis, swap=None, duplicate=True):
    """
    Mirrors the given transforms across the given axis set up to be used as a mirror translate transform.

    Args:
        transforms (list): Transforms to mirror across given axis.

        axis (string): Name of axis to mirror across.

        swap (list): Text to swap with each other for duplicates name.

        duplicate (boolean): If True will duplicate transforms before mirroring. Else will mirror the given transforms.

    Returns:
        (list): Transforms mirrored.
    """
    transforms = myu.validateSelect(transforms)
    axis_vector = convert.axisToVector(axis, absolute=True)
    mirrored_axis = [value * -1 for value in axis_vector]
    mirrored_axis.append(1)
    to_mirror = []

    if swap is None:
        swap = [pcfg.left_suffix, pcfg.right_suffix]

    if duplicate:
        for transform in transforms:
            name = transform.nodeName()
            new_name = pcu.swapText(name, *swap)
            new_transform = pm.duplicate(transform, ic=False, un=False, n=new_name)[0]
            to_mirror.append(new_transform)
    else:
        to_mirror = transforms

    for transform in to_mirror:
        matrix = transform.worldMatrix.get()
        identity = [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]
        mirrored_matrix = [m * a if m != 0 and a != 0 else m for row in identity for m, a in zip(row, mirrored_axis)]
        mirrored_matrix = matrix * pm.dt.Matrix(mirrored_matrix)
        pm.xform(transform, ws=True, m=mirrored_matrix)
        [transform.attr('s' + axis).set(abs(transform.attr('s' + axis).get())) for axis in ['x', 'y', 'z']]

    return to_mirror


def mirrorRotate(transforms=None, axis=pcfg.default_mirror_axis, swap=None):
    """
    Mirrors the given transforms across the given axis set up to be used as a mirror rotate transform.

    Args:
        transforms (list): Transforms to mirror across given axis.

        axis (string): Name of axis to mirror across.

        swap (list): Words to search and replace. Will search for first index, and replace with second index.

    Returns:
        (list): Joints that were mirrored. Note that all their children get mirrored as well.
    """
    mirrored_transforms = []
    transforms = myu.validateSelect(transforms)
    options = {'mxy': False, 'myz': False, 'mxz': False, 'mb': True, 'sr': swap}

    if axis == 'x':
        options['myz'] = True
    elif axis == 'y':
        options['mxz'] = True
    elif axis == 'z':
        options['mxy'] = True
    else:
        pm.error('No valid axis given. Pick "x", "y", or "z".')

    for transform in transforms:
        name = transform.nodeName()

        if not swap:
            if name.endswith(pcfg.left_suffix):
                options['sr'] = [pcfg.left_suffix, pcfg.right_suffix]
            elif name.endswith(pcfg.right_suffix):
                options['sr'] = [pcfg.right_suffix, pcfg.left_suffix]

        mirrored_joint = pm.mirrorJoint(transform, **options)[0]
        mirrored_joint = pm.PyNode(mirrored_joint)
        mirrored_transforms.append(mirrored_joint)
        parent = mirrored_joint.getParent()

        if mirrored_joint.getParent():
            pm.parent(mirrored_joint, w=True)
            parentTransforms(mirrored_joint, parent)

    return mirrored_transforms


def parentMatrixConstraint(driver=None, target=None, t=True, r=True, s=True, offset=False, joint_orient=False):
    """
    Creates a parent matrix constraint between given driver and target. Could use selected objects too.
    Shout-out to Jarred Love for his tutorials.

    Args:
        driver (pm.nodetypes.Transform): Transform that will drive the given target

        target (pm.nodetypes.Transform): Transform that will be driven by given driver.

        t (boolean): If True, will connect translate channel to be driven.

        r (boolean): If True, will connect rotate channel to be driven.

        s (boolean): If True, will connect scale channel to be driven.

        offset (boolean): If True, will maintain current transform relation between given driver and target.

        joint_orient (boolean): If True, AND given target transform has non-zero joint orient values,
        will create extra nodes to account for such values. Else will set joint orient values to zero.
    """
    if not driver or not target:
        selected = pm.selected()

        if len(selected) < 2:
            pm.error('Not enough items selected and no driver or target found!')

        driver = selected[-2]
        target = selected[-1]

    name = target.nodeName()
    matrix_multiplication = pm.createNode('multMatrix', n=name + pcfg.parent_matrix_mult_suffix)
    decompose_matrix = pm.createNode('decomposeMatrix', n=name + pcfg.parent_matrix_decomp_suffix)

    if offset:
        offset = target.worldMatrix.get() * driver.worldInverseMatrix.get()
        matrix_multiplication.matrixIn[0].set(offset)
        driver.worldMatrix[0] >> matrix_multiplication.matrixIn[1]
        target.parentInverseMatrix[0] >> matrix_multiplication.matrixIn[2]
    else:
        driver.worldMatrix[0] >> matrix_multiplication.matrixIn[0]
        target.parentInverseMatrix[0] >> matrix_multiplication.matrixIn[1]

    matrix_multiplication.matrixSum >> decompose_matrix.inputMatrix

    if t:
        decompose_matrix.outputTranslate >> target.translate

    if r:
        if target.hasAttr('jointOrient') and target.jointOrient.get() != pm.dt.Vector(0, 0, 0):
            if joint_orient:
                compose_matrix = pm.createNode('composeMatrix', n=name + pcfg.parent_matrix_rot_comp_suffix)
                compose_matrix.inputRotate.set(target.jointOrient.get())
                parent = target.getParent()

                if parent:
                    mult_rot_matrix = pm.createNode('multMatrix', n=name + pcfg.parent_matrix_rot_mult_suffix)
                    compose_matrix.outputMatrix >> mult_rot_matrix.matrixIn[0]
                    parent.worldMatrix >> mult_rot_matrix.matrixIn[1]
                    joint_orient_matrix_output = mult_rot_matrix.matrixSum
                else:
                    joint_orient_matrix_output = compose_matrix.outputMatrix

                inverse_matrix = pm.createNode('inverseMatrix', n=name + pcfg.parent_matrix_rot_inv_suffix)
                joint_orient_matrix_output >> inverse_matrix.inputMatrix

                mult_rot_matrix = pm.createNode('multMatrix', n=name + pcfg.parent_matrix_rot_mult_suffix)

                if offset:
                    offset = target.worldMatrix.get() * driver.worldInverseMatrix.get()
                    mult_rot_matrix.matrixIn[0].set(offset)
                    driver.worldMatrix >> mult_rot_matrix.matrixIn[1]
                    inverse_matrix.outputMatrix >> mult_rot_matrix.matrixIn[2]
                else:
                    driver.worldMatrix >> mult_rot_matrix.matrixIn[0]
                    inverse_matrix.outputMatrix >> mult_rot_matrix.matrixIn[1]

                rotate_decompose = pm.createNode('decomposeMatrix', n=name + pcfg.parent_matrix_rot_decomp_suffix)
                mult_rot_matrix.matrixSum >> rotate_decompose.inputMatrix
                rotate_decompose.outputRotate >> target.rotate

            else:
                target.jointOrient.set((0, 0, 0))
                decompose_matrix.outputRotate >> target.rotate

        else:
            decompose_matrix.outputRotate >> target.rotate

    if s:
        decompose_matrix.outputScale >> target.scale


def poleVectorMatrixConstraint(ik_handle, control):
    """
    Creates a pole vector matrix constraint from the given ik_handle's start joint driven by the given pole vector ctrl.
    Thanks to Wasim Khan for this method.
    https://github.com/wasimk/maya-pole-vector-constaint

    Args:
        ik_handle (pm.nodetypes.IkHandle): IK Handle that will be driven by pole vector control.

        control (pm.nodetypes.Transform): Control that will drive the ik_handle rotations.

    Returns:
        (list): All nodes created.
    """
    if ik_handle.nodeType() != 'ikHandle':
        pm.error(ik_handle.nodeName() + ' is not an IK Handle!')

    addSeparator(control)
    pm.addAttr(control, at='float', ln='poleVectorWeight', dv=1, min=0, max=1, k=True, w=True, r=True)
    joint = pm.PyNode(pm.ikHandle(ik_handle, q=True, startJoint=True))

    # First create all necessary nodes needed for pole vector math
    world_point = pm.createNode('pointMatrixMult', name='{}_Position_PointMatrixMult'.format(joint))
    compose_matrix = pm.createNode('composeMatrix', name='{}_Position_CompMatrix'.format(joint))
    inverse_matrix = pm.createNode('inverseMatrix', name='{}_Position_InverseMatrix'.format(joint))
    multiplication_matrix = pm.createNode('multMatrix', name='{}_PolePosition_MultMatrix'.format(ik_handle))
    pole_matrix = pm.createNode('pointMatrixMult', name='{}_PolePosition_PointMatrixMult'.format(ik_handle))
    blend_colors = pm.createNode('blendColors', name='{}_Blend_PoleWeight'.format(ik_handle))
    blend_colors.color2.set(ik_handle.poleVector.get())

    # Since ikHandle is setting rotation value on startJoint, we can't connect worldMatrix right away.
    # In order to avoid cycle, Compose world space position for start joint with pointMatrixMult node
    # Connecting position attribute and parentMatrix will give us worldSpace position
    joint.translate >> world_point.inPoint
    joint.parentMatrix >> world_point.inMatrix

    # Now composeMatrix from output, so we can inverse and find local position from startJoint to pole control
    world_point.output >> compose_matrix.inputTranslate
    compose_matrix.outputMatrix >> inverse_matrix.inputMatrix
    control.worldMatrix >> multiplication_matrix.matrixIn[0]
    inverse_matrix.outputMatrix >> multiplication_matrix.matrixIn[1]

    # Now connect outputs
    multiplication_matrix.matrixSum >> pole_matrix.inMatrix
    pole_matrix.output >> blend_colors.color1
    blend_colors.output >> ik_handle.poleVector
    control.poleVectorWeight >> blend_colors.blender

    return [blend_colors, pole_matrix, multiplication_matrix, inverse_matrix, compose_matrix, world_point]


def calculatePoleVectorTransform(start_transform, mid_transform, end_transform, scale=0.5):
    """
    Props to Greg Hendrix for walking through the math: https://vimeo.com/240328348

    Args:
        start_transform (PyNode): Start of the joint chain

        mid_transform (PyNode): Mid joint of the chain.

        end_transform (PyNode): End joint of the chain.

        scale (float): How far away should the pole vector position be compared to the chain length.

    Returns:
        (list): Transform of pole vector control. Translation as first index, rotation as second, scale as third.
    """

    zero_vector = pm.dt.Vector(0, 0, 0)
    if mid_transform.r.get() == zero_vector:
        if mid_transform.hasAttr('orientJoint'):
            if mid_transform.orientJoint.get() == zero_vector:
                return pm.dt.Vector(pm.xform(mid_transform, q=True, ws=True, rp=True))
        else:
            return pm.dt.Vector(pm.xform(mid_transform, q=True, ws=True, rp=True))

    start = pm.dt.Vector(pm.xform(start_transform, q=True, ws=True, rp=True))
    mid = pm.dt.Vector(pm.xform(mid_transform, q=True, ws=True, rp=True))
    end = pm.dt.Vector(pm.xform(end_transform, q=True, ws=True, rp=True))

    start_to_end = end - start
    start_to_mid = mid - start

    start_to_end_length = start_to_end.length()
    mid_scale = start_to_end.dot(start_to_mid) / (start_to_end_length * start_to_end_length)
    mid_chain_point = start + start_to_end * mid_scale

    chain_length = (mid - start).length() + (end - mid).length()
    translation = (mid - mid_chain_point).normal() * chain_length * scale + mid
    rotation = pipermath.getAimRotation(mid_chain_point, translation)
    single_scale = mid.radius.get() if isinstance(mid, pm.nodetypes.Transform) and mid.hasAttr('radius') else 1
    scale = [single_scale, single_scale, single_scale]

    return [translation, rotation, scale]


def getOrientAxis(start, target):
    """
    Gets the closest axis object is using to pointing to target.
    Thanks to Charles Wardlaw for helping script it.

    Args:
        start (PyNode): transform object to find axis of.

        target (string or PyNode): transform object that axis is pointing to.

    Returns:
        (tuple): Closest axis
    """
    closest_axis = None
    closest_dot_result = 0.0

    aim_direction = pipermath.getDirection(start, target)
    world_matrix = start.worldMatrix.get()

    for axis in pcfg.axes:
        axis_vector = pm.dt.Vector(axis)  # the world axis
        axis_vector = axis_vector * world_matrix  # turning the world axis to local start object axis
        dot = axis_vector.dot(aim_direction)  # dot product tells us how aligned the axis is with the aim direction
        if dot > closest_dot_result:
            closest_dot_result = dot
            closest_axis = axis

    return closest_axis


def createJointAtPivot():
    """
    Creates a joint at the current manipulator pivot point.
    """
    shift_held = myu.isShiftHeld()
    ctrl_held = myu.isCtrlHeld()
    alt_held = myu.isAltHeld()

    selection = pm.selected()
    if shift_held:
        for transform in selection:
            pm.select(cl=True)
            name = transform.nodeName() if alt_held else ''
            joint = pm.joint(p=myu.getManipulatorPosition(transform), n=name)
            if ctrl_held:
                constraint = pm.orientConstraint(transform, joint, mo=False)
                pm.delete(constraint)
    else:
        name = selection[-1].nodeName() if alt_held else ''
        pm.joint(p=myu.getManipulatorPosition(selection), n=name)


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
