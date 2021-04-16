#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import copy
import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.util as myu
import piper.mayapy.convert as convert
import piper.mayapy.pipermath as pipermath


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

        if not joint.hasAttr(pcfg.matrix_attribute):
            joint.addAttr(pcfg.matrix_attribute, at='matrix')

        if not joint.hasAttr(pcfg.matrix_inverse_attribute):
            joint.addAttr(pcfg.matrix_inverse_attribute, at='matrix')

        matrix = joint.worldMatrix.get()
        inverse_matrix = joint.worldInverseMatrix.get()
        joint_parent = joint.getParent()

        if joint_parent and isinstance(joint_parent, pm.nodetypes.Joint):
            length = pipermath.getDistance(joint_parent, joint)
            joint.bindLength.set(length)

        joint.attr(pcfg.matrix_attribute).set(matrix)
        joint.bindInverseMatrix.set(inverse_matrix)

    pm.displayInfo('Finished assigning Piper joint attributes to ' + str(len(joints)) + ' joints.')


def createAtPivot():
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


def health(parent_fail=pm.error,
           no_children_fail=pm.warning,
           type_fail=pm.error,
           joint_orient_fail=pm.warning,
           segment_scale_fail=pm.error,
           preferred_angle_fail=pm.warning,
           matrix_attribute_fail=pm.warning):
    """
    Performs a health check on the skeleton to catch anything that might cause trouble further down pipe.

    Args:
        parent_fail (method): How to display message of root joint not being the top of the hierarchy.

        no_children_fail (method): How to display message of no children found under root joint.

        type_fail (method): How to display message of non-joint type found in skeleton hierarchy.

        joint_orient_fail (method): How to display message of non-zero joint orient values found in joint.

        segment_scale_fail (method): How to display message when joint has segment scale compensate turned on.

        preferred_angle_fail (method): How to display message when joint does not have preferred angle set.

        matrix_attribute_fail (method): How to display message when joint does not have bind matrix attribute.

    Returns:
        (dictionary): Error causing nodes.
    """
    actionable_default = {'parent': None,
                          'type': [],
                          'joint_orient': [],
                          'segment_scale': [],
                          'preferred_angle': [],
                          'matrix_attribute': [],
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
            joint_orient_fail(joint_name + ' has non-zero joint orient values.')

        #  check if joint has segment scale compensate set to True or False (should be True)
        if joint.segmentScaleCompensate.get():
            actionable['segment_scale'].append(joint)
            segment_scale_fail(joint_name + ' segment scale compensate is turned on!')

        # check if joint has preferred angle ONLY if joint is not an end joint
        if joint.getChildren(type='joint') and \
           joint.preferredAngle.get().isEquivalent(zero_vector, tol=0.1) and \
           any([prefix in joint_name for prefix in pcfg.required_preferred_angle]):

            actionable['preferred_angle'].append(joint)
            preferred_angle_fail(joint_name + ' does not have a preferred angle set!')

        # check if joint has bind matrix attribute
        if not joint.hasAttr(pcfg.matrix_attribute):
            actionable['matrix_attribute'].append(joint)
            matrix_attribute_fail(joint_name + ' does not have the ' + pcfg.matrix_attribute + ' attribute!')

    errors = {} if actionable == actionable_default else actionable
    pm.warning('Errors found in skeleton! Open Script Editor') if errors else pm.displayInfo('Skeleton is happy')
    return errors
