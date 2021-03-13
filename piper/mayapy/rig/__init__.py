#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.util as myu
import piper.mayapy.pipernode as pipernode
import piper.mayapy.pipermath as pipermath
import piper.mayapy.attribute as attribute
import piper.mayapy.convert as convert

import xform
import space
import curve
import control


def FK(start, end=None, parent=None, axis=None, shape=curve.circle, sizes=None):
    """
    Creates FK controls for the transform chain deduced by the start and end transforms.

    Args:
        start (pm.nodetypes.Transform): Start of the chain to be driven by FK controls.

        end (pm.nodetypes.Transform): End of the chain to be driven by FK controls. If none given, will only drive start

        parent (pm.nodetypes.Transform): If given, will drive the start control through parent matrix constraint.

        axis (string): Only used if no end joint given for shape's axis to match rotations.

        shape (method): Used to create curve or visual representation of FK control.

        sizes (list): Sizes to use for each control.

    Returns:
        (list): Controls created in order from start to end.
    """
    controls = []
    transforms = xform.getChain(start, end)

    for i, transform in enumerate(transforms):
        if transform != transforms[-1]:
            next_transform = transforms[i + 1]
            axis_vector = pipermath.getOrientAxis(transform, next_transform)
            axis = convert.axisToString(axis_vector)

        name = transform.nodeName()
        size = sizes[i] if sizes else None
        control_parent = parent if transform == transforms[0] else controls[i - 1]
        ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=shape, size=size)
        xform.parentMatrixConstraint(ctrl, transform)
        controls.append(ctrl)

    return controls


def IK(start, end, parent=None, shape=curve.ring, sizes=None):
    """
    Creates IK controls and IK RP solver and for the given start and end joints.

    Args:
        start (pm.nodetypes.Joint): Start of the joint chain.

        end (pm.nodetypes.Joint): End of the joint chain.

        parent (pm.nodetypes.Transform): Parent of start control.

        shape (method): Creates the shape control that will drive joints.

        sizes (list): Sizes to use for each control.

    Returns:
        (list): Controls created in order from start to end.
    """
    transforms = xform.getChain(start, end)
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
        size = sizes[i] if sizes else None
        control_parent = parent if transform == transforms[0] else None

        if transform != transforms[-1]:
            next_transform = transforms[i + 1]
            axis_vector = pipermath.getOrientAxis(transform, next_transform)
            axis = convert.axisToString(axis_vector)

        # start
        if transform == transforms[0]:
            ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=shape, size=size)

            attribute.lockAndHide(ctrl.scale)
            scale_ctrl, _ = control.create(transform, name=name + '_scale', axis=axis, scale=0.75, parent=ctrl,
                                           shape=curve.plus, matrix_offset=False, size=size)

            xform.parentMatrixConstraint(transform, scale_ctrl, t=False, s=False)
            attribute.lockAndHideCompound(scale_ctrl, ['t', 'r'])
            scale_ctrl.s >> transform.s
            controls.append(scale_ctrl)

            # dynamic pivot
            pivot_ctrl, _ = control.create(start, shape=curve.fourArrows, name=name + '_pivot', scale=0.6, axis=axis,
                                           parent=ctrl, matrix_offset=False, size=size)

            pivot_ctrl.translate >> ctrl.rotatePivot
            attribute.nonKeyableCompound(pivot_ctrl, ['r', 's'])
            controls.append(pivot_ctrl)

        # mid
        elif transform == mid:
            ctrl, _ = control.create(transform, curve.orb, name, axis, scale=0.01, parent=control_parent,
                                     matrix_offset=False, size=size)

            translation, rotate, scale = xform.calculatePoleVector(start, mid, end)
            pm.xform(ctrl, t=translation, ro=rotate, s=scale)
            mid_control = ctrl

        # end
        elif transform == transforms[-1]:
            ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=pipernode.createIK,
                                     control_shape=shape, size=size)
        else:
            ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=shape, size=size)

        controls.append(ctrl)

    start_control = controls[2]
    piper_ik = controls[-1]
    piper_ik.startInitialLength.set(start_initial_length)
    piper_ik.endInitialLength.set(end_initial_length)

    if axis.startswith('n'):
        piper_ik.outputScale.set(-1)

    # connect controls to joints, and make ik handle
    xform.parentMatrixConstraint(start_control, start, t=True, r=False, s=False)
    xform.parentMatrixConstraint(piper_ik, end, t=False)
    ik_handle, effector = pm.ikHandle(sj=start, ee=end, sol='ikRPsolver', n=end.nodeName() + '_handle', pw=1, w=1)
    xform.parentMatrixConstraint(piper_ik, ik_handle, r=False, s=False)
    xform.poleVectorMatrixConstraint(ik_handle, mid_control)

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
    xform.toOffsetMatrix(mid_control)
    space.create([start_control], mid_control)
    mid_control.useScale.set(False)
    attribute.lockAndHideCompound(mid_control, ['r', 's'])

    return controls


