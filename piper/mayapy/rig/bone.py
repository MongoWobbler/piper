#  Copyright (c) Christian Corsica. All Rights Reserved.

import copy
import pymel.core as pm

import piper.config as pcfg
import piper.config.maya as mcfg

import piper.core.namer as namer
import piper.mayapy.convert as convert
import piper.mayapy.hierarchy as hierarchy
import piper.mayapy.modifier as modifier
import piper.mayapy.selection as selection
import piper.mayapy.manipulator as manipulator

from . import xform
from . import curve


def getRoot(skinned_mesh=None, start=None, namespace=None, warn=True):
    """
    Gets the root joint from a piper skinned mesh.

    Args:
        skinned_mesh (pm.nodetypes.Transform): Node to look for root joint under.

        start (pm.nodetypes.Transform): Node to look for children that are of type piperSkinnedMesh to look for joints.

        namespace (string): Used to filter skinned meshes to make sure we have the right one.

        warn (boolean): If true, will warn about root joint not found or multiple skinned meshes found.

    Returns:
        (pm.nodetypes.Joint): Root joint for skeleton.
    """
    if not skinned_mesh:
        if start:
            skinned_meshes = start.getChildren(ad=True, type='piperSkinnedMesh')
        else:
            skinned_meshes = selection.get('piperSkinnedMesh')

        if namespace:
            skinned_meshes = list(filter(lambda node: namespace in node.namespace(), skinned_meshes))

        if len(skinned_meshes) != 1:
            pm.warning('Found {} skinned meshes trying to get root!'.format(str(len(skinned_meshes)))) if warn else None
            return None

        skinned_mesh = skinned_meshes[0]

    root = skinned_mesh.getChildren(type='joint')
    if len(root) != 1:
        pm.warning('Found {} root joint(s) in {}!'.format(str(len(root)), skinned_mesh.name())) if warn else None
        return None

    root = root[0]
    if root.name(stripNamespace=True) != pcfg.root_joint_name:
        pm.warning('Root joint {} does not match config name {}'.format(root.name(), pcfg.root_joint_name))

    return root


def jointOrientToRotation(joints=None):
    """
    Removes all the joints orients from the joints given/found.

    Args:
        joints (list): Joints to remove joint orients of
    """
    joints = selection.validate(joints, find='joint')
    data = hierarchy.save(joints)
    hierarchy.reparent(data, xform.parent)


def rotationToJointOrient(joints=None):
    """
    Sets the given/found joint orient value from their rotation value, and removes all rotations values.

    Args:
        joints (list): Joints to remove rotation values and set joint orient values of.
    """
    joints = selection.validate(joints, find='joint')

    for joint in joints:
        rotation = joint.r.get()
        joint.jointOrient.set(rotation)
        joint.r.set(0, 0, 0)


def assignShape(joints, shape=curve.circle, *args, **kwargs):
    """
    Assigns a shape for given joints.

    Args:
        joints (list): Joints to assign curve shape to.

        shape (method): Creates the transform for the shapes desired for the joints
    """
    for joint in joints:
        joint.drawStyle.set(2)
        shape_transform = shape(*args, **kwargs)
        pm.delete(shape_transform, ch=True)
        joint_matrix = joint.worldMatrix.get()
        pm.xform(shape_transform, ws=True, m=joint_matrix)

        shapes = shape_transform.getShapes()
        for i, ctrl_shape in enumerate(shapes):
            pm.parent(ctrl_shape, joint, s=1, r=1)
            pm.rename(ctrl_shape, '{}Shape'.format(joint))

        pm.delete(shape_transform)


def assignLabels(joints=None):
    """
    Assigns labels and sides to the given joints based on their names.

    Args:
        joints (list): Joints to assign labels to.
    """
    joints = selection.validate(joints, find='joint')

    for joint in joints:
        joint_name = joint.nodeName()

        if joint_name.endswith(pcfg.left_suffix):
            joint.side.set(1)
            joint_name = namer.removeSuffixes(joint_name, pcfg.left_suffix)
        elif joint_name.endswith(pcfg.right_suffix):
            joint.side.set(2)
            joint_name = namer.removeSuffixes(joint_name, pcfg.right_suffix)

        # have to do string "type" because type is a built-in python function
        if joint_name in convert.JOINT_LABELS:
            label = convert.jointNameToLabel(joint_name)
            joint.attr('type').set(label)
        else:
            label = convert.jointNameToLabel('other')
            joint.attr('type').set(label)
            joint.otherType.set(joint_name)


