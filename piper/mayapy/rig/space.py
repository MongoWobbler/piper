#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.attribute as attribute
import piper.mayapy.pipermath as pipermath

import xform as xform
import control as control


def _connect(transform, target, space):
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


def getAll(transform, attribute_name=pcfg.spaces_name, cast=False):
    """
    Gets all the piper made spaces. Uses names stored in a string attribute to get these spaces.
    Will return empty list if no spaces attributes found.

    Args:
        transform (pm.nodetypes.Transform): Transform to get spaces from.

        attribute_name (string): The name of the attribute to get the spaces from.

        cast (boolean): If True, will cast each value of the attribute found into a PyNode.

    Returns:
        (list): All space attributes given transform has, if any.
    """
    attributes = None

    if transform.hasAttr(attribute_name):
        attributes = transform.attr(attribute_name).get()

    if attributes:
        attributes = attributes.split(', ')
        return [pm.PyNode(attribute_name) for attribute_name in attributes] if cast else attributes
    else:
        return []


def getFkIkAttributes(transform):
    """
    Check whether given node has all needed attributes to perform a switch, raise error if it does not.

    Args:
        transform (pm.nodetypes.Transform): Switcher control with attributes that hold all the FK IK information.

    Returns:
        (list): Transforms, FK controls, IK controls, and fk_ik attribute value. Transforms and controls are in order.
    """
    switcher = control.getSwitcher(transform)
    attribute.exists(switcher, pcfg.switcher_attributes, error=True)
    transforms = getAll(switcher, pcfg.switcher_transforms, cast=True)
    fk_controls = getAll(switcher, pcfg.switcher_fk, cast=True)
    ik_controls = getAll(switcher, pcfg.switcher_ik, cast=True)
    fk_ik_value = switcher.attr(pcfg.fk_ik_attribute).get()

    return switcher, transforms, fk_controls, ik_controls, fk_ik_value


def create(spaces, transform):
    """
    Creates the given spaces on the given transform.

    Args:
        spaces (list): A bunch of pm.nodetypes.Transform(s) that will drive the given transform.

        transform (pm.nodetypes.Transform): Transform to have ability to switch between given spaces.

    Returns:
          (list): Name of space attribute(s) made.
    """
    space_attributes = []
    parent = transform.getParent()
    transform_name = transform.nodeName()
    matrix_blend = transform.offsetParentMatrix.listConnections()
    has_spaces = matrix_blend and transform.hasAttr(pcfg.space_world_name)

    if has_spaces:
        # define matrix blend from the matrix plug
        matrix_blend = matrix_blend[0]

        if matrix_blend.nodeType() != 'blendMatrix':
            pm.error(transform.nodeName() + ' has wrong type: ' + matrix_blend.nodeName() + ' in offsetParentMatrix')
    else:
        # create and hook up matrix blend
        matrix_blend = pm.createNode('blendMatrix', n=transform_name + pcfg.space_blend_matrix_suffix)
        target = matrix_blend.attr('target[0]')
        offset_matrix = transform.offsetParentMatrix.get()
        matrix_blend.inputMatrix.set(offset_matrix)
        matrix_blend.outputMatrix >> transform.offsetParentMatrix

        # counter drive parent to create a world space
        if parent:
            parent.worldInverseMatrix >> target.targetMatrix

        # create attributes on transform and add world space by default
        attribute.addSeparator(transform)
        transform.addAttr(pcfg.space_use_translate, at='bool', dv=1, k=True)
        transform.addAttr(pcfg.space_use_rotate, at='bool', dv=1, k=True)
        transform.addAttr(pcfg.space_use_scale, at='bool', dv=1, k=True)
        transform.addAttr(pcfg.spaces_name, dt='string', k=False, h=True, s=True)
        transform.addAttr(pcfg.space_world_name, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)
        _connect(transform, target, transform.attr(pcfg.space_world_name))
        space_attributes.append(pcfg.space_world_name)

    for space in spaces:
        space_name = space.nodeName()
        space_attribute = space_name + pcfg.space_suffix
        transform.addAttr(space_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)
        target = attribute.getNextAvailableTarget(matrix_blend, 1)

        # make multiply matrix node and hook it up
        offset = transform.parentMatrix.get() * space.worldInverseMatrix.get()
        multiply = pm.createNode('multMatrix', n='space_{}_To_{}_multMatrix'.format(transform_name, space_name))
        multiply.matrixIn[0].set(offset)
        space.worldMatrix >> multiply.matrixIn[1]

        # counter drive parent
        if parent:
            parent.worldInverseMatrix >> multiply.matrixIn[2]

        multiply.matrixSum >> target.targetMatrix
        _connect(transform, target, transform.attr(space_attribute))
        space_attributes.append(space_attribute)

    # update the spaces attribute
    old_spaces = getAll(transform)
    updated_spaces = old_spaces + space_attributes
    transform.attr(pcfg.spaces_name).set(', '.join(updated_spaces))
    return space_attributes


