#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.util as myu
import piper.mayapy.pipernode as pipernode
import piper.mayapy.pipermath as pipermath
import piper.mayapy.attribute as attribute
import piper.mayapy.convert as convert

from . import xform
from . import space
from . import curve
from . import control
from . import switcher


def dynamicPivot(transform, target=None, shape=curve.square, axis=None, color='burnt orange', scale=1, size=None):
    """
    Creates a dynamic pivot at the given transform driving the given target.

    Args:
        transform (pm.nodetypes.Transform): Transform to create dynamic pivot at.

        target (pm.nodetypes.Transform): Transform to drive with dynamic pivot.

        shape (method): Used to create curve or visual representation of FK control.

        axis (string): Orientation for control made.

        color (string): Color for control.

        scale (float): Multiplied times size.

        size (list): X, Y, Z sizes of control.

    Returns:
        (pm.nodetypes.Transform): Control created.
    """
    if not target:
        target = transform

    pivot_ctrl, _ = control.create(transform,
                                   shape=shape,
                                   name=target.name() + pcfg.dynamic_pivot_suffix,
                                   axis=axis,
                                   color=color,
                                   scale=scale,
                                   parent=target,
                                   matrix_offset=False,
                                   size=size)

    pivot_ctrl.translate >> target.rotatePivot
    attribute.nonKeyableCompound(pivot_ctrl, ['r', 's'])
    pivot_ctrl.addAttr(pcfg.dynamic_pivot_rest, dt='string', k=False, h=True, s=True)
    pivot_ctrl.attr(pcfg.dynamic_pivot_rest).set(transform.name())
    return pivot_ctrl


def _getAxis(i, transforms, duplicates=None):
    """
    Attempts to figure out the axis for the given iteration of the given transforms and/or duplicates.

    Args:
        i (int): Iteration count.

        transforms (list): Transforms to use to get orient axis.

        duplicates (list): Duplicates of transforms

    Returns:
        (string): Axis calculated from orientation of current iteration and next iteration.
    """
    axis = None

    if not duplicates:
        duplicates = transforms

    if duplicates[i] != duplicates[-1]:
        axis_vector = pipermath.getOrientAxis(duplicates[i], duplicates[i + 1])
        axis = convert.axisToString(axis_vector)

    # attempt to deduce axis if transform only has one child and axis is not given
    elif len(transforms) == 1 and transforms[0].getChildren() and len(transforms[0].getChildren()) == 1:
        axis_vector = pipermath.getOrientAxis(transforms[0], transforms[0].getChildren()[0])
        axis = convert.axisToString(axis_vector)

    return axis


def simpleFK(start, end=None, parent=None, axis=None, shape=curve.circle, sizes=None):
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
        size = sizes[i] if sizes else None
        calc_axis = axis if axis else _getAxis(i, transforms)
        control_parent = parent if transform == transforms[0] else controls[i - 1]
        ctrl, _ = control.create(transform, shape, transform.name(), calc_axis, parent=control_parent, size=size)
        xform.parentMatrixConstraint(ctrl, transform, message=True)
        controls.append(ctrl)

    return controls