def assignBindAttributes(joints=None):
    """
    Assigns the bind matrix attribute to the given joints.

    Args:
        joints (list): Joints to assign bind matrix attribute to. If None given, will use selected or all joints.
    """
    joints = selection.validate(joints, find='joint')

    for joint in joints:

        if not joint.hasAttr(mcfg.length_attribute):
            joint.addAttr(mcfg.length_attribute, s=True, w=True, r=True, dv=0.001, min=0.001)

        joint_parent = joint.getParent()
        if joint_parent and isinstance(joint_parent, pm.nodetypes.Joint):
            distance_name = joint.name() + '_to_' + joint_parent.name() + mcfg.distance_suffix

            if pm.objExists(distance_name):
                pm.delete(distance_name)

            distance = pm.createNode('distanceBetween', n=distance_name)
            joint.worldMatrix >> distance.inMatrix1
            joint_parent.worldMatrix >> distance.inMatrix2
            distance.distance >> joint.attr(mcfg.length_attribute)

    pm.displayInfo('Finished assigning Piper joint attributes to ' + str(len(joints)) + ' joints.')


def setSegmentScaleCompensateOff(joints=None):
    """
    Sets the segment scale compensate attribute of the given joints to False.

    Args:
        joints (list): Joints to set segment scale compensate to False.
    """
    joints = selection.validate(joints, find='joint')
    turned_off = [joint.segmentScaleCompensate.set(False) for joint in joints if joint.segmentScaleCompensate.get()]
    pm.displayInfo('Finished turning segment scale compensate off for ' + str(len(turned_off)) + ' joints.')


def _createAtPivot(transform, name='', i=None, component_prefix=None, joints=None):
    """
    Simple convenience method for creating a joint at the transform's pivot. Meant to be used by createAtPivot.

    Args:
        transform (any): Will select given transform to figure out pivot to create joint at.

        name (string): Name to give joint.

        i (int): Used to get specific component node.

        component_prefix (string): Abbreviation for component to get with given i. Usually "vtx", "e", or "f".

        joints (list): Appends created joint to given joints.

    Returns:
        (list): Joints created, position of joint created, and component node
    """
    component = None

    if i is not None and component_prefix is not None:
        shape_name = transform.node().name()
        component = pm.PyNode(shape_name + '.{}[{}]'.format(component_prefix, str(i)))
        position = manipulator.getManipulatorPosition(component)
    else:
        position = manipulator.getManipulatorPosition(transform)

    joint = pm.joint(p=position, n=name)

    if isinstance(joints, list):
        joints.append(joint)

    return joint, position, component


def createAtPivot(selected=None, each=False, orient=False, name=False):
    """
    Creates a joint at the current manipulator pivot point.

    If SHIFT held: will create joint for EVERY transform/vertex/edge/face selected.
    If CTRL held: will orient joint to selected transform/vertex/edge/face selected.
    If ALT held: will assign name to new joint(s) based on current transform/vertex/edge/face selection.

    Args:
        selected (list):

        each (boolean): If True, will create joint for every transform/vertex/edge/face.

        orient (boolean): If True, will orient joint to transform/vertex/edge/face.

        name (boolean): If True, will name the new joint(s) based on the transform/vertex/edge/face.

    Returns:
        (list): Joints created.
    """
    joints = []
    shift_held = modifier.isShiftHeld() or each
    ctrl_held = modifier.isCtrlHeld() or orient
    alt_held = modifier.isAltHeld() or name
    selected = selection.validate(selected, minimum=1)

    if shift_held:
        for transform in selected:
            name = transform.name() if alt_held else ''
            if isinstance(transform, pm.nodetypes.Transform):
                joint, position, _ = _createAtPivot(transform, name, joints=joints)
                xform.orientToTransform(transform, joint, ctrl_held)

            elif isinstance(transform, pm.general.MeshVertex):
                for i in transform.indices():
                    joint, position, vertex = _createAtPivot(transform, name, i, 'vtx', joints)
                    xform.orientToVertex(joint, vertex, position, ctrl_held)

            elif isinstance(transform, pm.general.MeshEdge):
                for i in transform.indices():
                    joint, position, edge = _createAtPivot(transform, name, i, 'e', joints)
                    xform.orientToEdge(joint, edge, position, ctrl_held)

            elif isinstance(transform, pm.general.MeshFace):
                for i in transform.indices():
                    joint, position, face = _createAtPivot(transform, name, i, 'f', joints)
                    xform.orientToFace(joint, face, position, ctrl_held)

    else:
        transform = selected[-1]
        name = transform.name() if alt_held else ''
        joint, position, _ = _createAtPivot(transform, name, joints=joints)

        if len(selected) == 1 and ctrl_held:

            if isinstance(transform, pm.nodetypes.Transform):
                xform.orientToTransform(transform, joint)

            elif isinstance(transform, pm.general.MeshVertex):
                xform.orientToVertex(joint, transform, position)

            elif isinstance(transform, pm.general.MeshEdge):
                xform.orientToEdge(joint, transform, position)

            elif isinstance(transform, pm.general.MeshFace):
                xform.orientToFace(joint, transform, position)

    return joints