def FKIK(start, end, parent=None, axis=None, fk_shape=curve.circle, ik_shape=curve.ring, proxy=True):
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
    transforms = xform.getChain(start, end)
    sizes = [control.calculateSize(transform) for transform in transforms]
    fk_transforms = xform.duplicateChain(transforms, pcfg.fk_prefix, color='green')
    ik_transforms = xform.duplicateChain(transforms, pcfg.ik_prefix, color='purple')
    fk_controls = FK(fk_transforms[0], fk_transforms[-1], parent=parent, axis=axis, shape=fk_shape, sizes=sizes)
    ik_controls = IK(ik_transforms[0], ik_transforms[-1], parent=parent, shape=ik_shape, sizes=sizes)
    controls = fk_controls + ik_controls

    # create the switcher control that holds the fk to ik attribute and make the end transform drive it
    switcher_control, _ = control.create(end,
                                         name=end.nodeName() + pcfg.switcher_suffix,
                                         axis=axis,
                                         shape=curve.cube,
                                         scale=0.5)

    attribute.addSeparator(switcher_control)
    end.worldMatrix >> switcher_control.offsetParentMatrix
    attribute.nonKeyableCompound(switcher_control)
    switcher_control.addAttr(pcfg.fk_ik_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)
    switcher_attribute = switcher_control.attr(pcfg.fk_ik_attribute)
    switcher_control.addAttr(pcfg.switcher_transforms, dt='string', k=False, h=True, s=True)
    switcher_control.addAttr(pcfg.switcher_fk, dt='string', k=False, h=True, s=True)
    switcher_control.addAttr(pcfg.switcher_ik, dt='string', k=False, h=True, s=True)
    switcher_control.attr(pcfg.switcher_transforms).set(', '.join([node.nodeName() for node in transforms]))
    switcher_control.attr(pcfg.switcher_fk).set(', '.join([fk.nodeName() for fk in fk_controls]))
    switcher_control.attr(pcfg.switcher_ik).set(', '.join([ik.nodeName() for ik in ik_controls]))

    # one minus the output of the fk ik attribute in order to drive visibility of ik/fk controls
    negative_one = pm.createNode('multDoubleLinear', n=switcher_control.nodeName() + '_negativeOne')
    switcher_attribute >> negative_one.input1
    negative_one.input2.set(-1)

    plus_one = pm.createNode('plusMinusAverage', n=switcher_control.nodeName() + '_plusOne')
    negative_one.output >> plus_one.input1D[0]
    plus_one.input1D[1].set(1)

    [plus_one.output1D >> fk.lodVisibility for fk in fk_controls]
    [switcher_attribute >> ik.lodVisibility for ik in ik_controls]

    # use spaces to drive original chain with fk and ik transforms and hook up switcher attributes
    for original_transform, fk_transform, ik_transform in zip(transforms, fk_transforms, ik_transforms):
        world_space, fk_space, ik_space = space.create([fk_transform, ik_transform], original_transform)
        original_transform.attr(fk_space).set(1)
        switcher_attribute >> original_transform.attr(ik_space)

        # make joints smaller so that they are easier to visualize
        if original_transform.hasAttr('radius'):
            fk_transform.radius.set(fk_transform.radius.get() * .5)
            ik_transform.radius.set(ik_transform.radius.get() * .5)

    if not proxy:
        return controls

    # make proxy fk ik attribute on all the controls
    switcher_control.visibility.set(False)
    for ctrl in controls:
        attribute.addSeparator(ctrl)
        ctrl.addAttr(pcfg.proxy_fk_ik, proxy=switcher_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)

    return controls