def FK(start, end=None, parent=None, axis=None, shape=curve.circle, sizes=None, connect=True):
    """
    Creates FK controls for the transform chain deduced by the start and end transforms.

    Args:
        start (pm.nodetypes.Transform): Start of the chain to be driven by FK controls.

        end (pm.nodetypes.Transform): End of the chain to be driven by FK controls. If none given, will only drive start

        parent (pm.nodetypes.Transform): If given, will drive the start control through parent matrix constraint.

        axis (string): Only used if no end joint given for shape's axis to match rotations.

        shape (method): Used to create curve or visual representation of FK control.

        sizes (list): Sizes to use for each control.

        connect (bool): If True, connects the duplicate FK chain to the given start/end transforms to be driven.

    Returns:
        (list): Controls created in order from start to end.
    """
    controls = []
    in_controls = []
    transforms = xform.getChain(start, end)
    duplicates = xform.duplicateChain(transforms, prefix=pcfg.fk_prefix, color='green', scale=0.5)

    for i, duplicate in enumerate(duplicates):

        if not axis:
            axis = _getAxis(i, transforms, duplicates)

        name = duplicate.name()
        calc_axis = axis if axis else _getAxis(i, transforms)
        size = sizes[i] if sizes else control.calculateSize(transforms[i])
        ctrl_parent = parent if duplicate == duplicates[0] else controls[i - 1]
        ctrl, _ = control.create(duplicate, shape, name, calc_axis, parent=ctrl_parent, size=size, scale=1.2)
        controls.append(ctrl)

        xform.offsetConstraint(ctrl, duplicate, message=True)
        in_ctrl, _ = control.create(duplicate, name=name + '_inner', axis=axis, shape=curve.plus, size=size,
                                    parent=ctrl, color='burnt orange', inner=.125, matrix_offset=True)
        xform.parentMatrixConstraint(in_ctrl, duplicate)
        in_controls.append(in_ctrl)

        transform_parent = transforms[i].getParent()
        spaces = [transform_parent, ctrl_parent]
        spaces = filter(None, spaces)

        if spaces:
            space.create(spaces, in_ctrl)

        if connect:
            xform.parentMatrixConstraint(duplicate, transforms[i])

    return duplicates, controls + in_controls


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
    mid_ctrl = None
    inner_ctrl = None
    start_ctrl = None
    controls = []

    if mid == start or mid == end:
        pm.error('Not enough joints given! {} is the mid joint?'.format(mid.name()))

    start_initial_length = pipermath.getDistance(start, mid)
    end_initial_length = pipermath.getDistance(mid, end)

    for i, transform in enumerate(transforms):
        name = transform.name()
        size = sizes[i] if sizes else None
        control_parent = parent if transform == transforms[0] else None

        if transform != transforms[-1]:
            next_transform = transforms[i + 1]
            axis_vector = pipermath.getOrientAxis(transform, next_transform)
            axis = convert.axisToString(axis_vector)

        # start
        if transform == transforms[0]:
            ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=shape, size=size)
            start_ctrl = ctrl
            attribute.lockAndHide(ctrl.scale)
            scale_ctrl, _ = control.create(transform, name=name + '_scale', axis=axis, scale=0.75, parent=ctrl,
                                           shape=curve.plus, matrix_offset=False, size=size)

            xform.parentMatrixConstraint(transform, scale_ctrl, t=False, r=True, s=False)
            attribute.lockAndHideCompound(scale_ctrl, ['t', 'r'])
            scale_ctrl.s >> transform.s
            controls.append(scale_ctrl)

        # mid
        elif transform == mid:
            ctrl, _ = control.create(transform, curve.orb, name, axis, scale=0.01, matrix_offset=False, size=size)
            translation, rotate, scale, _ = xform.calculatePoleVector(start, mid, end)
            pm.xform(ctrl, t=translation, ro=rotate, s=scale)
            mid_ctrl = ctrl

        # end
        elif transform == transforms[-1]:
            ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=pipernode.createIK,
                                     control_shape=shape, size=size)
            inner_ctrl, _ = control.create(transform, curve.plus, 'inner_' + name, axis, color='burnt orange',
                                           parent=ctrl, size=size, matrix_offset=True, inner=.125)

            attribute.lockAndHideCompound(inner_ctrl, ['r', 's'])
            controls.append(inner_ctrl)
        else:
            ctrl, _ = control.create(transform, name=name, axis=axis, parent=control_parent, shape=shape, size=size)

        controls.append(ctrl)

    piper_ik = controls[-1]
    piper_ik.startInitialLength.set(start_initial_length)
    piper_ik.endInitialLength.set(end_initial_length)

    if axis.startswith('n'):
        piper_ik.outputScale.set(-1)

    # connect controls to joints, and make ik handle
    xform.parentMatrixConstraint(start_ctrl, start, t=True, r=False, s=False)
    xform.parentMatrixConstraint(piper_ik, end, t=False)
    ik_handle, effector = pm.ikHandle(sj=start, ee=end, sol='ikRPsolver', n=end.name() + '_handle', pw=1, w=1)
    xform.parentMatrixConstraint(piper_ik, ik_handle, r=False, s=False)
    # xform.poleVectorMatrixConstraint(ik_handle, mid_ctrl)
    constraint = pm.poleVectorConstraint(mid_ctrl, ik_handle)
    constraint.target[0].targetWeight.disconnect()  # disconnecting unused cycled connection

    # connect the rest
    start_ctrl.worldMatrix >> piper_ik.startMatrix
    mid_ctrl.worldMatrix >> piper_ik.poleVectorMatrix
    piper_ik.worldMatrix >> piper_ik.endMatrix
    piper_ik.startOutput >> mid.attr('t' + axis.lstrip('n'))
    piper_ik.twist >> ik_handle.twist
    piper_ik._.lock()

    # inner control connections
    inner_negate = pm.createNode('multiplyDivide', n=inner_ctrl.name() + '_negate')
    inner_ctrl.t >> inner_negate.input1
    inner_negate.input2.set([-1, -1, -1])

    inner_plus = pm.createNode('plusMinusAverage', n=inner_ctrl.name() + '_plus')
    inner_negate.output >> inner_plus.input3D[0]
    piper_ik.endOutput >> inner_plus.attr('input3D[1].input3D' + axis.lstrip('n'))
    inner_plus.output3D >> end.t

    # parent pole vector to end control and create
    pm.parent(mid_ctrl, piper_ik)
    xform.toOffsetMatrix(mid_ctrl)
    space.create([start_ctrl], mid_ctrl)
    mid_ctrl.useScale.set(False)
    attribute.lockAndHideCompound(mid_ctrl, ['r', 's'])

    return controls