def createShaped(shape=curve.circle, name='joint1', *args, **kwargs):
    """
    Convenience method for creating a joint with a nurbs shapes.

    Args:
        name (string): Name to give joint.

        shape (method): Creates the transform for the shapes desired for the joints

    Returns:
        (pm.nodetypes.Joint): Joint created.
    """
    joint = pm.joint(n=name)
    assignShape([joint], shape=shape, *args, **kwargs)
    return joint


def health(parent_fail=pm.error,
           no_children_fail=pm.warning,
           type_fail=pm.error,
           joint_orient_fail=pm.warning,
           segment_scale_fail=pm.error,
           preferred_angle_fail=pm.warning,
           bind_attribute_fail=pm.warning,
           bind_connection_fail=pm.warning):
    """
    Performs a health check on the skeleton to catch anything that might cause trouble further down pipe.

    Args:
        parent_fail (method): How to display message of root joint not being the top of the hierarchy.

        no_children_fail (method): How to display message of no children found under root joint.

        type_fail (method): How to display message of non-joint type found in skeleton hierarchy.

        joint_orient_fail (method): How to display message of non-zero joint orient values found in joint.

        segment_scale_fail (method): How to display message when joint has segment scale compensate turned on.

        preferred_angle_fail (method): How to display message when joint does not have preferred angle set.

        bind_attribute_fail (method): How to display message when joint does not have bind matrix attribute.

        bind_connection_fail (method): How to display message when joint does not have bind length attribute connected.

    Returns:
        (dictionary): Error causing nodes.
    """
    actionable_default = {'parent': None,
                          'type': [],
                          'joint_orient': [],
                          'segment_scale': [],
                          'preferred_angle': [],
                          'bind_attribute': [],
                          'bind_connection': [],
                          'children': None}
    actionable = copy.deepcopy(actionable_default)

    # check if root joint exists and that there is only one
    root_joint = pm.PyNode(pcfg.root_joint_name)

    # check if root has parent. Only valid parent is a skinned mesh node
    root_parent = root_joint.getParent()
    if root_parent and not isinstance(root_parent, pm.nodetypes.PiperSkinnedMesh):
        actionable['parent'] = root_joint
        parent_fail(pcfg.root_joint_name + ' is parented to invalid transform!')

    joints = root_joint.getChildren(ad=True)

    # warn user about having only root joint
    if not joints:
        actionable['children'] = root_joint
        no_children_fail('No skeleton hierarchy found! Only ' + pcfg.root_joint_name + ' found.')

    # set up hierarchy traversal, start with root joint by appending and reversing list
    joints.append(root_joint)
    joints.reverse()
    for joint in joints:
        joint_name = joint.nodeName()

        # check hierarchy to make sure everything is a joint
        if not isinstance(joint, pm.nodetypes.Joint):
            actionable['type'].append(joint)
            type_fail(joint_name + ' is not a joint!')

        # check if joint orient values is equal to zero
        joint_orient = joint.jointOrient.get()
        zero_vector = pm.dt.Vector(0, 0, 0)
        if not joint_orient.isEquivalent(zero_vector, tol=0.1):
            actionable['joint_orient'].append(joint)
            joint_orient_fail('The "' + joint_name + '" joint has non-zero joint orient values.')

        #  check if joint has segment scale compensate set to True or False (should be True)
        if joint.segmentScaleCompensate.get():
            actionable['segment_scale'].append(joint)
            segment_scale_fail('The "' + joint_name + '" joint has segment scale compensate turned on!')

        # check if joint has preferred angle ONLY if joint is not an end joint
        if joint.getChildren(type='joint') and \
           joint.preferredAngle.get().isEquivalent(zero_vector, tol=0.1) and \
           any([prefix in joint_name for prefix in mcfg.required_preferred_angle]):

            actionable['preferred_angle'].append(joint)
            preferred_angle_fail(joint_name + ' does not have a preferred angle set to non-zero value!')

        # check if joint has bind length attribute
        if not joint.hasAttr(mcfg.length_attribute):
            actionable['bind_attribute'].append(joint)
            bind_attribute_fail(joint_name + ' does not have the ' + mcfg.length_attribute + ' attribute!')

        # check if joint has bind length attribute connected
        elif not joint.attr(mcfg.length_attribute).connections(skipConversionNodes=True) and joint != root_joint:
            actionable['bind_connection'].append(joint)
            bind_connection_fail(joint_name + ' does not have the ' + mcfg.length_attribute + ' connected!')

    errors = {} if actionable == actionable_default else actionable
    pm.warning('Errors found in skeleton! Open Script Editor') if errors else pm.displayInfo('Skeleton is happy')
    return errors
