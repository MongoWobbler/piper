#  Copyright (c) Christian Corsica. All Rights Reserved.

from piper.mayapy.rig import Rig
from . import space


def blobber(path=''):
    """
    Build script for a blobber character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    with Rig(path=path) as rig:
        root_ctrl = rig.root()[1][0]
        pelvis_ctrl = rig.FK('pelvis', name='Pelvis', axis='y', parent=root_ctrl)[1][0]
        butt_ctrl = rig.extra('pelvis', 'butt', scale=1.05, spaces=[pelvis_ctrl])[0]

        rig.FK('mouth', 'lips', parent=pelvis_ctrl, name='Mouth')
        [rig.FK(joint, parent=pelvis_ctrl, axis='y', name='Hair') for joint in ['hair_back', 'hair_mid', 'hair_front']]
        [rig.FK(joint, parent=pelvis_ctrl, axis='z', name='Eyes') for joint in ['eye_l', 'eye_r']]
        [rig.FKIK(start, end, parent=butt_ctrl, name=name) for start, end, name in [['upperarm_r', 'hand_r', 'Right Arm'], ['upperarm_l', 'hand_l', 'Left Arm'], ['thigh_l', 'foot_l', 'Left Leg'], ['thigh_r', 'foot_r', 'Right Leg']]]


def mooer(path=''):
    """
    Build script for a mooer character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    with Rig(path=path) as rig:
        root_ctrl = rig.root()[1][0]
        pelvis_ctrl = rig.FK('pelvis', name='Pelvis', parent=root_ctrl)[1][0]
        butt_ctrl, butt_spaces = rig.extra('pelvis', 'butt', scale=1.05, spaces=[pelvis_ctrl])

        tail_ctrls = rig.FK('tail_01', 'tail_05', parent=pelvis_ctrl, name='Tail')[1]
        tail_spaces = space.create(tail_ctrls[0])
        space.switch(tail_ctrls[0], tail_spaces[0], t=False, s=False)

        rig.FK('ear_01_r', 'ear_02_r', parent=pelvis_ctrl, name='Right Ear')
        rig.FK('ear_01_l', 'ear_02_l', parent=pelvis_ctrl, name='Left Ear')

        right_socket_ctrl = rig.FK('eyesocket_r', parent=pelvis_ctrl, axis='z', name='Right Eye')[1][0]
        right_eye_in_ctrl = rig.FK('eye_r', parent=right_socket_ctrl, axis='z', name='Right Eye')[-1][0]
        space.switch(right_eye_in_ctrl, 'worldSpace', t=False, r=True, o=True, s=False)
        [rig.FK(joint, parent=right_socket_ctrl, axis='y', name='Right Eye') for joint in ['eyelid_top_r', 'eyelid_bottom_r']]

        left_socket_ctrl = rig.FK('eyesocket_l', parent=pelvis_ctrl, axis='z', name='Left Eye')[1][0]
        left_eye_in_ctrl = rig.FK('eye_l', parent=left_socket_ctrl, axis='z', name='Left Eye')[-1][0]
        space.switch(left_eye_in_ctrl, 'worldSpace', t=False, r=True, o=True, s=False)
        [rig.FK(joint, parent=left_socket_ctrl, axis='y', name='Left Eye') for joint in ['eyelid_top_l', 'eyelid_bottom_l']]

        nose_ctrl = rig.FK('nose', parent=pelvis_ctrl, axis='z', name='Nose')[1][0]
        [rig.FK(joint, parent=nose_ctrl, axis='z', name='Nose') for joint in ['nostril_r', 'nostril_l']]
        [rig.FK(joint, parent=nose_ctrl, axis='y', name='Mouth') for joint in ['mouth_top', 'mouth_top_r', 'mouth_top_l']]
        [rig.FK(joint, parent=pelvis_ctrl, axis='y', name='Mouth') for joint in ['jaw', 'mouth_r', 'mouth_l']]

        _, right_arm_iks, right_arm_ctrls = rig.FKIK('upperarm_r', 'hand_r', parent=butt_ctrl, name='Right Arm')
        rig.banker(right_arm_iks[-1], right_arm_ctrls[-1], side='front right')

        _, left_arm_iks, left_arm_ctrls = rig.FKIK('upperarm_l', 'hand_l', parent=butt_ctrl, name='Left Arm')
        rig.banker(left_arm_iks[-1], left_arm_ctrls[-1], side='front left')

        _, right_leg_iks, right_leg_ctrls = rig.FKIK('thigh_r', 'foot_r', parent=butt_ctrl, name='Right Leg')
        rig.banker(right_leg_iks[-1], right_leg_ctrls[-1], side='back right')

        _, left_leg_iks, left_leg_ctrls = rig.FKIK('thigh_l', 'foot_l', parent=butt_ctrl, name='Left Leg')
        rig.banker(left_leg_iks[-1], left_leg_ctrls[-1], side='back left')