def banker(joint, ik_control, pivot_track=None, side=''):
    """
    Creates a reverse foot control that changes pivot based on curve shape and control rotation input.
    Useful for banking.

    Args:
        joint (pm.nodetypes.Joint): Joint that will be driven by the reverse module and IK handle.

        ik_control (pm.nodetypes.Transform): Control that drives the IK Handle.

        pivot_track (pm.nodetypes.Transform): With a NurbsCurve shape as child that will act as the track for the pivot.

        side (string or None): Side to generate cross section

    Returns:
        (pm.nodetypes.Transform): Control that moves the reverse foot pivot.
    """
    joint_name = joint.nodeName()
    prefix = joint_name + '_'
    axis = pipermath.getOrientAxis(joint.getParent(), joint)
    is_negative = convert.axisToString(axis).startswith('n')
    axes = convert.axisToTriAxis(axis)

    # get the IK handle and validate there is only one
    ik_handle = ik_control.listConnections(skipConversionNodes=True, type='ikHandle')
    if len(ik_handle) != 1:
        pm.error('Needed only ONE ik_handle. {} found.'.format(str(len(ik_handle))))

    ik_handle = ik_handle[0]

    # create a pivot track (cross section curve) if no pivot track (curve) is given
    if not pivot_track:

        # if IK joint given, get the name of the regular joint by stripping the ik prefix
        if joint_name.startswith(pcfg.ik_prefix):
            stripped_name = pcu.removePrefixes(joint_name, pcfg.ik_prefix)
            search_joint = pm.PyNode(stripped_name)
        else:
            search_joint = joint

        # tries to get the meshes influenced by the skin cluster connected to the joint
        skins = search_joint.future(type='skinCluster')
        meshes = {mesh for skin in skins for mesh in pm.skinCluster(skin, q=True, g=True)} if skins else None

        # create the pivot track curve
        pm.select(cl=True)
        pivot_track = curve.originCrossSection(meshes, side=side, name=prefix + 'pivotTrack')

        # validate that only one is made
        if len(pivot_track) != 1:
            pm.error('Needed only ONE curve! {} curves made. Try to specify a side.'.format(str(len(pivot_track))))

        pivot_track = pivot_track[0]

    # create the pivot and the normalized pivot, move the norm pivot to joint and then to floor
    pivot = pm.group(em=True, name=prefix + 'Pivot')
    normalized_pivot = pm.group(em=True, name=prefix + 'normalizedPivot')
    pm.matchTransform(normalized_pivot, joint, pos=True, rot=False, scale=False)
    normalized_pivot.ty.set(0)
    xform.toOffsetMatrix(normalized_pivot)

    # figure out control size, create control, lock and hide axis, translate, and scale
    if ik_control.hasAttr(pcfg.proxy_fk_ik):
        switcher = control.getSwitcher(ik_control)
        transforms = space.getAll(switcher, pcfg.switcher_transforms, cast=True)
        size = control.calculateSize(transforms[-1])
    else:
        size = None

    ctrl, _ = control.create(joint, shape=curve.plus, name=prefix + 'bank', axis=axes[0], color='burnt orange',
                             matrix_offset=True, size=size, inner=.125, outer=1.25)

    attribute.lockAndHide(ctrl.attr('r' + axes[0]))
    attribute.lockAndHideCompound(ctrl, ['t', 's'])

    # node to add small number
    small_add = pm.createNode('plusMinusAverage', n=prefix + 'plusSmallNumber')
    small_add.input1D[0].set(0.001)

    normalize_node = pm.createNode('vectorProduct', n=prefix + 'pivotNormal')
    normalize_node.operation.set(0)
    normalize_node.normalizeOutput.set(True)

    # adding a small amount to avoid division by zero
    ctrl.attr('r' + axes[1]) >> small_add.input1D[1]
    small_add.output1D >> normalize_node.attr('input1' + axes[2].upper())

    # if axis is negative, we need to multiply the rotation by -1
    if is_negative:
        negative_mult = pm.createNode('multDoubleLinear', n=prefix + 'negative')
        ctrl.attr('r' + axes[2]) >> negative_mult.input1
        negative_mult.input2.set(-1)
        normalize_input_attribute = negative_mult.output
    else:
        normalize_input_attribute = ctrl.attr('r' + axes[2])

    normalize_input_attribute >> normalize_node.attr('input1' + axes[1].upper())
    normalize_node.output >> normalized_pivot.translate

    # creating the normalized (circle) version of the cross section
    positions = []
    duplicate_curve = pm.duplicate(pivot_track)[0]
    pm.move(0, 0, 0, duplicate_curve, rpr=True)
    cvs = duplicate_curve.numCVs()
    for cv in range(0, cvs):
        position = duplicate_curve.cv[cv].getPosition(space='world')
        position.normalize()
        positions.append(position)

    # delete the duplicate and finally make the normalize track. Make sure to close the curve and center pivots
    pm.delete(duplicate_curve)
    normalized_track = pm.curve(d=1, p=positions, k=range(len(positions)), ws=True, n=prefix + 'normalizedTrack')
    normalized_track = pm.closeCurve(normalized_track, replaceOriginal=True)[0]
    pm.xform(normalized_track, centerPivots=True)

    # move normalized track to joint, then to floor, and freeze transforms
    pm.matchTransform(normalized_track, joint, pos=True, rot=False, scale=False)
    normalized_track.ty.set(0)
    myu.freezeTransformations(normalized_track)

    decomposed_matrix = pm.createNode('decomposeMatrix', n=normalize_node + '_decompose')
    normalized_pivot.worldMatrix >> decomposed_matrix.inputMatrix

    nearest_point = pm.createNode('nearestPointOnCurve', n=prefix + 'nearestPoint')
    decomposed_matrix.outputTranslate >> nearest_point.inPosition
    normalized_track.getShape().worldSpace >> nearest_point.inputCurve

    curve_info = pm.createNode('pointOnCurveInfo', n=prefix + 'curveInfo')
    nearest_point.parameter >> curve_info.parameter
    pivot_track.getShape().worldSpace >> curve_info.inputCurve

    reverse_group = pm.group(em=True, n=prefix + 'reverse_grp')
    xform.parentMatrixConstraint(ik_control, reverse_group, offset=True)
    pm.parent([pivot, ctrl], reverse_group)

    # if axis is negative, we do NOT need to multiply the rotation by -1
    if is_negative:
        ctrl.r >> pivot.r
    else:
        negative_rotation = pm.createNode('multiplyDivide', n=prefix + 'negativeRotation')
        ctrl.r >> negative_rotation.input1
        negative_rotation.attr('input2' + axes[2].upper()).set(-1)
        negative_rotation.output >> pivot.r

    # curve_info position is where the pivot goes! Connect something to it if you want to visualize it
    curve_info.result.position >> pivot.rotatePivot

    # connect ik handle by letting the pivot drive it
    ik_handle.t.disconnect()
    pm.parent(ik_handle, pivot)

    # make the pivot drive the joint's rotations
    joint.r.disconnect()
    xform.parentMatrixConstraint(pivot, joint, t=False, r=True, s=False, offset=True)

    # clean up by hiding curves
    pivot_track.visibility.set(False)
    normalized_track.visibility.set(False)

    ik_control.addAttr(pcfg.banker_attribute, dt='string', k=False, h=True, s=True)
    ik_control.attr(pcfg.banker_attribute).set(ctrl.nodeName())

    # hook up pivot control with fk_ik attribute if ik has an fk-ik proxy
    if ik_control.hasAttr(pcfg.proxy_fk_ik):
        switcher = control.getSwitcher(ik_control)
        switcher_attribute = switcher.attr(pcfg.fk_ik_attribute)
        switcher_attribute >> ctrl.lodVisibility
        attribute.addSeparator(ctrl)
        ctrl.addAttr(pcfg.proxy_fk_ik, proxy=switcher_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)

    return ctrl
