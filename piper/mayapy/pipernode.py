#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.util as myu
import piper.mayapy.convert as convert
import piper.mayapy.attribute as attribute
from .rig import curve  # must do relative import in python 2


def get(node_type, ignore=None, search=True):
    """
    Gets the selected given node type or all the given node types in the scene if none selected.

    Args:
        node_type (string): Type of node to get.

        ignore (string): If given and piper node is a child of given ignore type, do not return the piper node.

        search (boolean): If True, and nothing is selected, will attempt to search the scene for all of the given type.

    Returns:
        (list) All nodes of the given node type.
    """
    piper_nodes = []
    selected = pm.selected()

    if selected:
        # get only the piper nodes from selection
        piper_nodes = pm.ls(selected, type=node_type)

        # traverse hierarchy for piper nodes
        if not piper_nodes:
            piper_nodes = set()
            for node in selected:
                first_type_parent = myu.getFirstTypeParent(node, node_type)
                piper_nodes.add(first_type_parent) if first_type_parent else None

    # search the whole scene for the piper node
    elif search:
        piper_nodes = pm.ls(type=node_type)

    # don't include any nodes that are a child of the given ignore type
    if ignore:
        piper_nodes = [node for node in piper_nodes if not myu.getFirstTypeParent(node, ignore)]

    return piper_nodes


def multiply(transform, main_term=None, weight=None, inputs=None):
    """
    Creates the multiply node and hooks up all the given given inputs to the given transform's scale.

    Args:
        transform (pm.nodetypes.Transform): Node to hook multiply onto its scale.

        main_term (pm.general.Attribute): Attribute to connect onto the multiply main_term.

        weight (pm.general.Attribute): Attribute to connect onto the multiply weight.

        inputs (list): Attributes to connect to the input plug of the multiply node.

    Returns:
        (pm.nodetypes.piperMultiply): Multiply node created.
    """
    multiply_node = pm.createNode('piperMultiply', n=transform.name(stripNamespace=True) + '_scaleMultiply')
    multiply_node.output >> transform.scale

    if main_term:
        main_term >> multiply_node.mainTerm

    if weight:
        weight >> multiply_node.weight

    if not inputs:
        return multiply_node

    [attr >> multiply_node.input[i] for i, attr in enumerate(inputs)]
    return multiply_node


def inputOutput(node_type, source=None, output=None):
    """
    Creates a node that has an input and output attribute based on given node type.

    Args:
        node_type (string): Type of node to create.

        source (pm.general.Attribute): Attribute to plug into node's input.

        output (pm.general.Attribute): Attribute to plug node's output into.

    Returns:
        (pm.nodetypes.DependNode): Node created.
    """
    name = source.node().name(stripNamespace=True) + '_' if source else ''
    suffix = node_type.split('piper')[-1]
    node = pm.createNode(node_type, name=name + suffix)

    if source:
        source >> node.input

    if output:
        node.output >> output

    return node


def oneMinus(source=None, output=None):
    """
    Creates a one minus node that turns a 0 to 1 range into a 1 to 0 or vice versa.

    Args:
        source (pm.general.Attribute): Attribute to plug into one minus input.

        output (pm.general.Attribute): Attribute to plug one minus' output into.

    Returns:
        (pm.nodetypes.piperOneMinus): One minus node created.
    """
    return inputOutput('piperOneMinus', source=source, output=output)


def reciprocal(source=None, output=None):
    """
    Creates a node that takes in the given source attribute and output its reciprocal. Reciprocal == 1/X

    Args:
        source (pm.general.Attribute): Attribute to plug into reciprocal's input.

        output (pm.general.Attribute): Attribute to plug reciprocal's output into.

    Returns:
        (pm.nodetypes.piperReciprocal): Reciprocal node created.
    """
    return inputOutput('piperReciprocal', source=source, output=output)


def create(node_type, color=None, name=None, parent=None):
    """
    Creates the given node type with the given color and given name/parent.

    Args:
        node_type (string): Node type to create.

        color (string): Name of color to turn outliner text to. Currently supporting:
        cyan, pink.

        name (string): Name of node.

        parent (PyNode or string): Parent of new node.

    Returns:
        (PyNode): Node created.
    """
    name = name if name else node_type
    piper_node = pm.createNode(node_type, name=name, parent=parent, skipSelect=True)
    rgb = convert.colorToRGB(color)

    if rgb:
        piper_node.useOutlinerColor.set(True)
        piper_node.outlinerColor.set(rgb)

    return piper_node


