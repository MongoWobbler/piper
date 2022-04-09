#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm

from piper.mayapy.rig import Rig
from piper.mayapy.mirror import mirror
from . import curve
from . import space


def blobber(path=''):
    """
    Build script for a blobber character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    with Rig(path=path, mirror=True) as rig:
        root_ctrl = rig.root()[1][0]
        pelvis_ctrl = rig.FK('pelvis', name='Pelvis', axis='y', parent=root_ctrl)[1][0]
        butt_ctrl = rig.extra('pelvis', 'butt', scale=1.05, spaces=[pelvis_ctrl])[0]

        rig.FK('mouth', 'lips', parent=pelvis_ctrl, name='Mouth')
        [rig.FK(joint, parent=pelvis_ctrl, axis='y', name='Hair') for joint in ['hair_back', 'hair_mid', 'hair_front']]
        rig.FK('eye_l', parent=pelvis_ctrl, axis='z', name='Eyes')
        rig.FKIK('upperarm_l', 'hand_l', parent=butt_ctrl, name='Left Arm')
        rig.FKIK('thigh_l', 'foot_l', parent=butt_ctrl, name='Left Leg')


def mooer(path=''):
    """
    Build script for a mooer character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    with Rig(path=path, mirror=True) as rig:
        root_ctrl = rig.root()[1][0]
        pelvis_ctrl = rig.FK('pelvis', name='Pelvis', axis='y', parent=root_ctrl)[1][0]
        butt_ctrl, butt_spaces = rig.extra('pelvis', 'butt', scale=1.05, spaces=[pelvis_ctrl])

        tail_ctrls = rig.FK('tail_01', 'tail_05', parent=pelvis_ctrl, name='Tail')[1]
        tail_spaces = rig.createSpace(tail_ctrls[0])
        rig.switchSpace(tail_ctrls[0], tail_spaces[0], t=False, s=False)

        rig.FK('ear_01_l', 'ear_02_l', parent=pelvis_ctrl, name='Left Ear')

        left_socket_ctrl = rig.FK('eyesocket_l', parent=pelvis_ctrl, axis='z', name='Left Eye')[1][0]
        left_eye_in_ctrl = rig.FK('eye_l', parent=left_socket_ctrl, axis='z', name='Left Eye')[-1][0]
        rig.switchSpace(left_eye_in_ctrl, 'worldSpace', t=False, r=True, o=True, s=False)

        eyelid_joints = ['eyelid_top_l', 'eyelid_bottom_l']
        [rig.FK(joint, parent=left_socket_ctrl, axis='y', name='Left Eye') for joint in eyelid_joints]

        nose_ctrl = rig.FK('nose', parent=pelvis_ctrl, axis='z', name='Nose')[1][0]
        rig.FK('nostril_l', parent=nose_ctrl, axis='z', name='Nose')
        [rig.FK(joint, parent=nose_ctrl, axis='y', name='Mouth') for joint in ['mouth_top', 'mouth_top_l']]
        [rig.FK(joint, parent=pelvis_ctrl, axis='y', name='Mouth') for joint in ['jaw', 'mouth_l']]

        _, left_arm_iks, left_arm_ctrls = rig.FKIK('upperarm_l', 'hand_l', parent=butt_ctrl, name='Left Arm')
        rig.banker(left_arm_iks[-1], left_arm_ctrls[-1], side='Left Front')

        _, left_leg_iks, left_leg_ctrls = rig.FKIK('thigh_l', 'foot_l', parent=butt_ctrl, name='Left Leg')
        rig.banker(left_leg_iks[-1], left_leg_ctrls[-1], side='Left Back')


