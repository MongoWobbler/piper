#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.rig.core as rig
import piper.mayapy.rig.space as space
import piper.mayapy.rig.curve as curve
import piper.mayapy.rig.control as control
import piper.mayapy.pipernode as pipernode
import piper.mayapy.pipermath as pipermath
import piper.mayapy.attribute as attribute
import piper.mayapy.convert as convert


def FK(start, end=None, parent=None, axis=None, shape=curve.circle):
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


def IK(start, end, parent=None, shape=curve.ring):
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
    mid_control = None
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
            attribute.lockAndHide(ctrl.scale)
            scale_ctrl, _ = control.create(transform,
                                           name=name + '_scale',
                                           axis=axis,
                                           scale=0.75,
                                           parent=ctrl,
                                           shape=curve.circle,
                                           matrix_offset=False)
            rig.parentMatrixConstraint(transform, scale_ctrl, t=False, s=False)
            attribute.lockAndHideCompound(scale_ctrl, ['t', 'r'])
            scale_ctrl.s >> transform.s
            controls.append(scale_ctrl)

            # dynamic pivot
            pivot_ctrl, _ = control.create(start, shape=curve.lever, name=name + '_pivot',
                                           axis=axis, parent=ctrl, matrix_offset=False)
            pivot_ctrl.translate >> ctrl.rotatePivot
            attribute.nonKeyableCompound(pivot_ctrl, ['r', 's'])
            controls.append(pivot_ctrl)

        # mid
        elif transform == mid:
            ctrl, _ = control.create(transform, curve.orb, name, axis, parent=control_parent, matrix_offset=False)
            translation, rotate, scale = rig.calculatePoleVectorTransform(start, mid, end)
            pm.xform(ctrl, t=translation, ro=rotate, s=scale)
            mid_control = ctrl

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

    start_control = controls[2]
    piper_ik = controls[-1]
    piper_ik.startInitialLength.set(start_initial_length)
    piper_ik.endInitialLength.set(end_initial_length)

    if axis.startswith('n'):
        piper_ik.outputScale.set(-1)

    # connect controls to joints, and make ik handle
    rig.parentMatrixConstraint(start_control, start, t=True, r=False, s=False)
    rig.parentMatrixConstraint(piper_ik, end, t=False)
    ik_handle, effector = pm.ikHandle(sj=start, ee=end, sol='ikRPsolver', n=end.nodeName() + '_handle', pw=1, w=1)
    rig.parentMatrixConstraint(piper_ik, ik_handle, r=False, s=False)
    rig.poleVectorMatrixConstraint(ik_handle, mid_control)

    # connect the rest
    start_control.worldMatrix >> piper_ik.startMatrix
    mid_control.worldMatrix >> piper_ik.poleVectorMatrix
    piper_ik.worldMatrix >> piper_ik.endMatrix
    piper_ik.startOutput >> mid.attr('t' + axis.lstrip('n'))
    piper_ik.endOutput >> end.attr('t' + axis.lstrip('n'))
    piper_ik.twist >> ik_handle.twist
    piper_ik._.lock()

    # parent pole vector to end control and create
    pm.parent(mid_control, piper_ik)
    rig.transformToOffsetMatrix(mid_control)
    space.create([start_control], mid_control)
    attribute.lockAndHideCompound(mid_control, ['r', 's'])

    return controls


def FKIK(start, end, parent=None, axis=None, fk_shape=curve.circle, ik_shape=curve.ring):
    """
    Creates a FK and IK controls that drive the chain from start to end.

    Args:
        Args:
        start (pm.nodetypes.Transform): Start of the chain to be driven by FK controls.

        end (pm.nodetypes.Transform): End of the chain to be driven by FK controls. If none given, will only drive start

        parent (pm.nodetypes.Transform): If given, will drive the start control through parent matrix constraint.

        axis (string): Only used if no end joint given for shape's axis to match rotations.

        fk_shape (method): Used to create curve or visual representation for the FK controls.

        ik_shape (method): Used to create curve or visual representation for the IK controls.

    Returns:
        (list): Two lists, FK and IK controls created in order from start to end respectively.
    """
    # create joint chains that is the same as the given start and end chain for FK and IK then create controls on those
    original_transforms = rig.getChain(start, end)
    fk_transforms = rig.duplicateChain(original_transforms, 'fk_', color='green')
    ik_transforms = rig.duplicateChain(original_transforms, 'ik_', color='purple')
    fk_controls = FK(fk_transforms[0], fk_transforms[-1], parent=parent, axis=axis, shape=fk_shape)
    ik_controls = IK(ik_transforms[0], ik_transforms[-1], parent=parent, shape=ik_shape)

    # create the switcher control that holds the fk to ik attribute and make the end transform drive it
    switcher_control, _ = control.create(end,
                                         name=end.nodeName() + pcfg.switcher_suffix,
                                         axis=axis,
                                         shape=curve.cube,
                                         scale=0.5)

    attribute.addSeparator(switcher_control)
    switcher_control.addAttr(pcfg.fk_ik_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)
    switcher_control.addAttr(pcfg.switcher_fk, dt='string', k=False, h=True, s=True)
    switcher_control.addAttr(pcfg.switcher_ik, dt='string', k=False, h=True, s=True)
    switcher_control.addAttr(pcfg.switcher_transforms, dt='string', k=False, h=True, s=True)
    switcher_control.attr(pcfg.switcher_fk).set(', '.join([fk.nodeName() for fk in fk_controls]))
    switcher_control.attr(pcfg.switcher_ik).set(', '.join([ik.nodeName() for ik in ik_controls]))
    switcher_control.attr(pcfg.switcher_transforms).set(', '.join([node.nodeName() for node in original_transforms]))
    end.worldMatrix >> switcher_control.offsetParentMatrix
    attribute.nonKeyableCompound(switcher_control)

    # use spaces to drive original chain with fk and ik transforms and hook up switcher attributes
    for original_transform, fk_transform, ik_transform in zip(original_transforms, fk_transforms, ik_transforms):
        world_space, fk_space, ik_space = space.create([fk_transform, ik_transform], original_transform)
        original_transform.attr(fk_space).set(1)
        switcher_control.attr(pcfg.fk_ik_attribute) >> original_transform.attr(ik_space)

        # make joints smaller so that they are easier to visualize
        if original_transform.hasAttr('radius'):
            fk_transform.radius.set(fk_transform.radius.get() * .5)
            ik_transform.radius.set(ik_transform.radius.get() * .5)

    return [fk_controls + ik_controls]