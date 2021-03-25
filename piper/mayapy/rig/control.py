#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.util as myu
import piper.mayapy.pipermath as pipermath
import piper.mayapy.attribute as attribute

from . import xform
from . import curve


def calculateSize(joint, scale=1):
    """
    Calculates the size a control should be based on verts affected bounds or joint radius.

    Args:
        joint (pm.nodetypes.Transform): Uses it's affecting verts or radius to calculate size.

        scale (float): Number to scale result by.

    Returns:
        (list): X, Y, Z Scale.
    """
    skin_clusters = set(joint.connections(type='skinCluster'))  # remove duplicates cause Maya
    if skin_clusters:
        distance_sum = 0
        pm.select(cl=True)

        # select the verts joint is affecting and get the bounds all those verts make
        [pm.skinCluster(skin, selectInfluenceVerts=joint, edit=True, ats=True) for skin in skin_clusters]
        bounds = pm.exactWorldBoundingBox(calculateExactly=True, ii=False)
        pm.select(cl=True)

        # calculate the average distance of the bounds in each axis and use that as the size
        for i in range(3):
            distance_sum += abs(bounds[i] - bounds[i + 3])

        average_distance = (distance_sum / 3.0) * scale * 0.9  # scaling down slightly
        return average_distance, average_distance, average_distance

    elif joint.hasAttr('radius'):
        radius = joint.radius.get() * scale
        return radius, radius, radius

    else:
        return scale, scale, scale


def create(transform,
           shape=curve.circle,
           name='control',
           axis='y',
           color='pink',
           scale=1.0,
           matrix_offset=True,
           group_offset=False,
           parent=None,
           size=None,
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

        size (list): If given, will use this as the size to set the scale of the control

        *args (Any): Used in shape method.

        **kwargs (Any): Used in shape method.

    Returns:
        (list): control made as first index and group made as second index if group was made, else False.
    """
    control = shape(name=name + pcfg.control_suffix, *args, **kwargs)
    curve.color(control, color)

    if not size:
        size = calculateSize(transform)

    size = [xyz * scale for xyz in size]
    control.s.set(size)

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
            xform.toOffsetMatrix(control)
        elif group_offset:
            group_offset = pm.group(em=True, name=name + pcfg.offset_suffix)
            pm.matchTransform(group_offset, transform)
            pm.parent(control, group_offset)
            pipermath.zeroOut(control)
            xform.parentMatrixConstraint(parent, group_offset, offset=True)
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

    attribute.nonKeyable(control.visibility)
    return control, group_offset


def getSwitcher(transform):
    """
    Gets the switcher if the given transform has an fk_ik attribute.

    Args:
        transform (pm.nodetypes.Transform): Transform to get switcher control of.

    Returns:
        (pm.nodetypes.Transform): Switcher control that holds real fk_ik attribute.
    """
    if transform.hasAttr(pcfg.proxy_fk_ik):
        real_switcher = transform.attr(pcfg.proxy_fk_ik).connections()

        if not real_switcher:
            pm.error(transform.nodeName() + ' has proxy attribute but is not connected!')

        return real_switcher[0]

    elif transform.hasAttr(pcfg.fk_ik_attribute):
        return transform

    else:
        pm.error(transform.nodeName() + ' is not connected to a switcher!')