def wooer(path=''):
    """
    Build script for a wooer character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    with Rig(path=path) as rig:
        root_ctrl = rig.root()[1][0]
        pelvis_ctrl = rig.FK('pelvis', name='Pelvis', axis='y', parent=root_ctrl)[1][0]
        butt_ctrl = rig.extra('pelvis', 'butt', scale=1.05, spaces=[pelvis_ctrl])[0]

        _, tail_ctrls, _ = rig.FK('tail_01', 'tail_07', parent=pelvis_ctrl, name='Tail')
        rig.FK('flipper_01_l', 'flipper_03_l', parent=tail_ctrls[-1], name='Tail')
        rig.FK('flipper_01_r', 'flipper_03_r', parent=tail_ctrls[-1], name='Tail')

        [rig.FKIK(start, end, parent=butt_ctrl, name=name) for start, end, name in [['upperarm_r', 'hand_r', 'Right Arm'], ['upperarm_l', 'hand_l', 'Left Arm']]]

        rig.FK('nose', parent=pelvis_ctrl, axis='z', name='Nose')
        _, jaw_ctrls, _ = [rig.FK(joint, parent=pelvis_ctrl, axis='y', name='Mouth') for joint in ['jaw', 'mouth_r', 'mouth_l', 'mouth_top_r', 'mouth_top_l', 'mouth_top']][0]
        [rig.FK(joint, parent=jaw_ctrls[0], axis='y', name='Mouth') for joint in ['mouth_bottom_r', 'mouth_bottom', 'mouth_bottom_l']]
        [rig.FK(joint, parent=pelvis_ctrl, axis='z', name='Eyes') for joint in ['eye_l', 'eye_r', 'eyelid_top_l', 'eyelid_bottom_l', 'eyelid_top_r', 'eyelid_bottom_r']]


def johnnyJupiter(path=''):
    """
    Build script for a Johnny Jupiter character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    with Rig(path=path) as rig:
        root_ctrl = rig.root()[1][0]
        _, spine_ctrls, _ = rig.FK('pelvis', 'head', parent=root_ctrl, name='Spine')
        butt_ctrl = rig.extra('pelvis', 'butt', scale=1.05, spaces=[spine_ctrls[0]])[0]

        _, right_clavicle_ctrl, _ = rig.FK('clavicle_r', name='Right_Arm', parent=spine_ctrls[3])
        _, left_clavicle_ctrl, _ = rig.FK('clavicle_l', name='Left Arm', parent=spine_ctrls[3])

        _, _, right_arm_ctrls = rig.FKIK('upperarm_r', 'hand_r', name='Right Arm', parent=right_clavicle_ctrl[0])
        spaces = space.create(right_arm_ctrls[1], [root_ctrl, spine_ctrls[0], spine_ctrls[3]])
        space.switch(right_arm_ctrls[1], spaces[-2], t=False, r=True, o=True, s=True)

        _, _, left_arm_ctrls = rig.FKIK('upperarm_l', 'hand_l', name='Left Arm', parent=left_clavicle_ctrl[0])
        spaces = space.create(left_arm_ctrls[1], [root_ctrl, spine_ctrls[0], spine_ctrls[3]])
        space.switch(left_arm_ctrls[1], spaces[-2], t=False, r=True, o=True, s=True)

        rig.twist('lowerarm_twist_01_r', 'lowerarm_r', 'hand_r', name='Right Arm')
        rig.twist('upperarm_twist_01_r', 'upperarm_r', 'upperarm_r', blended=False, weight=-0.5, name='Right Arm')
        rig.twist('lowerarm_twist_01_l', 'lowerarm_l', 'hand_l', name='Left Arm')
        rig.twist('upperarm_twist_01_l', 'upperarm_l', 'upperarm_l', blended=False, weight=-0.5, name='Left Arm')

        rig.humanLeg('thigh_r', 'foot_r', 'ball_r', parent=butt_ctrl, name='Right Leg')
        rig.humanLeg('thigh_l', 'foot_l', 'ball_l', parent=butt_ctrl, name='Left Leg')

        rig.twist('thigh_twist_01_r', 'thigh_r', 'thigh_r', blended=False, weight=-0.5, name='Right Leg')
        rig.twist('thigh_twist_01_l', 'thigh_l', 'thigh_l', blended=False, weight=-0.5, name='Left Leg')

        [rig.FK(start, end, offset='hand_r', name='Right Fingers') for start, end in [['index_01_r', 'index_02_r'], ['middle_01_r', 'middle_02_r'], ['pinky_01_r', 'pinky_02_r'], ['thumb_01_r', 'thumb_03_r']]]
        [rig.FK(start, end, offset='hand_l', name='Left Fingers') for start, end in [['index_01_l', 'index_02_l'], ['middle_01_l', 'middle_02_l'], ['pinky_01_l', 'pinky_02_l'], ['thumb_01_l', 'thumb_03_l']]]

        backpack_ctrl = rig.FK('backpack', parent=spine_ctrls[3], axis='z', name='Backpack')[1][0]
        _, right_tubes, _ = rig.FK('tube_01_r', 'tube_07_r', parent=backpack_ctrl, name='Backpack')
        _, left_tubes, _ = rig.FK('tube_01_l', 'tube_07_l', parent=backpack_ctrl, name='Backpack')

        [rig.FK(joint, axis='z', parent=spine_ctrls[-1], name='Face') for joint in ['ear_r', 'ear_l', 'mouth', 'nose', 'eye_r', 'eye_l', 'eyebrow_out_r', 'eyebrow_mid_r', 'eyebrow_in_r', 'eyebrow_out_l', 'eyebrow_mid_l', 'eyebrow_in_l']]
        rig.FK('hair_01', 'hair_03', parent=spine_ctrls[-1], name='Face')

        helmet_ctrl = rig.FK('helmet', axis='z', parent=spine_ctrls[-1], name='Face')[1][0]
        helmet_space = space.create(right_tubes[-1], [helmet_ctrl])
        space.switch(right_tubes[-1], helmet_space[-1])

        helmet_space = space.create(left_tubes[-1], [helmet_ctrl])
        space.switch(left_tubes[-1], helmet_space[-1])


