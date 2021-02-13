#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.mayapy.pipermath as pipermath
import piper_config as pcfg
import piper.mayapy.util as myu
import piper.mayapy.rig.core as rig
import piper.mayapy.rig.createshape as createshape


def create(transform,
           shape=createshape.circle,
           name='control',
           axis='y',
           color='pink',
           scale=1.0,
           matrix_offset=True,
           group_offset=False,
           parent=None,
           *args,
           **kwargs):
    """
    Creates a control with the given shape, color, orientation, offset, and parent.

    Args:
        transform (pm.nodetypes.Transform): Transform to match control onto.

        shape (method): Creates control curve.

        name (string): Name of control.

        axis (string): Orientation for control.

        color (string): Color of curve.

        scale (float): Scale to multiply by joint radius.

        matrix_offset (boolean): If True, will zero out transform and place it in parent Offset Matrix attribute.

        group_offset (boolean): If True, will create an empty group that will hold offset values.

        parent (pm.nodetypes.Transform): If given, will parent control or group under given parent.

        *args (Any): Used in shape method.

        **kwargs (Any): Used in shape method.

    Returns:
        (list): control made as first index and group made as second index if group was made, else False.
    """
    joint_radius = transform.radius.get() if transform.hasAttr('radius') else 1
    joint_radius *= scale
    control = shape(name=name + pcfg.control_suffix, *args, **kwargs)
    control.s.set((joint_radius, joint_radius, joint_radius))
    createshape.color(control, color)
    pm.delete(control, ch=True)  # delete history

    if axis == 'x':
        control.rz.set(control.rz.get() + 90)
    if axis == 'nx':
        control.rz.set(control.rz.get() - 90)
    elif axis == 'z':
        control.rx.set(control.rx.get() + 90)
    elif axis == 'nz':
        control.rx.set(control.rx.get() - 90)

    myu.freezeTransformations(control)

    if parent:
        if matrix_offset:
            pm.matchTransform(control, transform)
            pm.parent(control, parent)
            rig.transformToOffsetMatrix(control)
        elif group_offset:
            group_offset = pm.group(em=True, name=name + pcfg.offset_suffix)
            pm.matchTransform(group_offset, transform)
            pm.parent(control, group_offset)
            pipermath.zeroOut(control)
            rig.parentMatrixConstraint(parent, group_offset, offset=True)
        else:
            pm.matchTransform(control, transform)
            pm.parent(control, parent)
    else:
        if matrix_offset:
            control.offsetParentMatrix.set(transform.worldMatrix.get())
        elif group_offset:
            group_offset = pm.group(em=True, name=name + pcfg.offset_suffix)
            pm.matchTransform(group_offset, transform)
            pm.parent(control, group_offset)
            pipermath.zeroOut(control)
        else:
            pm.matchTransform(control, transform)

    rig.nonKeyable(control.visibility)
    return control, group_offset