def createShaped(node_type, name=None, control_shape=curve.circle):
    """
    Creates piper IK transform with given control shape curve

    Args:
        node_type (string): Name for the type of node to create.

        name (string): Name to give the transform node.

        control_shape (method): Method that generates nurbs curve the transform will use.

    Returns:
        (PyNode): Transform node created with control shape curves as child(ren).
    """
    transform = create(node_type, name=name)
    transform._.lock()
    ctrl = control_shape()
    curves = ctrl.getChildren(type='nurbsCurve')
    pm.parent(curves, transform, shape=True, add=True)
    pm.delete(ctrl)

    return transform


def createFK(name=None, control_shape=curve.circle):
    """
    Creates piper FK transform with given control shape curve

    Args:
        name (string): Name for the piper IK nodes.

        control_shape (method): Method that generates nurbs curve that Piper FK transform will use.

    Returns:
        (pm.nodetypes.piperFK): Piper FK node created.
    """
    return createShaped('piperFK', name, control_shape)


def createIK(name=None, control_shape=curve.circle):
    """
    Creates piper IK transform with given control shape curve

    Args:
        name (string): Name for the piper IK nodes.

        control_shape (method): Method that generates nurbs curve that Piper IK transform will use.

    Returns:
        (pm.nodetypes.piperIK): Piper IK node created.
    """
    return createShaped('piperIK', name, control_shape)


def createOrientMatrix(position, orientation, name=None):
    """
    Creates a piper orient matrix node that keeps given position matrix, but maintains given orientation matrix.

    Args:
        position (pm.general.Attribute or pm.dt.Matrix): position to plug into orient matrix position attribute.

        orientation (pm.general.Attribute or pm.dt.Matrix): orientation to plug into orient matrix orient attribute.

        name (string): Name to give piper orient matrix node.

    Returns:
        (pm.nodetypes.piperOrientMatrix): Piper Orient Matrix node created.
    """
    if not name:
        name = 'orientMatrix'

    node = pm.createNode('piperOrientMatrix', name=name)

    if isinstance(position, pm.general.Attribute):
        position >> node.positionMatrix
    elif isinstance(position, pm.dt.Matrix):
        node.positionMatrix.set(position)

    if isinstance(orientation, pm.general.Attribute):
        orientation >> node.orientMatrix
    elif isinstance(orientation, pm.dt.Matrix):
        node.orientMatrix.set(orientation)

    return node


def createSwingTwist(driver, target, axis='y', swing=0, twist=1):
    """
    Creates the swing twist node with given axis, swing, and twist attributes.

    Args:
        driver (pm.nodetypes.Transform): Node that will drive given target. Must have BIND used as rest matrix.

        target (pm.nodetypes.Transform): Node that will be driven with twist/swing through offsetParentMatrix.

        axis (string): Axis in which node will output twist.

        swing (float): Weight of swing rotation.

        twist (float): Weight of twist rotation.

    Returns:
        (pm.nodetypes.swingTwist): Swing Twist node created.
    """
    name = target.name(stripNamespace=True) + '_ST'
    swing_twist = pm.createNode('swingTwist', n=name)
    axis_index = convert.axisToIndex(axis)
    swing_twist.twistAxis.set(axis_index)
    swing_twist.swing.set(swing)
    swing_twist.twist.set(twist)
    driver_bind = convert.toBind(driver, fail_display=pm.error)

    driver.matrix >> swing_twist.driverMatrix
    driver_bind.matrix >> swing_twist.driverRestMatrix

    offset_driver = swing_twist.outMatrix
    node_plug = attribute.getSourcePlug(target.offsetParentMatrix)

    if node_plug:
        mult_matrix = pm.createNode('multMatrix', n=name + '_MM')
        swing_twist.outMatrix >> mult_matrix.matrixIn[0]
        node_plug >> mult_matrix.matrixIn[1]
        offset_driver = mult_matrix.matrixSum

    offset_driver >> target.offsetParentMatrix
    return swing_twist


