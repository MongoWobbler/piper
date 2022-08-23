#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.config.maya as mcfg
import piper.core.pipermath as pipermath

import piper.mayapy.mesh as mesh
import piper.mayapy.attribute as attribute

from . import bone
from . import xform
from . import curve


def getTag(node):
    """
    Gets the tag associated with the given node, if none given a tag is created.

    Args:
        node (pm.nodetypes.DependNode): node to find tag of.

    Returns:
        (pm.nodetypes.Controller): Tag associated with given nodes.
    """
    tag = node.message.connections(scn=False, d=True, type='controller')

    if not tag:
        pm.controller(node)  # make controller tag if none found
        return getTag(node)  # pm.controller does not return anything, so use getTag to get the node

    return tag[0]


def getSet(name):
    """
    Convenience method for getting a control set if already exists, else creates ones with given name.

    Args:
        name (string): Name of control set to check for or make.

    Returns:
        (SelectionSet): Set that can hold nodes used for organizing outliner.
    """
    return pm.PyNode(name) if pm.objExists(name) else pm.sets(n=name)


def tagAsControllerParent(child, parent):
    """
    Tags the given child as the child of the given parent in the controller tag.

    Args:
        child (pm.nodetypes.DependNode): Node to become a child of given parent in controller tag.

        parent (pm.nodetypes.DependNode): Node to become parent of given child in controller tag.

    Returns:
        (list): Child tag as first index, parent tag as second index.
    """
    child_tag = getTag(child)
    parent_tag = getTag(parent)
    index = attribute.getNextAvailableIndex(parent_tag, 'children[{}]')
    children_plug = parent_tag.attr('children[{}]'.format(str(index)))

    parent_tag.prepopulate >> child_tag.prepopulate
    child_tag.parent >> children_plug

    return child_tag, parent_tag


def getAll(namespaces=None):
    """
    Gets all the controls found in the control set with the given namespace.

    Args:
        namespaces (Iterable): Names of namespace to append as prefix to the control set name.

    Returns:
        (list): All controls sorted.
    """
    if namespaces:
        sets = [pm.PyNode(n + ':' + mcfg.control_set) for n in namespaces if pm.objExists(n + ':' + mcfg.control_set)]
    else:
        sets = pm.ls(mcfg.control_set, recursive=True)

    controls = {ctrl for control_set in sets for ctrl in control_set.members(flatten=True)}
    controls = list(controls)
    controls.sort()
    return controls


def getAllOfType(set_name):
    """
    Gets all the controls of the given set name found in scene.

    Returns:
        (set): All inner controls.
    """
    exists = pm.objExists(set_name) or pm.objExists('*:' + set_name)
    if not exists:
        return set()

    control_sets = pm.ls(set_name, recursive=True)
    return {ctrl for control_set in control_sets for ctrl in control_set.members()}


def getAllInner():
    """
    Convenience method for finding all the inner controls found in scene.

    Returns:
        (set): All inner controls.
    """
    return getAllOfType(mcfg.inner_controls_set)


def getAllBendy():
    """
    Convenience method for finding all the bendy controls found in scene.

    Returns:
        (set): All inner controls.
    """
    return getAllOfType(mcfg.bendy_control_set)


def replaceShapes(path, controls=None, remove=True):
    """
    Replaces all the the given control shapes with controls of the same name in the given path file.
    If no controls given, will use selected. If none selected, will use all controls in the scene.

    Args:
        path (string): Path to Maya file to reference in to get new control shapes.

        controls (list): Controls to replace shapes of.

        remove (boolean): If True, will remove the reference after replacing the shapes.

    Returns:
        (list): New shapes created.
    """
    if not controls:
        controls = pm.selected()

    if not controls:
        controls = getAll()

    shapes = []
    reference = pm.createReference(path, namespace=mcfg.temp_namespace)

    for target in controls:
        source_name = mcfg.temp_namespace + ':' + target.name()

        if not pm.objExists(source_name):
            continue

        source = pm.PyNode(source_name)
        replaced = curve.copy(source, target)
        shapes.append(replaced)

    if remove:
        reference.remove()

    pm.displayInfo('Replaced shapes from ' + path)
    return shapes


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

    if try_root and joint_name == mcfg.root_joint_name:
        skins = {skin for bone in joint.getChildren(ad=True) for skin in bone.future(type='skinCluster')}
        meshes = {geo.getParent() for skin in skins for geo in skin.getGeometry()}

        # no mesh is not bound
        if not meshes:
            return calculateSize(joint, scale, use_skins=False, try_root=False)

        length = 0
        positions = []

        for static_mesh in meshes:
            positions += mesh.getVertexPositions(static_mesh)

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
           joint=False,
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

        joint (boolean): If True, will create the control as a joint instead of a regular transform.

        *args (Any): Used in shape method.

        **kwargs (Any): Used in shape method.

    Returns:
        (pm.nodetypes.Transform): Control made.
    """
    name = name + mcfg.control_suffix
    kwargs['name'] = name
    control = bone.createShaped(shape, *args, **kwargs) if joint else shape(*args, **kwargs)
    curve.color(control, color)
    pm.controller(control)

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

    attribute.freezeTransformations(control)

    if parent:
        if matrix_offset:
            pm.matchTransform(control, transform)
            pm.parent(control, parent)
            xform.toOffsetMatrix(control)
        else:
            pm.matchTransform(control, transform)
            pm.parent(control, parent)

        tagAsControllerParent(control, parent)
    else:
        if matrix_offset:
            control.offsetParentMatrix.set(transform.worldMatrix.get())
        else:
            pm.matchTransform(control, transform)

    attribute.nonKeyable(control.visibility)
    return control
