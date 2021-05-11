#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.core.pipermath as pipermath
import piper.mayapy.util as myu
import piper.mayapy.attribute as attribute

from . import xform
from . import curve


def getAll(namespace=''):
    """
    Gets all the controls found in the control set with the given namespace.

    Args:
        namespace (string): Name of namespace to append as prefix to the control set name.

    Returns:
        (list): All controls
    """
    control_set = namespace + ':' + pcfg.control_set if namespace else pcfg.control_set

    if not pm.objExists(control_set):
        return []

    control_set = pm.PyNode(control_set)
    controls = control_set.members(flatten=True)
    return controls


def calculateSize(joint, scale=1, use_skins=True, try_root=True):
    """
    Calculates the size a control should be based on verts affected bounds or joint radius.

    Args:
        joint (pm.nodetypes.Transform): Uses it's affecting verts or radius to calculate size.

        scale (float): Number to scale result by.

        use_skins (boolean): If True, will try to use the bounding box of influencing skins to calculate size.

        try_root (boolean): If True, will try to get the average length of the vertex positions of the meshes

    Returns:
        (list): X, Y, Z Scale.
    """
    skin_clusters = joint.future(type='skinCluster')
    joint_name = joint.name(stripNamespace=True)

    if try_root and joint_name == pcfg.root_joint_name:
        skins = {skin for bone in joint.getChildren(ad=True) for skin in bone.future(type='skinCluster')}
        meshes = {geo.getParent() for skin in skins for geo in skin.getGeometry()}

        # no mesh is not bound
        if not meshes:
            return calculateSize(joint, scale, use_skins=False, try_root=False)

        length = 0
        positions = []

        for mesh in meshes:
            positions += myu.getVertexPositions(mesh)

        for position in positions:
            projection = [position[0], 0, position[2]]  # project onto XZ plane
            length += pipermath.magnitude(projection)

        average_length = length / len(positions)
        return average_length, average_length, average_length

    elif use_skins and skin_clusters:
        distance_sum = 0
        pm.select(cl=True)

        # select the verts joint is affecting and get the bounds all those verts make
        [pm.skinCluster(skin, selectInfluenceVerts=joint, edit=True, ats=True) for skin in skin_clusters]
        selected = pm.selected()
        selected = list(filter(lambda x: not isinstance(x, pm.nodetypes.Mesh), selected))

        # if mesh is selected, its because joint is not influencing any verts, so call itself without doing skins calc
        if not selected:
            return calculateSize(joint, scale, use_skins=False)

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

        parent (pm.nodetypes.Transform or None): If given, will parent control or group under given parent.

        size (list): If given, will use this as the size to set the scale of the control

        *args (Any): Used in shape method.

        **kwargs (Any): Used in shape method.

    Returns:
        (pm.nodetypes.Transform): Control made.
    """
    control = shape(name=name + pcfg.control_suffix, *args, **kwargs)
    curve.color(control, color)
    # pm.controller(control)

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
        else:
            pm.matchTransform(control, transform)
            pm.parent(control, parent)
    else:
        if matrix_offset:
            control.offsetParentMatrix.set(transform.worldMatrix.get())
        else:
            pm.matchTransform(control, transform)

    attribute.nonKeyable(control.visibility)
    return control
