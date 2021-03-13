#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import copy
import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.util as myu
import piper.mayapy.convert as convert


def assignLabels(joints=None):
    """
    Assigns labels and sides to the given joints based on their names.

    Args:
        joints (list): Joints to assign labels to.
    """
    joints = myu.validateSelect(joints, find='joint')

    for joint in joints:
        has_side = False
        joint_name = joint.nodeName()

        if joint_name.endswith(pcfg.left_suffix):
            has_side = True
            joint.side.set(1)
            joint_name = pcu.removeSuffixes(joint_name, pcfg.left_suffix)
        elif joint_name.endswith(pcfg.right_suffix):
            has_side = True
            joint.side.set(2)
            joint_name = pcu.removeSuffixes(joint_name, pcfg.right_suffix)

        # have to do string "type" because type is a built-in python function
        if has_side:
            label = convert.jointNameToLabel('other')
            joint.attr('type').set(label)
            joint.otherType.set(joint_name)
        else:
            label = convert.jointNameToLabel(joint_name)
            joint.attr('type').set(label)


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
           segment_scale_fail=pm.warning,
           preferred_angle_fail=pm.warning):
    """
    Performs a health check on the skeleton to catch anything that might cause trouble further down pipe.

    Args:
        parent_fail (method): How to display message of root joint not being the top of the hierarchy.

        no_children_fail (method): How to display message of no children found under root joint.

        type_fail (method): How to display message of non-joint type found in skeleton hierarchy.

        joint_orient_fail (method): How to display message of non-zero joint orient values found in joint.

        segment_scale_fail (method): How to display message when joint has segment scale compensate turned off.

        preferred_angle_fail (method): How to display message when joint does not have preferred angle set.

    Returns:
        (dictionary): Error causing nodes.
    """
    actionable_default = {'parent': None,
                          'type': [],
                          'joint_orient': [],
                          'segment_scale': [],
                          'preferred_angle': [],
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
        if joint_orient != zero_vector:
            actionable['joint_orient'].append(joint)
            joint_orient_fail(joint_name + ' has non-zero joint orient values.')

        #  check if joint has segment scale compensate set to True or False (should be True)
        if not joint.segmentScaleCompensate.get():
            actionable['segment_scale'].append(joint)
            segment_scale_fail(joint_name + ' segment scale compensate is turned off!')

        # check if joint has preferred angle ONLY if joint is not an end joint
        if joint.getChildren(type='joint') and joint.preferredAngle.get() == zero_vector:
            actionable['preferred_angle'].append(joint)
            preferred_angle_fail(joint_name + ' does not have a preferred angle set!')

    errors = {} if actionable == actionable_default else actionable
    pm.warning('Errors found in skeleton! Open Script Editor') if errors else pm.displayInfo('Skeleton is happy')
    return errors