def FKIK(start, end, parent=None, axis=None, fk_shape=curve.circle, ik_shape=curve.ring, proxy=True):
    """
    Creates a FK and IK controls that drive the chain from start to end.

    Args:
        start (pm.nodetypes.Transform): Start of the chain to be driven by FK controls.

        end (pm.nodetypes.Transform): End of the chain to be driven by FK controls. If none given, will only drive start

        parent (pm.nodetypes.Transform): If given, will drive the start control through parent matrix constraint.

        axis (string): Only used if no end joint given for shape's axis to match rotations.

        fk_shape (method): Used to create curve or visual representation for the FK controls.

        ik_shape (method): Used to create curve or visual representation for the IK controls.

        proxy (boolean): If True, adds a proxy FK_IK attribute to all controls.

    Returns:
        (list): Two lists, FK and IK controls created in order from start to end respectively.
    """
    # create joint chains that is the same as the given start and end chain for FK and IK then create controls on those
    transforms = xform.getChain(start, end)
    sizes = [control.calculateSize(transform) for transform in transforms]
    ik_transforms = xform.duplicateChain(transforms, pcfg.ik_prefix, color='purple', scale=0.5)
    fk_transforms, fk_controls = FK(start, end, parent=parent, axis=axis, shape=fk_shape, sizes=sizes, connect=False)
    ik_controls = IK(ik_transforms[0], ik_transforms[-1], parent=parent, shape=ik_shape, sizes=sizes)
    controls = fk_controls + ik_controls

    # create the switcher control and add the transforms, fk, and iks to its attribute to store it
    switcher_control = switcher.create(end, end.name())
    switcher_attribute = switcher_control.attr(pcfg.fk_ik_attribute)
    switcher.addData(switcher_control.attr(pcfg.switcher_transforms), transforms, names=True)
    switcher.addData(switcher_control.attr(pcfg.switcher_fk), fk_controls, names=True)
    switcher.addData(switcher_control.attr(pcfg.switcher_ik), ik_controls, names=True)
    controls.insert(0, switcher_control)

    # one minus the output of the fk ik attribute in order to drive visibility of ik/fk controls
    negative_one = pm.createNode('multDoubleLinear', n=switcher_control.name() + '_negativeOne')
    switcher_attribute >> negative_one.input1
    negative_one.input2.set(-1)

    plus_one = pm.createNode('plusMinusAverage', n=switcher_control.name() + '_plusOne')
    negative_one.output >> plus_one.input1D[0]
    plus_one.input1D[1].set(1)

    [plus_one.output1D >> fk.lodVisibility for fk in fk_controls]
    [switcher_attribute >> ik.lodVisibility for ik in ik_controls]

    # use spaces to drive original chain with fk and ik transforms and hook up switcher attributes
    for original_transform, fk_transform, ik_transform in zip(transforms, fk_transforms, ik_transforms):
        world_space, fk_space, ik_space = space.create([fk_transform, ik_transform], original_transform, direct=True)
        original_transform.attr(fk_space).set(1)
        switcher_attribute >> original_transform.attr(ik_space)

    if not proxy:
        return controls

    # make proxy fk ik attribute on all the controls
    switcher_control.visibility.set(False)
    for ctrl in controls:
        attribute.addSeparator(ctrl)
        ctrl.addAttr(pcfg.proxy_fk_ik, proxy=switcher_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)

    return fk_transforms, ik_transforms, controls


