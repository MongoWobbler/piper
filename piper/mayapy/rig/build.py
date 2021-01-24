#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.core.util as pcu
import piper.mayapy.rig.core as rig
import piper.mayapy.rig.control as control
import piper.mayapy.rig.createshape as createshape
import piper.mayapy.pipernode as pipernode
import piper.mayapy.pipermath as pipermath
import piper.mayapy.convert as convert


def FK(start, end=None, parent=None, axis=None, shape=createshape.circle):
    """
    Creates FK controls for the transform chain deduced by the start and end transforms.

    Args:
        start (pm.nodetypes.Transform): Start of the chain to be driven by FK controls.

        end (pm.nodetypes.Transform): End of the chain to be driven by FK controls. If none given, will only drive start

        parent (pm.nodetypes.Transform): If given, will drive the start control through parent matrix constraint.

        axis (string): Only used if no end joint given for shape's axis to match rotations.

        shape (method): Used to create curve or visual representation of FK control.

    Returns:
        (list): Controls created in order from start to end.
    """
    controls = []
    transforms = rig.getChain(start, end)

    for i, transform in enumerate(transforms):
        if transform != transforms[-1]:
            next_transform = transforms[i + 1]
            axis_vector = rig.getOrientAxis(transform, next_transform)
            axis = convert.axisToString(axis_vector)

        control_parent = parent if transform == transforms[0] else controls[i - 1]
        ctrl, _ = control.create(transform, name=transform.nodeName(), axis=axis, parent=control_parent, shape=shape)
        rig.parentMatrixConstraint(ctrl, transform)
        controls.append(ctrl)

    return controls


def IK(start, end, parent=None, shape=createshape.ring):
    """
    Creates IK controls and IK RP solver and for the given start and end joints.

    Args:
        start (pm.nodetypes.Joint): Start of the joint chain.

        end (pm.nodetypes.Joint): End of the joint chain.

        parent (pm.nodetypes.Transform): Parent of start control.

        shape (method): Creates the shape control that will drive joints.

    Returns:
        (list): Controls created in order from start to end.
    """
    transforms = rig.getChain(start, end)
    mid = pcu.getMedian(transforms)
    axis = None
    mid_ctrl = None
    controls = []

    if mid == start or mid == end:
        pm.error('Not enough joints given! {} is the mid joint?'.format(mid.nodeName()))

    start_initial_length = pipermath.getDistance(start, mid)
    end_initial_length = pipermath.getDistance(mid, end)

    for i, transform in enumerate(transforms):
        name = transform.nodeName()
        control_parent = parent if transform == transforms[0] else None

        if transform != transforms[-1]:
            next_transform = transforms[i + 1]
            axis_vector = rig.getOrientAxis(transform, next_transform)
            axis = convert.axisToString(axis_vector)

        # start
        if transform == transforms[0]:
            ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=shape)
            rig.lockAndHideCompound(ctrl, ['r', 's'])
            scale_ctrl, _ = control.create(transform,
                                           name=name + '_scale',
                                           axis=axis,
                                           scale=0.75,
                                           parent=ctrl,
                                           shape=createshape.circle,
                                           matrix_offset=False)
            rig.parentMatrixConstraint(transform, scale_ctrl, t=False, s=False)
            rig.lockAndHideCompound(scale_ctrl, ['t', 'r'])
            scale_ctrl.s >> transform.s
            controls.append(scale_ctrl)

        # mid
        elif transform == mid:
            ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=createshape.orb)
            translation, rotate, scale = rig.calculatePoleVectorTransform(start, mid, end)
            ctrl.t.set(translation)
            ctrl.r.set(rotate)
            ctrl.s.set(scale)
            rig.transformToOffsetMatrix(ctrl)
            rig.lockAndHideCompound(ctrl, ['r', 's'])
            mid_ctrl = ctrl

        # end
        elif transform == transforms[-1]:
            ctrl, _ = control.create(transform,
                                     name=name,
                                     axis=axis,
                                     parent=control_parent,
                                     shape=pipernode.createIK,
                                     control_shape=shape)
        else:
            ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=shape)

        controls.append(ctrl)

    start_control = controls[1]
    piper_ik = controls[-1]
    piper_ik.startInitialLength.set(start_initial_length)
    piper_ik.endInitialLength.set(end_initial_length)

    if axis.startswith('n'):
        piper_ik.outputScale.set(-1)

    rig.parentMatrixConstraint(start_control, start, t=True, r=False, s=False)
    rig.parentMatrixConstraint(piper_ik, end, t=False)
    ik_handle, effector = pm.ikHandle(sj=start, ee=end, sol='ikRPsolver', n=end.nodeName() + '_handle', pw=1, w=1)
    rig.parentMatrixConstraint(piper_ik, ik_handle, r=False, s=False)
    rig.poleVectorMatrixConstraint(ik_handle, mid_ctrl)

    # connect the rest
    start_control.worldMatrix >> piper_ik.startMatrix
    mid_ctrl.worldMatrix >> piper_ik.poleVectorMatrix
    piper_ik.worldMatrix >> piper_ik.endMatrix
    piper_ik.startOutput >> mid.attr('t' + axis.lstrip('n'))
    piper_ik.endOutput >> end.attr('t' + axis.lstrip('n'))
    piper_ik.twist >> ik_handle.twist
    piper_ik._.lock()

    return controls