def createMesh():
    """
    Creates a piper mesh group(s) based on whether user has selection, shift held, and scene saved.

    Returns:
        (pm.nt.piperMesh or list): Usually PyNode created. If Shift held, will return list or all piperMesh(es) created.
    """
    selected = pm.selected()
    scene_name = pm.sceneName().namebase

    if selected:
        # if shift held, create a a piper mesh for each selected object.
        if myu.isShiftHeld():
            piper_meshes = []
            for node in selected:
                parent = node.getParent()
                name = pcfg.mesh_prefix + node.nodeName()
                piper_mesh = create('piperMesh', 'cyan', name=name, parent=parent)
                pm.parent(node, piper_mesh)
                piper_meshes.append(piper_mesh)

            return piper_meshes
        else:
            # If user selected stuff that is not a mesh, warn the user.
            non_mesh_transforms = [node for node in selected if not node.getShapes()]
            if non_mesh_transforms:
                pm.warning('The following are not meshes! \n' + '\n'.join(non_mesh_transforms))

            # Get the parent roots and parent them under the piper mesh node to not mess up any hierarchies.
            name = pcfg.mesh_prefix
            name += scene_name if scene_name else selected[-1].nodeName()
            piper_mesh = create('piperMesh', 'cyan', name=name)
            parents = myu.getRootParents(selected)
            pm.parent(parents, piper_mesh)

            return piper_mesh

    name = '' if scene_name.startswith(pcfg.mesh_prefix) else pcfg.mesh_prefix
    name += scene_name if scene_name else 'piperMesh'
    piper_mesh = create('piperMesh', 'cyan', name=name)
    meshes = pm.ls(type='mesh')
    parents = myu.getRootParents(meshes)
    pm.parent(parents, piper_mesh)

    return piper_mesh


def createSkinnedMesh():
    """
    Creates a skinned mesh node for each root joint found in the skin clusters

    Returns:
        (list): PyNodes of nodes created.
    """
    selected = pm.selected()
    scene_name = pm.sceneName().namebase

    if selected:
        skin_clusters = set()
        skin_clusters.update(set(pm.listConnections(selected, type='skinCluster')))
        skin_clusters.update(set(pm.listHistory(selected, type='skinCluster')))
    else:
        skin_clusters = pm.ls(type='skinCluster')

    if not skin_clusters:
        pm.warning('No skin clusters found!')
        piper_skinned_mesh = create('piperSkinnedMesh', 'pink', name=pcfg.skinned_mesh_prefix + 'piperSkinnedMesh')
        return [piper_skinned_mesh]

    piper_skinned_meshes = []
    skinned_meshes = myu.getSkinnedMeshes(skin_clusters)
    for root_joint, geometry in skinned_meshes.items():
        name = '' if scene_name.startswith(pcfg.skinned_mesh_prefix) else pcfg.skinned_mesh_prefix
        name += scene_name if scene_name else next(iter(geometry)).nodeName()
        piper_skinned_mesh = create('piperSkinnedMesh', 'pink', name=name)
        piper_skinned_meshes.append(piper_skinned_mesh)
        geometry_parents = myu.getRootParents(geometry)
        pm.parent(root_joint, geometry_parents, piper_skinned_mesh)

    return piper_skinned_meshes


def createRig(name=''):
    """
    Creates the node that houses all rig nodes.

    Args:
        name (string): If given, will use the given name as the name for the rig node.

    Returns:
        (pm.nodetypes.piperRig): Rig node created.
    """
    name = name if name else 'piperRig'
    piper_rig = create('piperRig', 'burnt orange', name=name)
    piper_rig.addAttr(pcfg.message_root_control, at='message')
    piper_rig._.lock()
    attribute.nonKeyable(piper_rig.highPolyVisibility)
    attribute.lockAndHideCompound(piper_rig)
    attribute.addSeparator(piper_rig)
    return piper_rig


def createAnimation():
    """
    Creates the node that houses a rig. Used to export animation.

    Returns:
        (pm.nodetypes.piperAnimation): Animation node created.
    """
    scene_name = pm.sceneName().namebase
    name = scene_name if scene_name else 'piperAnimation'
    piper_animation = create('piperAnimation', 'dark green', name=pcfg.animation_prefix + name)
    attribute.lockAndHideCompound(piper_animation)
    rigs = get('piperRig', ignore='piperAnimation')
    pm.parent(rigs[0], piper_animation) if len(rigs) == 1 else pm.warning('{} rigs found!'.format(str(len(rigs))))
    return piper_animation