def waooer(path=''):
    """
    Build script for a waooer character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    with Rig(path=path, mirror=True) as rig:
        root_ctrl = rig.root()[1][0]
        pelvis_ctrl = rig.FK('pelvis', name='Pelvis', axis='y', parent=root_ctrl)[1][0]
        butt_ctrl, butt_spaces = rig.extra('pelvis', 'butt', scale=1.05, spaces=[pelvis_ctrl])
        space.switch(butt_ctrl, butt_spaces[-1])

        _, tail_ctrls, _ = rig.FK('tail_01', 'tail_07', parent=pelvis_ctrl, name='Tail')
        rig.FK('flipper_01_l', 'flipper_03_l', parent=tail_ctrls[-1], name='Tail')

        left_arm_ctrls = rig.FKIK('upperarm_l', 'hand_l', parent=butt_ctrl, name='Left Arm')[-1]
        elbow_spaces = rig.createSpace(left_arm_ctrls[2], [pelvis_ctrl])
        rig.switchSpace(left_arm_ctrls[2], elbow_spaces[0])

        rig.FK('nose', parent=pelvis_ctrl, axis='z', name='Nose')

        upper_mouth_joints = ['jaw', 'mouth_l', 'mouth_top_l', 'mouth_top']
        jaw_ctrls = [rig.FK(joint, parent=pelvis_ctrl, axis='y', name='Mouth') for joint in upper_mouth_joints][0][1]
        [rig.FK(joint, parent=jaw_ctrls[0], axis='y', name='Mouth') for joint in ['mouth_bottom', 'mouth_bottom_l']]

        eye_joints = ['eye_l', 'eyelid_top_l', 'eyelid_bottom_l']
        [rig.FK(joint, parent=pelvis_ctrl, axis='z', name='Eyes') for joint in eye_joints]


def johnnyJupiter(path=''):
    """
    Build script for a johnny jupiter character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    fingers = [['index_01_l', 'index_02_l'],
               ['middle_01_l', 'middle_02_l'],
               ['pinky_01_l', 'pinky_02_l'],
               ['thumb_01_l', 'thumb_03_l']]

    with Rig(path=path, mirror=True) as rig:
        # root and spine
        root_ctrl = rig.root()[1][0]
        _, spine_ctrls, _ = rig.FK('pelvis', 'head', parent=root_ctrl, name='Spine')
        butt_ctrl = rig.extra('pelvis', 'butt', scale=1.05, spaces=[spine_ctrls[0]])[0]
        head_space = space.create(spine_ctrls[-1], [spine_ctrls[0]])
        space.switch(spine_ctrls[-1], head_space[-1], t=False, r=True, o=True, s=True)

        # arm
        clavicle_ctrl = rig.FK('clavicle_l', name='Left Arm', parent=spine_ctrls[3])[1][0]
        arm_ctrls = rig.FKIK('upperarm_l', 'hand_l', spaces=[spine_ctrls[0]], name='Left Arm', parent=clavicle_ctrl)[-1]
        spaces = rig.createSpace(arm_ctrls[1], [root_ctrl, spine_ctrls[0], spine_ctrls[3]])
        rig.switchSpace(arm_ctrls[1], spaces[-2], t=False, r=True, o=True, s=True)

        # twist and fingers
        rig.twist('lowerarm_twist_01_l', 'lowerarm_l', 'hand_l', name='Left Arm')
        rig.twist('upperarm_twist_01_l', 'upperarm_l', 'upperarm_l', blended=False, weight=-0.5, name='Left Arm')
        [rig.FK(start, end, offset='hand_l', name='Left Fingers') for start, end in fingers]

        # leg
        rig.humanLeg('thigh_l', 'foot_l', 'ball_l', parent=butt_ctrl, name='Left Leg')
        rig.twist('thigh_twist_01_l', 'thigh_l', 'thigh_l', blended=False, weight=-0.5, name='Left Leg')

        # backpack
        backpack_ctrl = rig.FK('backpack', parent=spine_ctrls[3], axis='z', name='Backpack')[1][0]
        backspace_space = space.create(backpack_ctrl, [spine_ctrls[0]])
        space.switch(backpack_ctrl, backspace_space[-1], t=False, r=True, o=True, s=True)
        _, left_tubes, _ = rig.FK('tube_01_l', 'tube_07_l', parent=backpack_ctrl, name='Backpack')

        # face
        face_joints = ['ear_l', 'mouth', 'nose', 'eye_l']
        [rig.FK(joint, axis='z', parent=spine_ctrls[-1], name='Face') for joint in face_joints]
        rig.FK('hair_01', 'hair_03', parent=spine_ctrls[-1], name='Face')

        # eyebrows
        eyebrow_joints = ['eyebrow_out_l', 'eyebrow_mid_l', 'eyebrow_in_l']
        ctrl = rig.FK('eyebrow_l', parent=spine_ctrls[-1], shape=curve.square, axis='z', name='Left Eyebrow')[1][0]
        [rig.FK(joint, axis='z', parent=ctrl, name='Left Eyebrow') for joint in eyebrow_joints]

        # helmet
        helmet_ctrl = rig.FK('helmet', axis='z', parent=spine_ctrls[-1], name='Face')[1][0]
        helmet_space = rig.createSpace(left_tubes[-1], [helmet_ctrl])
        rig.switchSpace(left_tubes[-1], helmet_space[-1])

        [mirror(pm.setAttr, tube.name() + '.volumetric', 0) for tube in left_tubes]


def sticker(path=''):
    """
    Build script for a sticker character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    with Rig(path=path, mirror=True) as rig:
        root_ctrl = rig.root('root')[1][0]

        spine_ctrls = rig.FK('pelvis', 'head', parent=root_ctrl, name='Spine')[1]
        spine_ctrls[-1].volumetric.set(False)  # spine blows up if this is not off because it is stacked on top of head
        butt_ctrl, butt_spaces = rig.extra('pelvis', 'butt', scale=1.05, spaces=[spine_ctrls[0]])
        space.create(spine_ctrls[1], [root_ctrl, spine_ctrls[0]])

        left_arm_ctrls = rig.FKIK('upperarm_l', 'hand_l', name='Left Arm', parent=spine_ctrls[-2])[-1]
        upperarm_joints = ['upperarm_l', 'upperarm_twist_{}_l', 'lowerarm_l']
        rig.bendy(upperarm_joints, name='Left Upperarm', ctrl_parent=spine_ctrls[-2])
        rig.bendy(['lowerarm_l', 'lowerarm_twist_{}_l', 'hand_l'], name='Left Lowerarm')
        rig.createSpace(left_arm_ctrls[1], [root_ctrl, spine_ctrls[0]])

        rig.FKIK('thigh_l', 'foot_l', name='Left Leg', parent=butt_ctrl)[-1]
        rig.bendy(['thigh_l', 'thigh_twist_{}_l', 'calf_l'], name='Left Thigh', ctrl_parent=spine_ctrls[0])
        rig.bendy(['calf_l', 'calf_twist_{}_l', 'foot_l'], name='Left Calf')
