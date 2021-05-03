#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import inspect

import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.util as myu
import piper.mayapy.convert as convert
import piper.mayapy.attribute as attribute
import piper.mayapy.pipermath as pipermath
import piper.mayapy.pipernode as pipernode
import piper.mayapy.pipe.paths as paths
import piper.mayapy.ui.window as uiwindow

from . import bone
from . import xform
from . import space
from . import curve
from . import control
from . import switcher


def getMeshes():
    """
    Gets all the meshes inside all the piper skinned nodes in the scene.

    Returns:
        (set): Piper transforms that hold mesh shapes grouped under piper skinned nodes.
    """
    nodes = pipernode.get('piperSkinnedMesh')
    return {mesh.getParent() for skin in nodes for mesh in skin.getChildren(ad=True, type='mesh') if mesh.getParent()}


def setLockOnMeshes(lock):
    """
    Locks or unlocks all the transforms under piper skinned nodes that have mesh shapes.

    Args:
        lock (int): Mode to set on meshes. 0 is unlocked, 1 is locked.
    """
    meshes = getMeshes()
    for mesh in meshes:
        try:
            mesh.overrideEnabled.set(1)
            mesh.overrideDisplayType.set(lock)
        except RuntimeError as error:
            pm.warning('Can\'t set lock on mesh! ' + str(error))


def lockMeshes():
    """
    Locks all the transforms under piper skinned nodes that have mesh shapes.
    """
    setLockOnMeshes(2)


def unlockMeshes():
    """
    Unlocks all the transforms under piper skinned nodes that have mesh shapes.
    """
    setLockOnMeshes(0)