def banker(joint, ik_control, pivot_track=None, side='', use_track_shape=True):
    """
    Creates a reverse foot control that changes pivot based on curve shape and control rotation input.
    Useful for banking.

    Args:
        joint (pm.nodetypes.Joint): Joint that will be driven by the reverse module and IK handle.

        ik_control (pm.nodetypes.Transform): Control that drives the IK Handle.

        pivot_track (pm.nodetypes.Transform): With a NurbsCurve shape as child that will act as the track for the pivot.

        side (string or None): Side to generate cross section

        use_track_shape (boolean): If True, will use the pivot track shape as the control shape

    Returns:
        (pm.nodetypes.Transform): Control that moves the reverse foot pivot.
    """
    joint_name = joint.name()
    prefix = joint_name + '_'
    axis = pipermath.getOrientAxis(joint.getParent(), joint)
    axes = convert.axisToTriAxis(axis)

    if not side:
        side = pcu.getSide(joint_name)

    # get the IK handle and validate there is only one
    ik_handle = ik_control.connections(skipConversionNodes=True, type='ikHandle')
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
        switcher_control = switcher.get(ik_control)
        transforms = switcher.getData(switcher_control.attr(pcfg.switcher_transforms), cast=True)
        size = control.calculateSize(transforms[-1])
    else:
        size = None

    if use_track_shape:
        ctrl = pm.duplicate(pivot_track, n=prefix + 'bank')[0]
        curve.color(ctrl, 'burnt orange')
    else:
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

    # need to multiply the rotation by -1
    negative_mult = pm.createNode('multDoubleLinear', n=prefix + 'negative')
    ctrl.attr('r' + axes[2]) >> negative_mult.input1
    negative_mult.input2.set(-1)
    normalize_input_attribute = negative_mult.output

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

    # curve_info position is where the pivot goes! Connect something to it if you want to visualize it
    ctrl.r >> pivot.r
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
    ik_control.attr(pcfg.banker_attribute).set(ctrl.name())

    # hook up pivot control with fk_ik attribute if ik has an fk-ik proxy
    if ik_control.hasAttr(pcfg.proxy_fk_ik):
        switcher_control = switcher.get(ik_control)
        switcher_attribute = switcher_control.attr(pcfg.fk_ik_attribute)
        switcher_attribute >> ctrl.lodVisibility
        attribute.addSeparator(ctrl)
        ctrl.addAttr(pcfg.proxy_fk_ik, proxy=switcher_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)

    return ctrl


