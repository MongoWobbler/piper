#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm
import maya.cmds as cmds
import piper.core.util as pcu
import piper.mayapy.util as myu
import maya.internal.nodes.proximitywrap.node_interface as node_interface


def returnToBindPose(joints=None):
    """
    Returns the associated bindPoses of the given joints to the pose when they were originally bound.

    Args:
        joints (list): Joints to find bind poses of.
        Note, these are NOT necessarily all the joints that will be restored since joints can share bindPose nodes.

    Returns:
        (set): Bind poses restored.
    """
    # Get joints, find all the bind poses all the joints are using, restore the bind poses for each pose found.
    joints = myu.validateSelect(joints, find='joint')
    poses = {pose for joint in joints for pose in pm.dagPose(joint, bp=True, q=True)}
    [pm.dagPose(pose, g=True, restore=True) for pose in poses]
    return poses


def createProximityWrap(source, target):
    """
    Creates a proximity with the given source and target transforms.

    Args:
        source (pm.nodetypes.Transform): Transform with skinned mesh that will drive given target.

        target (pm.nodetypes.Transform): Transform with mesh shape that will be driven by given source.

    Returns:
        (pm.nodetypes.ProximityWrap): Proximity wrap node created.
    """
    # implementing with maya.cmds since PyMel raises the following warning for every attribute set.
    # Warning: pymel.core.general : Could not create desired MFn. Defaulting to MFnDependencyNode.
    deformer = cmds.deformer(target.name(), type='proximityWrap', name=target.name(stripNamespace=True) + '_pWrap')[0]
    cmds.setAttr(deformer + '.maxDrivers', 1)
    cmds.setAttr(deformer + '.falloffScale', 1.4)
    cmds.setAttr(deformer + '.smoothInfluences', 5)
    cmds.setAttr(deformer + '.smoothNormals', 5)

    proximity_interface = node_interface.NodeInterface(deformer)
    proximity_interface.addDriver(source.getShapes()[-1].name())  # last shape should be the deformed shape
    return deformer


def createTensionDisplay(transforms=None, shape_display=pm.warning, skin_display=pm.warning):
    """
    Creates tension nodes and hooks them up to mesh by intercepting the skin cluster.

    Args:
        transforms (list): Transforms with mesh shapes that will get tension nodes hooked up.

        shape_display (method): Error to display if there are not two shapes.

        skin_display (method): Error to display if no skin clusters found.

    Returns:
        (list): Tension nodes created.
    """
    tension_nodes = []
    transforms = myu.validateSelect(transforms, find='mesh', parent=True)

    for transform in transforms:
        original_shape = None
        deformed_shape = None
        skin_cluster = None
        shapes = transform.getShapes()

        if len(shapes) != 2:
            shape_display('Need two shapes! A deformed shape and an original one.')
            continue

        # get skin cluster and figure out which shape is the original and which is the deformed
        for i, shape in enumerate(shapes):
            skin_cluster = shape.listHistory(type='skinCluster')
            if skin_cluster:
                skin_cluster = skin_cluster[0]
                deformed_shape = shape
                original_shape = shapes[0] if i == 1 else shapes[1]
                break

        if not skin_cluster:
            skin_display('No skin cluster found.')
            continue

        # create tension node and hook it up with necessary data
        tension = pm.createNode('tensionNode', name=transform.nodeName() + '_tension')
        skin_cluster.outputGeometry[0] >> tension.deformedShape
        original_shape.worldMesh >> tension.origShape
        deformed_shape.inMesh.disconnect()
        tension.out >> deformed_shape.inMesh
        tension_nodes.append(tension)

    return tension_nodes


class Binder(object):

    def __init__(self):
        """
        Example:
            import piper.mayapy.rig.skin as skin
            binder = skin.Binder()
            binder.unbind()
            # move joints around, delete joints, parent joints, etc.
            binder.rebind()
        """
        self.info = {}
        self.directory = os.path.join(pcu.getPiperDirectory(), 'temp').replace('\\', '/')

    def unbind(self, meshes=None, bind_pose=True):
        """
        Unbinds the skin clusters from the given meshes (will use selection or all meshes in scene if None).
        Stores skin cluster weights in a temp file to be rebound with the rebind method.

        Args:
            meshes (list): Meshes to unbind.

            bind_pose (boolean): If True will move joints back to the bind pose before unbinding.

        Returns:
            (dictionary): All the info gathered  from unbinding joints.
        """
        # reset info
        self.info = {}
        scene_path = pm.sceneName()
        scene_name = os.path.splitext(scene_path.name)[0] + '_' if scene_path else ''
        meshes = myu.validateSelect(meshes, find='mesh', parent=True)
        pcu.validateDirectory(self.directory)

        for mesh in meshes:
            # get the skin of the mesh, if it doesnt exist then we don't need to store skin weights
            mesh_name = mesh.nodeName()
            skin = mesh.listHistory(type='skinCluster')

            if not skin:
                continue

            # get the info we need to rebind the mesh: skin name, max influences, and joints influencing mesh
            # stored as string in case object gets deleted and renamed after unbinding
            skin = skin[0].nodeName()
            max_influences = pm.skinCluster(mesh, q=True, mi=True)
            joints = [joint.nodeName() for joint in pm.skinCluster(skin, q=True, influence=True)]

            if bind_pose:
                returnToBindPose(joints)

            # select mesh, export skin weights, and detach skin using MEL because pm.bindSkin(delete=True) has errors.
            pm.select(mesh)
            deformer_name = scene_name + mesh_name + '.xml'
            path = pm.deformerWeights(deformer_name, export=True, deformer=skin, path=self.directory)
            pm.mel.eval('doDetachSkin "2" { "1","1" }')

            self.info[mesh_name] = {'skin': skin,
                                    'max_influences': max_influences,
                                    'joints': joints,
                                    'path': path}

        pm.select(meshes)
        return self.info

    def rebind(self, mesh_display=pm.warning, joint_display=pm.warning):
        """
        Rebinds meshes with skin clusters based on the date in the stored info class variable.

        Args:
            mesh_display (method): How to display a missing mesh.

            joint_display (method): How to display a missing joint.
        """
        for mesh, info in self.info.items():

            path = info['path']
            if not pm.objExists(mesh):
                mesh_display(mesh + ' does not exist! Will not be rebound')
                os.remove(path)
                continue

            # make sure mesh is unique, and that joints exist
            mesh = pm.PyNode(mesh)
            joints = info['joints']
            joints = [pm.PyNode(joint) if pm.objExists(joint) else joint_display('Missed ' + joint) for joint in joints]

            pm.select(mesh, joints)
            skin_name = info['skin']
            max_influences = info['max_influences']
            pm.skinCluster(tsb=True, fnw=True, mi=max_influences, name=skin_name, omi=True)

            directory = os.path.dirname(path)
            deformer_name = os.path.basename(path)
            pm.deformerWeights(deformer_name, im=True, m='index', df=skin_name, e=True, p=directory)
            os.remove(path)
            print('# Imported deformer weights from ' + path + ' to ' + mesh.nodeName())

        # select meshes to end it all
        pm.select(self.info.keys())

        if not os.listdir(self.directory):
            os.rmdir(self.directory)
