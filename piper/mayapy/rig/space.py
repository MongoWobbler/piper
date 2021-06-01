#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.mayamath as mayamath
import piper.mayapy.attribute as attribute
import piper.mayapy.pipernode as pipernode

from . import xform
from . import switcher


def _connect(transform, target, space, orient_matrix=None):
    """
    Convenience method for connecting the use transforms attributes from the piper space to matrix blend target.

    Args:
        transform (pm.nodetypes.Transform): Transform connect use transform from onto target.

        target (pm.Attribute): Attribute with use transform attributes.

        space (pm.Attribute): Space attribute that will drive the target weight.
    """
    space >> target.weight
    transform.attr(pcfg.space_use_translate) >> target.useTranslate
    transform.attr(pcfg.space_use_rotate) >> target.useRotate
    transform.attr(pcfg.space_use_scale) >> target.useScale

    if orient_matrix:
        transform.attr(pcfg.space_use_orient) >> orient_matrix.useOrient


def exists(transform):
    """
    Gets whether the given transform has spaces or not.

    Args:
        transform (pm.nodetypes.Transform): Transform to check if has spaces.

    Returns:
        (boolean): True if has a spaces blender connected, False if it does not.
    """
    matrix_blend = attribute.getMessagedSpacesBlender(transform)
    return bool(matrix_blend)


def getAll(transform, cast=False):
    """
    Gets all the piper made spaces. Uses names stored in a string attribute to get these spaces.
    Will return empty list if no spaces attributes found.

    Args:
        transform (pm.nodetypes.Transform): Transform to get spaces from.

        cast (boolean): If True, will cast each value of the attribute found into a PyNode.

    Returns:
        (list): All space attributes given transform has, if any.
    """
    spaces = None

    if transform.hasAttr(pcfg.spaces_name):
        spaces = transform.attr(pcfg.spaces_name).get()

    if spaces:
        spaces = spaces.split(', ')
        return [pm.PyNode(space_name) for space_name in spaces] if cast else spaces
    else:
        return []


def getCurrent(transform):
    """
    Gets the space the transform is currently on.

    Args:
        transform (pm.nodetypes.Transform): Transform to get current space it is on.

    Returns:
        (string): Name of space given transform is currently on.
    """
    spaces = getAll(transform)
    for space_attribute in spaces:
        if transform.attr(space_attribute).get():
            return space_attribute

    return None