class Rig(object):

    def __init__(self, path='', rig=None, find=True, group=False):
        """
        Houses all rig scripts.

        Args:
            path (string): Path to skeletal mesh to prepare to start rigging.

            rig (pm.nodetypes.piperRig): Rig transform that holds all skinned meshes referenced.

            find (boolean): Will attempt to find piperRig node in scene if no rig or path is given.

            group (boolean): If True, will automatically parent nodes into the groups and/or into rig node.
        """
        self.rig = rig
        self.auto_group = group
        self.group_stack = {}

        if path:
            self.prepare(path)
        elif find and not rig:
            rigs = pm.ls(type='piperRig')

            if not rigs:
                pm.warning('No rigs found!')
            elif len(rigs) > 1:
                pm.warning('Found ' + str(len(rigs)) + ' rigs! Using ' + rigs[0].name())
                self.rig = rigs[0]
            else:
                self.rig = rigs[0]

    def prepare(self, path=''):
        """
        Prepares the scene for a rig.

        Returns:
            (pm.nodetypes.piperRig): Rig transform that holds all skinned meshes referenced.
        """
        if not path:
            path = pm.sceneName()

        # getRelativeArt checks if scene is saved
        skeleton_path = paths.getRelativeArt(path=path)
        rig_name, _ = os.path.splitext(os.path.basename(skeleton_path))
        rig_name = rig_name.split(pcfg.skinned_mesh_prefix)[-1]

        # if scene is modified, ask user if they would like to save, not save, or cancel operation
        if not uiwindow.save():
            pm.error('Scene not saved.')

        # open skeletal mesh to check for bone health
        if path != pm.sceneName():
            pm.openFile(path, force=True, esn=False, prompt=False)

        # perform a bone health check before referencing to emphasize any possible errors
        bone.health()

        # create new file, reference the skeleton into the new file, create rig group
        pm.newFile(force=True)
        self.rig = pipernode.createRig(name=rig_name)
        pm.createReference(skeleton_path, namespace=pcfg.skeleton_namespace)
        pm.createReference(skeleton_path, namespace=pcfg.bind_namespace)
        skinned_meshes = pipernode.get('piperSkinnedMesh')
        [node.visibility.set(False) for node in skinned_meshes if node.name().startswith(pcfg.bind_namespace)]
        pm.parent(skinned_meshes, self.rig)
        lockMeshes()

        return self.rig

    def addToGroupStack(self, parent, children):
        """
        Adds the given children as the value to the given parent key to the group_stack dictionary.

        Args:
            parent (pm.nodetypes.Transform): Node to add as key that things will be parented to.

            children (list): Nodes to parent to given parent.
        """
        current = self.group_stack.get(parent)
        self.group_stack[parent] = current + children if current else children

    def runGroupStack(self):
        """
        Parents all the given children to their corresponding parent key in the group stack dictionary.
        """
        [pm.parent(children, parent) for (parent, children) in self.group_stack.items()]
        self.group_stack.clear()

    def findGroup(self, reference_transform, transforms):
        """
        Finds the group the given transforms should be parented under based on given reference transform.

        Args:
            reference_transform (pm.nodetypes.Transform): Used to search parent hierarchy or group stack for parent.

            transforms (list): Nodes to parent.
        """
        found = False
        group_parent = None
        transform_parent = myu.getRootParent(reference_transform)

        # try to find the reference transform's parent in the group stack to figure out where it should be parented to
        for parent, children in self.group_stack.items():
            if transform_parent in children:
                group_parent = parent
                break

        # if found, add transform to the found parent
        if group_parent:
            self.addToGroupStack(group_parent, transforms)
            found = True

        # else get the first parent that is either a piperRig or is a group
        else:
            parent = myu.getFirstTypeOrEndsWithParent(reference_transform, 'piperRig', pcfg.group_suffix)
            if parent:
                self.addToGroupStack(parent, transforms)
                found = True

        if found and self.auto_group:
            self.runGroupStack()

    def organize(self, transforms, prefix=None, name=None):
        """
        Organizes the given transforms into a group if name given and into the rig node.

        Args:
            transforms (Iterable): Nodes to group and/or move into rig node.

            prefix (string): Prefix for group name. Usually calling function name.

            name (string): Name to give group.

        Returns:
            (pm.nodetypes.Transform): Group node made.
        """
        # preliminary checks, don't make group if no name given and there is no rig node
        if (name is None or not transforms) or (not name and not self.rig):
            return

        group = None
        if name:
            group = pm.group(name=prefix + '_' + name + pcfg.group_suffix, empty=True)
            attribute.lockAndHideCompound(group)

        parent_to_rig = transforms
        if group:
            # pm.parent(transforms, group) if self.auto_group else self.addToGroupStack(group, transforms)
            self.addToGroupStack(group, transforms)
            parent_to_rig = [group]

        if self.rig:
            # pm.parent(parent_to_rig, self.rig) if self.auto_group else self.addToGroupStack(group, transforms)
            self.addToGroupStack(self.rig, parent_to_rig)

            # drive visibility of groups through rig node
            if group:
                attribute_name = group.name() + pcfg.visibility_suffix
                self.rig.addAttr(attribute_name, at='bool', dv=1, k=True)
                self.rig.attr(attribute_name) >> group.visibility
                group.setAttr('visibility', k=False, cb=False)  # set hidden, still keyable even though k is False

        if self.auto_group:
            self.runGroupStack()

        return group

    def dynamicPivot(self, transform, target=None, shape=curve.square, axis=None, color='red', scale=1, size=None):
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
        self.organize([pivot_ctrl], prefix=inspect.currentframe().f_code.co_name, name='')
        return pivot_ctrl

    @staticmethod
    def _getAxis(i, transforms, last_axis, duplicates=None):
        """
        Attempts to figure out the axis for the given iteration of the given transforms and/or duplicates.

        Args:
            i (int): Iteration count.

            transforms (list): Transforms to use to get orient axis.

            duplicates (list): Duplicates of transforms

        Returns:
            (string): Axis calculated from orientation of current iteration and next iteration.
        """
        axis = last_axis

        if not duplicates:
            duplicates = transforms

        if duplicates[i] != duplicates[-1]:
            axis_vector = pipermath.getOrientAxis(duplicates[i], duplicates[i + 1])
            axis = convert.axisToString(axis_vector)

        # attempt to deduce axis if transform only has one child and axis is not given
        elif len(transforms) == 1 and transforms[0].getChildren() and len(transforms[0].getChildren()) == 1:
            axis_vector = pipermath.getOrientAxis(transforms[0], transforms[0].getChildren()[0])
            axis = convert.axisToString(axis_vector)

        last_axis = axis
        return axis, last_axis

    def FK(self, start, end='', parent=None, axis=None, shape='', sizes=None, connect=True, global_ctrl='', name=''):
        """
        Creates FK controls for the transform chain deduced by the start and end transforms.

        Args:
            start (pm.nodetypes.Transform): Start of the chain to be driven by FK controls.

            end (pm.nodetypes.Transform): End of the chain to be driven by FK controls.

            parent (pm.nodetypes.Transform): If given, will drive the start control through parent matrix constraint.

            axis (string): Only used if no end joint given for shape's axis to match rotations.

            shape (method): Used to create curve or visual representation of FK control.

            sizes (list): Sizes to use for each control.

            connect (bool): If True, connects the duplicate FK chain to the given start/end transforms to be driven.

            global_ctrl (pm.nodetypes.Transform): If given, will use this to drive global scale of piperIK control.

            name (str or None): Name to give group that will house all FK components.

        Returns:
            (list): Controls created in order from start to end.
        """
        if not shape:
            shape = curve.circle

        controls = []
        decomposes = []
        multiplies = []
        in_controls = []
        calc_axis = 'y'
        last_axis = axis
        transforms = xform.getChain(start, end)
        duplicates = xform.duplicateChain(transforms, prefix=pcfg.fk_prefix, color='green', scale=0.5)

        for i, (transform, duplicate) in enumerate(zip(transforms, duplicates)):
            dup_name = duplicate.name()
            calc_axis, last_axis = axis if axis else self._getAxis(i, transforms, last_axis, duplicates)
            size = sizes[i] if sizes else control.calculateSize(transform)
            ctrl_parent = parent if duplicate == duplicates[0] else controls[i - 1]

            ctrl = control.create(duplicate, pipernode.createFK, dup_name, calc_axis,
                                  scale=1.2, control_shape=shape, size=size)

            attribute.bindConnect(transform, ctrl, ctrl_parent)  # connects attributes that offset controls
            controls.append(ctrl)
            ctrl._.lock()

            xform.offsetConstraint(ctrl, duplicate, message=True)
            in_ctrl = control.create(duplicate, name=dup_name + '_inner', axis=calc_axis, shape=curve.plus, size=size,
                                     parent=ctrl, color='burnt orange', inner=.125, matrix_offset=True)

            decompose = xform.parentMatrixConstraint(in_ctrl, duplicate)
            decomposes.append(decompose)
            in_controls.append(in_ctrl)

            transform_parent = None if transform.name() == pcfg.root_joint_name else transform.getParent()
            transform.attr(pcfg.length_attribute) >> ctrl.initialLength
            spaces = [transform_parent, ctrl_parent]
            spaces = filter(lambda node: not isinstance(node, (pm.nodetypes.PiperSkinnedMesh, type(None))), spaces)

            if spaces:
                space.create(spaces, in_ctrl)

            if connect:
                xform.parentMatrixConstraint(duplicate, transform)

            # easier to support game engines scale is uniform
            attribute.uniformScale(ctrl, calc_axis)
            attribute.uniformScale(in_ctrl, calc_axis)

            # used for scale calculation in FK control
            ctrl.worldMatrix >> ctrl.scaleDriverMatrix
            duplicate_parent = duplicate.getParent()

            if duplicate_parent:
                duplicate_parent.parentMatrix >> ctrl.scaleParentMatrix
                duplicate_parent.translate >> ctrl.scaleTranslate

                calc_axis = calc_axis.lstrip('n')
                main_term = decomposes[-2].attr('outputScale' + calc_axis.upper())
                inputs = [ctrl_parent.attr('s' + calc_axis), ctrl.outputScale]

                if global_ctrl:
                    inputs.append(global_ctrl.sy)

                # connect all the stuff needed for volumetric scaling
                multiply = pipernode.multiply(duplicate_parent, main_term, ctrl.volumetric, inputs)
                multiplies.append(multiply)

        # edge cases for scaling
        if parent and len(transforms) > 1:
            multiply_input = attribute.getNextAvailableMultiplyInput(multiplies[0])
            parent.attr('s' + calc_axis) >> multiply_input

            if len(transforms) > 2 and controls[1] != controls[-1]:
                multiply_input = attribute.getNextAvailableMultiplyInput(multiplies[1])
                parent.attr('s' + calc_axis) >> multiply_input

        if len(transforms) > 2:
            multiply_input = attribute.getNextAvailableMultiplyInput(multiplies[1])
            controls[0].attr('s' + calc_axis) >> multiply_input

        self.organize(controls + [duplicates[0]], prefix=inspect.currentframe().f_code.co_name, name=name)
        return duplicates, controls, in_controls

    def IK(self, start, end, parent=None, shape=curve.ring, sizes=None, connect=True, global_ctrl='', name=''):
        """
        Creates IK controls and IK RP solver and for the given start and end joints.

        Args:
            start (pm.nodetypes.Joint): Start of the joint chain.

            end (pm.nodetypes.Joint): End of the joint chain.

            parent (pm.nodetypes.Transform): Parent of start control.

            shape (method): Creates the shape control that will drive joints.

            sizes (list): Sizes to use for each control.

            connect (bool): If True, connects the duplicate FK chain to the given start/end transforms to be driven.

            global_ctrl (pm.nodetypes.Transform): If given, will use this to drive global scale of piperIK control.

            name (str or None): Name to give group that will house all IK components.

        Returns:
            (list): Controls created in order from start to end.
        """
        axis = None
        mid_ctrl = None
        start_ctrl = None
        scale_buffer = None
        controls = []
        transforms = xform.getChain(start, end)
        duplicates = xform.duplicateChain(transforms, prefix=pcfg.ik_prefix, color='purple', scale=0.5)
        mid = pcu.getMedian(transforms)
        mid_duplicate = pcu.getMedian(duplicates)

        if mid == start or mid == end:
            pm.error('Not enough joints given! {} is the mid joint?'.format(mid.name()))

        for i, (transform, duplicate) in enumerate(zip(transforms, duplicates)):
            dup_name = duplicate.name(stripNamespace=True)
            size = sizes[i] if sizes else control.calculateSize(transform)
            ctrl_parent = parent if transform == transforms[0] else None

            if transform != transforms[-1]:
                next_transform = transforms[i + 1]
                axis_vector = pipermath.getOrientAxis(transform, next_transform)
                axis = convert.axisToString(axis_vector)

            # start
            if transform == transforms[0]:
                ctrl = control.create(duplicate, name=dup_name, axis=axis, shape=shape, size=size)
                attribute.bindConnect(transform, ctrl, ctrl_parent)
                start_ctrl = ctrl

                # scale buffer transform
                scale_buffer = pm.joint(n=dup_name + pcfg.scale_buffer_suffix)
                scale_buffer.segmentScaleCompensate.set(False)
                pm.matchTransform(scale_buffer, duplicate)
                pm.parent(duplicate, scale_buffer)

            # mid
            elif transform == mid:
                ctrl = control.create(duplicate, curve.orb, dup_name, axis, scale=0.01, matrix_offset=False, size=size)
                translation, rotate, scale, _ = xform.calculatePoleVector(start, mid, end)
                pm.xform(ctrl, t=translation, ro=rotate, s=scale)
                mid_ctrl = ctrl

            # end
            elif transform == transforms[-1]:
                ctrl = control.create(duplicate, pipernode.createIK, dup_name, axis, control_shape=shape, size=size)
                attribute.bindConnect(transform, ctrl)

            else:
                # other unknown joint(s), left for possible future 3+ IK joint chains
                ctrl = control.create(duplicate, name=dup_name, axis=axis, shape=shape, size=size)

            if connect:
                xform.parentMatrixConstraint(duplicate, transform)

            attribute.uniformScale(ctrl, axis)
            controls.append(ctrl)

        piper_ik = controls[-1]
        nodes_to_organize = [controls[0], scale_buffer, piper_ik]
        mid.attr(pcfg.length_attribute) >> piper_ik.startInitialLength
        transforms[-1].attr(pcfg.length_attribute) >> piper_ik.endInitialLength

        if axis.startswith('n'):
            piper_ik.direction.set(-1)
            axis = axis.lstrip('n')

        # connect controls to joints, and make ik handle
        decompose = xform.parentMatrixConstraint(start_ctrl, scale_buffer, t=True, r=False, s=True)
        xform.parentMatrixConstraint(piper_ik, duplicates[-1], t=False)
        ik_handle_name = duplicates[-1].name(stripNamespace=True) + '_handle'
        ik_handle, _ = pm.ikHandle(sj=duplicates[0], ee=duplicates[-1], sol='ikRPsolver', n=ik_handle_name, pw=1, w=1)
        pm.parent(ik_handle, piper_ik)
        pipermath.zeroOut(ik_handle)
        ik_handle.translate >> piper_ik.handleTranslate
        ik_handle.parentMatrix >> piper_ik.handleParentMatrix
        # xform.poleVectorMatrixConstraint(ik_handle, mid_ctrl)
        attribute.addSeparator(mid_ctrl)
        mid_ctrl.addAttr('poleVectorWeight', k=True, dv=1, min=0, max=1)
        constraint = pm.poleVectorConstraint(mid_ctrl, ik_handle)
        mid_ctrl.poleVectorWeight >> constraint.attr(mid_ctrl.name() + 'W0')

        # connect the rest
        start_ctrl.attr('s' + axis) >> piper_ik.startControlScale
        start_ctrl.worldMatrix >> piper_ik.startMatrix
        mid_ctrl.worldMatrix >> piper_ik.poleVectorMatrix
        piper_ik.startOutput >> mid_duplicate.attr('t' + axis)
        piper_ik.endOutput >> duplicates[-1].attr('t' + axis)
        piper_ik.twist >> ik_handle.twist
        piper_ik._.lock()

        # scale ctrl connect
        decompose_scale = decompose.attr('outputScale' + axis.upper())
        pipernode.multiply(scale_buffer, decompose_scale, inputs=[piper_ik.startOutputScale])
        pipernode.multiply(mid_duplicate, mid_ctrl.attr('s' + axis), inputs=[piper_ik.endOutputScale])
        mid_ctrl.attr('s' + axis) >> piper_ik.poleControlScale

        # parent pole vector to end control and create
        pm.parent(mid_ctrl, piper_ik)
        xform.toOffsetMatrix(mid_ctrl)
        space.create([start_ctrl], mid_ctrl)
        mid_ctrl.useScale.set(False)
        attribute.lockAndHideCompound(mid_ctrl, ['r'])

        # preferred angle connection
        mid_bind = convert.toBind(mid, pm.warning)
        if mid_bind:
            mid_bind.preferredAngle >> piper_ik.preferredAngleInput
            piper_ik.preferredAngleOutput >> mid_duplicate.preferredAngle

        # must parent before creating spaces
        if global_ctrl:
            pm.parent(piper_ik, global_ctrl)
            nodes_to_organize = [controls[0], scale_buffer]

        # create spaces for piper ik
        spaces = filter(None, [parent, global_ctrl])
        space.create(spaces, piper_ik)

        # global scale comes from parent's world matrix scale
        if parent:
            parent_decompose = pm.createNode('decomposeMatrix', n=parent.name(stripNamespace=True) + '_DM')
            parent.worldMatrix >> parent_decompose.inputMatrix
            parent_decompose.attr('outputScale' + axis.upper()) >> piper_ik.globalScale

        self.organize(nodes_to_organize, prefix=inspect.currentframe().f_code.co_name, name=name)
        return duplicates, controls, scale_buffer

    def FKIK(self, start, end, parent=None, fk_shape='', ik_shape='', proxy=True, global_ctrl='', name=''):
        """
        Creates a FK and IK controls that drive the chain from start to end.

        Args:
            start (pm.nodetypes.Joint): Start of the chain to be driven by FK controls.

            end (pm.nodetypes.Joint): End of the chain to be driven by FK controls. If none given, will only drive start

            parent (pm.nodetypes.Transform): If given, will drive the start control through parent matrix constraint.

            fk_shape (method): Used to create curve or visual representation for the FK controls.

            ik_shape (method): Used to create curve or visual representation for the IK controls.

            proxy (boolean): If True, adds a proxy FK_IK attribute to all controls.

            global_ctrl (pm.nodetypes.Transform): If given, will use this to drive global scale of piperIK control.

            name (str or None): Name to give group that will house all FKIK components.

        Returns:
            (list): Two lists, FK and IK controls created in order from start to end respectively.
        """
        if not fk_shape:
            fk_shape = curve.circle

        if not ik_shape:
            ik_shape = curve.ring

        # create joint chains that is the same as the given start and end chain for FK and IK then create controls
        transforms = xform.getChain(start, end)
        sizes = [control.calculateSize(transform) for transform in transforms]
        fk_transforms, fk_ctrls, in_ctrls = self.FK(start, end, parent, '', fk_shape, sizes, False, global_ctrl, None)
        ik_transforms, ik_ctrls, buffer = self.IK(start, end, parent, ik_shape, sizes, False, global_ctrl, None)
        controls = fk_ctrls + in_ctrls + ik_ctrls

        # create the switcher control and add the transforms, fk, and iks to its attribute to store it
        switcher_control = switcher.create(end, end.name(stripNamespace=True))
        switcher_attribute = switcher_control.attr(pcfg.fk_ik_attribute)
        switcher.addData(switcher_control.attr(pcfg.switcher_transforms), transforms, names=True)
        switcher.addData(switcher_control.attr(pcfg.switcher_fk), fk_ctrls + in_ctrls, names=True)
        switcher.addData(switcher_control.attr(pcfg.switcher_ik), ik_ctrls, names=True)
        controls.insert(0, switcher_control)

        # one minus the output of the fk ik attribute in order to drive visibility of ik/fk controls
        one_minus = pipernode.oneMinus(source=switcher_attribute)
        [one_minus.output >> fk.lodVisibility for fk in fk_ctrls + in_ctrls]
        [switcher_attribute >> ik.lodVisibility for ik in ik_ctrls]

        # use spaces to drive original chain with fk and ik transforms and hook up switcher attributes
        for og_transform, fk_transform, ik_transform in zip(transforms, fk_transforms, ik_transforms):
            world_space, fk_space, ik_space = space.create([fk_transform, ik_transform], og_transform, direct=True)
            og_transform.attr(fk_space).set(1)
            switcher_attribute >> og_transform.attr(ik_space)

        results = fk_transforms, ik_transforms, controls
        nodes_to_organize = [fk_transforms[0], ik_transforms[0], buffer] + fk_ctrls + [ik_ctrls[0], switcher_control]
        self.organize(nodes_to_organize, prefix=inspect.currentframe().f_code.co_name, name=name)

        if not proxy:
            return results

        # make proxy fk ik attribute on all the controls
        switcher_control.visibility.set(False)
        for ctrl in controls[1:]:  # start on index 1 since switcher is on index 0
            attribute.addSeparator(ctrl)
            ctrl.addAttr(pcfg.proxy_fk_ik, proxy=switcher_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)

        return results

    def banker(self, joint, ik_control, pivot_track=None, side='', use_track_shape=True):
        """
        Creates a reverse foot control that changes pivot based on curve shape and control rotation input.
        Useful for banking.

        Args:
            joint (pm.nodetypes.Joint): Joint that will be driven by the reverse module and IK handle.

            ik_control (pm.nodetypes.Transform): Control that drives the IK Handle.

            pivot_track (pm.nodetypes.Transform): NurbsCurve shape as child that will act as the track for the pivot.

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
        ik_handle = list(set(ik_control.connections(skipConversionNodes=True, type='ikHandle')))
        if len(ik_handle) != 1:
            pm.error('Needed only ONE ik_handle. {} found.'.format(str(len(ik_handle))))

        ik_handle = ik_handle[0]

        # create a pivot track (cross section curve) if no pivot track (curve) is given
        if not pivot_track:

            # if IK joint given, get the name of the regular joint by stripping the ik prefix
            if joint_name.startswith(pcfg.ik_prefix):
                stripped_name = pcu.removePrefixes(joint_name, pcfg.ik_prefix)
                namespace_name = pcfg.skeleton_namespace + ':' + stripped_name
                search_joint = pm.PyNode(stripped_name) if pm.objExists(stripped_name) else pm.PyNode(namespace_name)
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
            ctrl = control.create(joint, shape=curve.plus, name=prefix + 'bank', axis=axes[0], color='burnt orange',
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

        nodes_to_organize = [reverse_group, normalized_pivot, normalized_track, pivot_track]
        self.findGroup(joint, nodes_to_organize)

        return ctrl

    @staticmethod
    def reverse(driver, target, driven_negate=None, transform=None, switcher_ctrl=None, shape=None, axis=None):
        """
        Creates a control that offsets the given target through rotation (usually foot roll reverse rig).

        Args:
            driver (pm.nodetypes.Transform): The transform that drives the whole chain. Usually the IK handle.

            target (pm.nodetypes.Transform): Transform that will have control rotations added to. Usually end joint.

            driven_negate (pm.nodetypes.Transform): Transform that will have control rotations subtracted from.
            Usually any controls further down the chain/hierarchy of the given target.

            transform (pm.nodetypes.Transform): Transform for making the control. Useful for figuring out control size.
            If None given, will try to use given driven_negate, if no driven_negate, will try to use given target.

            switcher_ctrl (pm.nodetypes.Transform): Transform that handles switching between FK and IK chains.

            shape (method): Creates the shape control that will drive reverse rig system.

            axis (string): Direction control will be facing when created.

        Returns:
            (pm.nodetypes.Transform): Control created.
        """
        if not transform:
            transform = driven_negate if driven_negate else target

        if not shape:
            shape = curve.square

        # attempt to deduce axis if transform only has one child and axis is not given
        if not axis and transform.getChildren() and len(transform.getChildren()) == 1:
            axis_vector = pipermath.getOrientAxis(transform, transform.getChildren()[0])
            axis = convert.axisToString(axis_vector)
            axis = convert.axisToTriAxis(axis)[1]

        # create control
        name = transform.name() + '_reverse'
        driver_parent = driver.getParent()
        ctrl = control.create(transform, shape, name, axis, 'burnt orange', 0.5, True, parent=driver_parent)

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
        if not driven_negate or not driven_negate.offsetParentMatrix.connections(scn=True, plugs=True, d=False):
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