def switch(transform, new_space=None, t=True, r=True, s=True):
    """
    Switches the given transform to the given new_space while maintaining the world transform of the given transform.
    Choose to switch driving translate, rotate, or scale attributes on or off too.

    Args:
        transform (pm.nodetypes.Transform):

        new_space (string): Name of space attribute to switch to.

        t (boolean): If True, space will affect translate values.

        r (boolean): If True, space will affect rotate values.

        s (boolean): If True, space will affect scale values.
    """
    position = transform.worldMatrix.get()
    transform.useTranslate.set(t)
    transform.useRotate.set(r)
    transform.useScale.set(s)
    spaces = getAll(transform)
    [transform.attr(space_attribute).set(0) for space_attribute in spaces]

    if new_space:
        transform.attr(new_space).set(1)

    pm.xform(transform, ws=True, m=position)


def switchFKIK(switcher, key=True, match_only=False):
    """
    Moves the FK or IK controls to the transform of the other based on the FK_IK attribute on the switcher control.

    Args:
        switcher (pm.nodetypes.Transform): Switcher control with attributes that hold all the FK IK information.

        key (boolean): If True, will set a key at the previous frame.

        match_only (boolean): If True, will match the FK/IK space, but will not switch the FK_IK attribute.
    """
    # check whether given node has all needed attributes to perform a switch, raise error if it does not.
    switcher, transforms, fk_controls, ik_controls, fk_ik_value = getFkIkAttributes(switcher)
    current_frame = pm.currentTime(q=True)

    if not (fk_ik_value == 1 or fk_ik_value == 0):
        pm.warning('FK IK attribute = {}, which is not a whole number, matching might be off!'.format(str(fk_ik_value)))

    # FK is being used, move IK to original joints
    if fk_ik_value <= 0.5:
        new_fk_ik_value = 1
        mid = pcu.getMedian(transforms)
        to_key = ik_controls + [switcher]

        # if foot has banker attribute, set to banker's rotations to 0 and add it to key list
        if ik_controls[-1].hasAttr(pcfg.banker_attribute):
            banker_control = pm.PyNode(ik_controls[-1].attr(pcfg.banker_attribute).get())
            [banker_control.attr(r).set(0) for r in ['rx', 'ry', 'rz'] if not banker_control.attr(r).isLocked()]
            to_key.append(banker_control)

        if key:
            pm.setKeyframe(to_key, time=current_frame - 1)

        for transform, ik_control in zip(transforms, ik_controls[2:]):

            # start of chain
            if transform == transforms[0]:
                translate = pm.xform(transform, q=True, ws=True, t=True)
                scale = pm.xform(transform, q=True, ws=True, s=True)
                pm.xform(ik_control, ws=True, t=translate)
                pm.xform(ik_controls[0], ws=True, s=scale)

            # middle transform
            elif transform == mid:
                translate, _, _ = xform.calculatePoleVector(transforms[0], mid, transforms[-1], scale=2)
                pm.xform(ik_control, ws=True, t=translate)

            else:
                matrix = transform.worldMatrix.get()
                pm.xform(ik_control, ws=True, m=matrix)

    # IK is being used, move FK to original joints
    else:
        new_fk_ik_value = 0

        if key:
            pm.setKeyframe(fk_controls + [switcher], time=current_frame - 1)

        # set the inner controls to their local space
        inner_start_index = len(fk_controls)/2
        for inner_ctrl in fk_controls[inner_start_index:]:
            switch(inner_ctrl)
            pipermath.zeroOut(inner_ctrl)

        # only match the real controls, not the inner ones
        for transform, fk_control in zip(transforms, fk_controls[:inner_start_index]):
            matrix = transform.worldMatrix.get()
            pm.xform(fk_control, ws=True, m=matrix)

    if not match_only:
        switcher.attr(pcfg.fk_ik_attribute).set(new_fk_ik_value)


def resetDynamicPivot(pivot_control, key=True):
    """
    Resets the position of the dynamic pivot. Maintains world position of control driven by pivot.

    Args:
        pivot_control (pm.nodetypes.Transform): Pivot control that needs to be reset to zero position.

        key (boolean): If True, will key the pivot and parent control on the previous frame.
    """
    parent = pivot_control.getParent()
    matrix = parent.worldMatrix.get()

    if key:
        current_frame = pm.currentTime(q=True)
        pm.setKeyframe(pivot_control, time=current_frame - 1)
        pm.setKeyframe(parent, time=current_frame - 1)

    pipermath.zeroOut(pivot_control)
    pm.xform(parent, ws=True, m=matrix)
    parent.r.set(0, 0, 0)