def create(spaces=None, transform=None, direct=False, warn=True):
    """
    Creates the given spaces on the given transform.

    Args:
        spaces (iterator): A bunch of pm.nodetypes.Transform(s) that will drive the given transform.

        transform (pm.nodetypes.Transform): Transform to have ability to switch between given spaces.

        direct (boolean): If False, will plug output matrix into offsetParentMatrix, else direct connection.

        warn (boolean): If True, will warn about any existing spaces on given transform that clash with given spaces.

    Returns:
          (list): Name of space attribute(s) made.
    """
    if not spaces and not transform:
        selected = pm.selected()
        spaces = selected[:-1]
        transform = selected[-1]

        if len(selected) < 2:
            pm.error('Not enough transforms selected!')

    orient_matrix = None
    space_attributes = []
    parent = transform.getParent()
    transform_name = transform.name(stripNamespace=True)
    matrix_blend = attribute.getMessagedSpacesBlender(transform)

    if not matrix_blend:
        # create and hook up matrix blend
        matrix_blend = pm.createNode('blendMatrix', n=transform_name + pcfg.space_blend_matrix_suffix)
        attribute.addSpaceMessage(matrix_blend, transform)
        target = matrix_blend.attr('target[0]')

        if transform.offsetParentMatrix.isDestination():
            plug_source = transform.offsetParentMatrix.connections(scn=True, plugs=True, destination=False)[0]
            plug_source >> matrix_blend.inputMatrix
        else:
            offset_matrix = transform.offsetParentMatrix.get()
            matrix_blend.inputMatrix.set(offset_matrix)

        if direct:
            multiply = pm.createNode('multMatrix', n=transform_name + '_blendOffset_MM')
            multiply.matrixIn[0].set(transform.matrix.get())
            matrix_blend.outputMatrix >> multiply.matrixIn[1]

            decompose = pm.createNode('decomposeMatrix', n=transform_name + '_blend_DM')
            multiply.matrixSum >> decompose.inputMatrix
            decompose.outputTranslate >> transform.translate
            decompose.outputRotate >> transform.rotate
            decompose.outputScale >> transform.scale
        else:
            matrix_blend.outputMatrix >> transform.offsetParentMatrix

        # counter drive parent to create a world space
        if parent:
            parent.worldInverseMatrix >> target.targetMatrix

        # create attributes on transform and add world space by default
        attribute.addSeparator(transform)
        transform.addAttr(pcfg.space_use_translate, at='bool', dv=1, k=True)
        transform.addAttr(pcfg.space_use_rotate, at='bool', dv=1, k=True)
        transform.addAttr(pcfg.space_use_orient, at='bool', dv=0, k=True)
        transform.addAttr(pcfg.space_use_scale, at='bool', dv=1, k=True)
        transform.addAttr(pcfg.spaces_name, dt='string', k=False, h=True, s=True)
        transform.addAttr(pcfg.space_world_name, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)
        _connect(transform, target, transform.attr(pcfg.space_world_name))
        space_attributes.append(pcfg.space_world_name)

    # used for orient
    has_input_matrix = matrix_blend.inputMatrix.isDestination()
    position = matrix_blend.inputMatrix.connections(scn=True, p=True, d=False)[0] if has_input_matrix else None

    for space in spaces:
        space_name = space.name(stripNamespace=True)
        space_attribute = space_name + pcfg.space_suffix

        if transform.hasAttr(space_attribute):
            pm.warning(space_attribute + ' already exists on ' + transform_name) if warn else None
            continue

        transform.addAttr(space_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)
        target = attribute.getNextAvailableTarget(matrix_blend, 1)

        # make multiply matrix node and hook it up
        offset = transform.parentMatrix.get() * space.worldInverseMatrix.get()
        multiply = pm.createNode('multMatrix', n='space_{}_To_{}_MM'.format(transform_name, space_name))
        multiply.matrixIn[0].set(offset)
        space.worldMatrix >> multiply.matrixIn[1]
        target_plug = multiply.matrixSum

        # counter drive parent
        if parent:
            parent.worldInverseMatrix >> multiply.matrixIn[2]

        # if has input matrix, then create an orient space
        if has_input_matrix:
            orient_name = '{}_X_{}_OM'.format(transform_name, space_name)
            orient_matrix = pipernode.createOrientMatrix(position, multiply.matrixSum, name=orient_name)
            target_plug = orient_matrix.output

        target_plug >> target.targetMatrix
        _connect(transform, target, transform.attr(space_attribute), orient_matrix)
        space_attributes.append(space_attribute)

    # update the spaces attribute
    old_spaces = getAll(transform)
    updated_spaces = old_spaces + space_attributes
    transform.attr(pcfg.spaces_name).set(', '.join(updated_spaces))
    return space_attributes


def switch(transform, new_space=None, t=True, r=True, o=False, s=True, key=False):
    """
    Switches the given transform to the given new_space while maintaining the world transform of the given transform.
    Choose to switch driving translate, rotate, or scale attributes on or off too.

    Args:
        transform (pm.nodetypes.Transform):

        new_space (string or None): Name of space attribute to switch to.

        t (boolean): If True, space will affect translate values.

        r (boolean): If True, space will affect rotate values.

        o (boolean): If True, space will affect orient values.

        s (boolean): If True, space will affect scale values.

        key (boolean): If True, will set a key at the previous frame on the transform.
    """
    if key:
        current_frame = pm.currentTime(q=True)
        pm.setKeyframe(transform, time=current_frame - 1)

    position = transform.worldMatrix.get()
    transform.useTranslate.set(t)
    transform.useRotate.set(r)
    transform.useOrient.set(o)
    transform.useScale.set(s)
    spaces = getAll(transform)
    [transform.attr(space_attribute).set(0) for space_attribute in spaces]

    if new_space:
        transform.attr(new_space).set(1)

    pm.xform(transform, ws=True, m=position)


