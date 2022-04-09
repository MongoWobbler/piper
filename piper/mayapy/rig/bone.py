#  Copyright (c) Christian Corsica. All Rights Reserved.

import copy
import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.util as myu
import piper.mayapy.convert as convert

from . import xform
from . import curve


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
    joints = myu.validateSelect(joints, find='joint')

    for joint in joints:
        joint_name = joint.nodeName()

        if joint_name.endswith(pcfg.left_suffix):
            joint.side.set(1)
            joint_name = pcu.removeSuffixes(joint_name, pcfg.left_suffix)
        elif joint_name.endswith(pcfg.right_suffix):
            joint.side.set(2)
            joint_name = pcu.removeSuffixes(joint_name, pcfg.right_suffix)

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
    joints = myu.validateSelect(joints, find='joint')

    for joint in joints:

        if not joint.hasAttr(pcfg.length_attribute):
            joint.addAttr(pcfg.length_attribute, s=True, w=True, r=True, dv=0.001, min=0.001)

        joint_parent = joint.getParent()
        if joint_parent and isinstance(joint_parent, pm.nodetypes.Joint):
            distance_name = joint.name() + '_to_' + joint_parent.name() + pcfg.distance_suffix

            if pm.objExists(distance_name):
                pm.delete(distance_name)

            distance = pm.createNode('distanceBetween', n=distance_name)
            joint.worldMatrix >> distance.inMatrix1
            joint_parent.worldMatrix >> distance.inMatrix2
            distance.distance >> joint.attr(pcfg.length_attribute)

    pm.displayInfo('Finished assigning Piper joint attributes to ' + str(len(joints)) + ' joints.')


def setSegmentScaleCompensateOff(joints=None):
    """
    Sets the segment scale compensate attribute of the given joints to False.

    Args:
        joints (list): Joints to set segment scale compensate to False.
    """
    joints = myu.validateSelect(joints, find='joint')
    [joint.segmentScaleCompensate.set(False) for joint in joints]


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
        position = myu.getManipulatorPosition(component)
    else:
        position = myu.getManipulatorPosition(transform)

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
    shift_held = myu.isShiftHeld() or each
    ctrl_held = myu.isCtrlHeld() or orient
    alt_held = myu.isAltHeld() or name
    selected = myu.validateSelect(selected, minimum=1)

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
           bind_attribute_fail=pm.warning):
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

    Returns:
        (dictionary): Error causing nodes.
    """
    actionable_default = {'parent': None,
                          'type': [],
                          'joint_orient': [],
                          'segment_scale': [],
                          'preferred_angle': [],
                          'bind_attribute': [],
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
           any([prefix in joint_name for prefix in pcfg.required_preferred_angle]):

            actionable['preferred_angle'].append(joint)
            preferred_angle_fail(joint_name + ' does not have a preferred angle set to non-zero value!')

        # check if joint has bind length attribute
        if not joint.hasAttr(pcfg.length_attribute):
            actionable['bind_attribute'].append(joint)
            bind_attribute_fail(joint_name + ' does not have the ' + pcfg.length_attribute + ' attribute!')

    errors = {} if actionable == actionable_default else actionable
    pm.warning('Errors found in skeleton! Open Script Editor') if errors else pm.displayInfo('Skeleton is happy')
    return errors