def reverse(driver, target, driven_negate=None, transform=None, switcher_ctrl=None, shape=curve.square, axis=None):
    """
    Creates a control that offsets the given target through rotation (usually foot roll reverse rig).

    Args:
        driver (pm.nodetypes.Transform): The transform that drives the whole chain. Usually the IK handle.

        target (pm.nodetypes.Transform): Transform that will have control rotations added to. Usually end joint.

        driven_negate (pm.nodetypes.Transform): Transform that will have control rotations subtracted from.
        Usually any controls further down the chain/hierarchy of the given target.

        transform (pm.nodetypes.Transform): Transform for making the control. Useful for figuring out control size too.
        If None given, will try to use given driven_negate, if no driven_negate, will try to use given target.

        switcher_ctrl (pm.nodetypes.Transform): Transform that handles switching between FK and IK chains.

        shape (method): Creates the shape control that will drive reverse rig system.

        axis (string): Direction control will be facing when created.

    Returns:
        (pm.nodetypes.Transform): Control created.
    """
    if not transform:
        transform = driven_negate if driven_negate else target

    # attempt to deduce axis if transform only has one child and axis is not given
    if not axis and transform.getChildren() and len(transform.getChildren()) == 1:
        axis_vector = pipermath.getOrientAxis(transform, transform.getChildren()[0])
        axis = convert.axisToString(axis_vector)
        axis = convert.axisToTriAxis(axis)[1]

    # create control
    name = transform.name() + '_reverse'
    driver_parent = driver.getParent()
    ctrl, _ = control.create(transform, shape, name, axis, 'burnt orange', 0.5, True, parent=driver_parent)

    name = ctrl.name()
    pm.parent(driver, ctrl)
    attribute.lockAndHideCompound(ctrl, ['t', 's'])
    target_source = target.rotate.connections(scn=True, plugs=True, destination=False)

    # add control's rotation to whatever is connected to target's rotate.
    if target_source:
        target_source = target_source[0]
        plus = pm.createNode('plusMinusAverage', n='_'.join([target.name(), 'plus', ctrl.name()]))
        target_source >> plus.input3D[0]
        ctrl.rotate >> plus.input3D[1]
        plus.output3D >> target.rotate
    else:
        ctrl.rotate >> target.rotate

    # if no driven negate given or driven negate is not being offset by the offsetParentMatrix, we are finished here
    if not driven_negate or not driven_negate.offsetParentMatrix.connections(scn=True, plugs=True, destination=False):
        return ctrl

    # decompose and compose matrices to get rotation value subtracted with control's rotation
    source_matrix = driven_negate.offsetParentMatrix.connections(scn=True, plugs=True, destination=False)[0]
    source_name = source_matrix.node().name()
    decomp_matrix = pm.createNode('decomposeMatrix', n=source_name + '_DM')
    compose_matrix = pm.createNode('composeMatrix', n=source_name + '_CM')

    source_matrix >> decomp_matrix.inputMatrix
    decomp_matrix.outputTranslate >> compose_matrix.inputTranslate
    decomp_matrix.outputScale >> compose_matrix.inputScale

    minus = pm.createNode('plusMinusAverage', n='_'.join([source_name, 'minus', name]))
    minus.operation.set(2)
    decomp_matrix.outputRotate >> minus.input3D[0]
    ctrl.rotate >> minus.input3D[1]
    minus.output3D >> compose_matrix.inputRotate
    compose_matrix.outputMatrix >> driven_negate.offsetParentMatrix
    attribute.addReverseMessage(ctrl, driven_negate)

    if switcher_ctrl:
        # add reverse control to switcher data and connect ik visibility onto reverse control
        switcher.addData(switcher_ctrl.attr(pcfg.switcher_reverses), [name])
        switcher_attribute = switcher_ctrl.attr(pcfg.fk_ik_attribute)
        switcher_attribute >> ctrl.lodVisibility

        # add proxy fk_ik attribute to ctrl
        attribute.addSeparator(ctrl)
        ctrl.addAttr(pcfg.proxy_fk_ik, proxy=switcher_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)

        # only make driven_negate by affected if IK is set to True
        blend = pm.createNode('blendMatrix', n=source_name + '_negateBlend')
        source_matrix >> blend.inputMatrix
        compose_matrix.outputMatrix >> blend.target[0].targetMatrix
        switcher_attribute >> blend.target[0].weight
        blend.outputMatrix >> driven_negate.offsetParentMatrix

    return ctrl
