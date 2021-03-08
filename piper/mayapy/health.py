#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import copy
import pymel.core as pm
import piper_config as pcfg


def skeleton(parent_fail=pm.error,
             no_children_fail=pm.warning,
             type_fail=pm.error,
             joint_orient_fail=pm.warning,
             segment_scale_fail=pm.warning):
    """
    Performs a health check on the skeleton to catch anything that might cause trouble further down pipe.

    Args:
        parent_fail (method): How to display message of root joint not being the top of the hierarchy.

        no_children_fail (method): How to display message of no children found under root joint.

        type_fail (method): How to display message of non-joint type found in skeleton hierarchy.

        joint_orient_fail (method): How to display message of non-zero joint orient values found in joint.

        segment_scale_fail (method): How to display message when joint has segment scale compensate turned off.

    Returns:
        (dictionary): Error causing nodes.
    """
    actionable_default = {'parent': None,
                          'type': [],
                          'joint_orient': [],
                          'segment_scale': [],
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

    errors = {} if actionable == actionable_default else actionable
    pm.warning('Errors found in skeleton! Open Script Editor') if errors else pm.displayInfo('Skeleton is happy')
    return errors