def sticker(path=''):
    """
    Build script for a Sticker character.

    Args:
        path (string): Path to skeletal mesh maya file with skeletal mesh node holding joints, skins, and mesh.
    """
    with Rig(path=path) as rig:
        root_ctrl = rig.root('root')[1][0]

        spine_ctrls = rig.FK('pelvis', 'head', parent=root_ctrl, name='Spine')[1]
        spine_ctrls[-1].volumetric.set(False)  # spine blows up if this is not off because it is stacked on top of head
        butt_ctrl, butt_spaces = rig.extra('pelvis', 'butt', scale=1.05, spaces=[spine_ctrls[0]])
        space.create(spine_ctrls[1], [root_ctrl, spine_ctrls[0]])

        right_arm_ctrls = rig.FKIK('upperarm_r', 'hand_r', name='Right Arm', parent=spine_ctrls[-2])[-1]
        left_arm_ctrls = rig.FKIK('upperarm_l', 'hand_l', name='Left Arm', parent=spine_ctrls[-2])[-1]
        rig.bendy(['upperarm_r', 'upperarm_twist_{}_r', 'lowerarm_r'], name='Right Upperarm', ctrl_parent=spine_ctrls[-2])
        rig.bendy(['lowerarm_r', 'lowerarm_twist_{}_r', 'hand_r'], name='Right Lowerarm')
        rig.bendy(['upperarm_l', 'upperarm_twist_{}_l', 'lowerarm_l'], name='Left Upperarm', ctrl_parent=spine_ctrls[-2])
        rig.bendy(['lowerarm_l', 'lowerarm_twist_{}_l', 'hand_l'], name='Left Lowerarm')
        space.create(right_arm_ctrls[1], [root_ctrl, spine_ctrls[0]])
        space.create(left_arm_ctrls[1], [root_ctrl, spine_ctrls[0]])

        rig.FKIK('thigh_r', 'foot_r', name='Right Leg', parent=butt_ctrl)[-1]
        rig.FKIK('thigh_l', 'foot_l', name='Left Leg', parent=butt_ctrl)[-1]
        rig.bendy(['thigh_r', 'thigh_twist_{}_r', 'calf_r'], name='Right Thigh', ctrl_parent=spine_ctrls[0])
        rig.bendy(['calf_r', 'calf_twist_{}_r', 'foot_r'], name='Right Calf')
        rig.bendy(['thigh_l', 'thigh_twist_{}_l', 'calf_l'], name='Left Thigh', ctrl_parent=spine_ctrls[0])
        rig.bendy(['calf_l', 'calf_twist_{}_l', 'foot_l'], name='Left Calf')