def switchFKIK(switcher_ctrl, key=True, match_only=False):
    """
    Moves the FK or IK controls to the transform of the other based on the FK_IK attribute on the switcher control.

    Args:
        switcher_ctrl (pm.nodetypes.Transform): Switcher control with attributes that hold all the FK IK information.

        key (boolean): If True, will set a key at the previous frame.

        match_only (boolean): If True, will match the FK/IK space, but will not switch the FK_IK attribute.
    """
    # check whether given node has all needed attributes to perform a switch, raise error if it does not.
    switcher_ctrl, transforms, fk_controls, ik_controls, reverses, fk_ik_value = switcher.getAllData(switcher_ctrl)
    current_frame = pm.currentTime(q=True)
    reverse_control_transforms = {}

    if not (fk_ik_value == 1 or fk_ik_value == 0):
        pm.warning('FK IK attribute = {}, which is not a whole number, matching might be off!'.format(str(fk_ik_value)))

    # FK is being used, move IK to original joints
    if fk_ik_value <= 0.5:
        new_fk_ik_value = 1
        mid = pcu.getMedian(transforms)

        to_key = ik_controls + [switcher_ctrl] + reverses

        # if foot has banker attribute, set to banker's rotations to 0 and add it to key list
        if ik_controls[-1].hasAttr(pcfg.banker_attribute):
            banker_control = pm.PyNode(ik_controls[-1].attr(pcfg.banker_attribute).get())
            [banker_control.attr(r).set(0) for r in ['rx', 'ry', 'rz'] if not banker_control.attr(r).isLocked()]
            to_key.append(banker_control)

        if key:
            pm.setKeyframe(to_key, time=current_frame - 1)

        ik_controls[-1].volumetric.set(False)

        [reverse.r.set(0, 0, 0) for reverse in reverses]
        for transform, ik_control in reversed(list(zip(transforms, ik_controls))):

            # middle transform
            if transform == mid:
                translate, _, _, straight = xform.calculatePoleVector(transforms[0], mid, transforms[-1], scale=2)
                ik_control.t.set(0, 0, 0) if straight else pm.xform(ik_control, ws=True, t=translate)

            # end
            else:
                matrix = transform.worldMatrix.get()
                pm.xform(ik_control, ws=True, m=matrix)

    # IK is being used, move FK to original joints
    else:
        new_fk_ik_value = 0

        # storing reverse control transforms that will need to be set after matching IK chain
        for reverse in reverses:
            negated_ctrl = attribute.getMessagedReverseTarget(reverse)
            driven = attribute.getMessagedTarget(negated_ctrl)
            reverse_control_transforms[negated_ctrl] = driven.worldMatrix.get()

        if key:
            pm.setKeyframe(fk_controls + [switcher_ctrl] + list(reverse_control_transforms), time=current_frame - 1)

        # set the inner controls to their local space
        inner_start_index = int(len(fk_controls)/2)
        for inner_ctrl in fk_controls[inner_start_index:]:
            switch(inner_ctrl)
            mayamath.zeroOut(inner_ctrl)

        # only match the real controls, not the inner ones
        for transform, fk_control in zip(transforms, fk_controls[:inner_start_index]):
            matrix = transform.worldMatrix.get()
            fk_control.volumetric.set(0)
            pm.xform(fk_control, ws=True, m=matrix)

    if not match_only:
        switcher_ctrl.attr(pcfg.fk_ik_attribute).set(new_fk_ik_value)

        if reverse_control_transforms:
            {pm.xform(transform, ws=True, m=matrix) for transform, matrix in reverse_control_transforms.items()}


def resetDynamicPivot(pivot_control, key=True, rest=False):
    """
    Resets the position of the dynamic pivot. Maintains world position of control driven by pivot.

    Args:
        pivot_control (pm.nodetypes.Transform): Pivot control that needs to be reset to zero position.

        key (boolean): If True, will key the pivot and parent control on the previous frame.

        rest (boolean): If True, will move pivot to the rest position.
    """
    parent = pivot_control.getParent()
    matrix = parent.worldMatrix.get()
    rest_matrix = pm.PyNode(pivot_control.attr(pcfg.dynamic_pivot_rest).get()).worldMatrix.get()

    if key:
        current_frame = pm.currentTime(q=True)
        pm.setKeyframe(pivot_control, time=current_frame - 1)
        pm.setKeyframe(parent, time=current_frame - 1)

    pm.xform(pivot_control, ws=True, m=rest_matrix) if rest else mayamath.zeroOut(pivot_control)
    pm.xform(parent, ws=True, m=matrix)
    pm.xform(parent, ws=True, m=matrix)  # called twice because Maya is stupid
