#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import abc
import sys
import json
import shutil

import pymel.core as pm

import piper.config as pcfg
import piper.config.maya as mcfg
import piper.core.dcc as dcc
import piper.core.filer as filer
import piper.core.pather as pather
import piper.core.pythoner as python
import piper.core.fbx_sdk as fbx_sdk

import piper.mayapy.rig as rig
import piper.mayapy.rig.bone as bone
import piper.mayapy.animation as animation
import piper.mayapy.graphics as graphics
import piper.mayapy.mesh as mesh
import piper.mayapy.plugin as plugin
import piper.mayapy.selection as selection
import piper.mayapy.pipe.fbxpreset as fbxpreset
import piper.mayapy.pipe.paths as paths


# Assign ABC based on version
ABC = abc.ABC if sys.version_info >= (3, 4) else abc.ABCMeta('ABC', (), {})


class Export(ABC):

    def __init__(self):
        self.extension = None
        self.mesh_settings = None
        self.skinned_mesh_settings = None
        self.animation_settings = None
        self.animation_errors = {}
        self.export_method = self._write
        self.source_method = None  # method that instantiates this class and calls export method. Needed for metadata.

    @abc.abstractmethod
    def write(self, export_path, settings):
        """
        Dependent on export method. Meant to be overridden by child class.

        Args:
            export_path (string): Path to export to.

            settings (any): Extra argument to pass on. Helpful for setting presets or options of write function.
        """
        pass

    def _write(self, export_path, settings, *_, **__):
        """
        Called to write file after verifying directory exists, and posts results after export.

        Args:
            export_path (string): Path to export to.

            settings (any): Extra argument to pass to self.write.

        Returns:
            (string): Path where file wrote to.
        """
        self.onStart(export_path)
        self.write(export_path, settings)  # this is where the export actually happens
        self.onFinished(export_path)
        return export_path

    def toSelf(self, name, settings, *_, **__):
        """
        Exports .fbx of selected nodes to the folder that the current scene is in.
        If file is not saved, will export to root of art directory.

        Args:
            name (string): Name of file.

            settings (any): Extra argument to pass to self.write.

        Returns:
            (string): Path where file wrote to.
        """
        export_path = paths.getSelfExport(name + self.extension)
        self._write(export_path, settings)
        return export_path

    def toGame(self, name, settings, *_, **kwargs):
        """
        Exports selected nodes to the game directory + the relative directory the file is found in with the given name.

        Args:
            name (string): Name of file.

            settings (any): Extra argument to pass to self.write.

        Returns:
            (string): Path where file wrote to.
        """
        export_textures = kwargs.get('textures')
        if export_textures:
            self.textures()

        export_path = paths.getGameExport(name + self.extension)
        self._write(export_path, settings)

        return export_path

    @staticmethod
    def textures():
        shader = graphics.PiperShader()
        textures = shader.getTextures()

        if not textures:
            return

        for texture in textures:
            export_path = paths.getGameTextureExport(texture)
            pather.validateDirectory(os.path.dirname(export_path))
            shutil.copyfile(texture, export_path)
            print('Copying ' + texture + ' to ' + export_path)

        print('Finished copying ' + str(len(textures)) + ' textures ' + '=' * 40)

    def writeExportAttributes(self, transform, piper_node):
        """
        Sets the attributes to be written to the root joint of the given skinned mesh to know where file came from.

        Args:
            transform (pm.nodetypes.DagNode or None): Node to write export attributes on. Usually mesh or root joint.

            piper_node (pm.nodetypes.PiperNode): Piper node that holds transform to write attributes to.
        """
        # add attributes if they don't exist on the transform already
        [transform.addAttr(attr, dt='string', s=True) for attr in pcfg.export_attributes if not transform.hasAttr(attr)]

        current_dcc = dcc.get()
        transform.attr(pcfg.dcc_attribute).set(current_dcc)

        relative_path = paths.getRelativeArt()
        transform.attr(pcfg.relative_attribute).set(relative_path)

        node_name = piper_node.name()
        transform.attr(pcfg.pipernode_attribute).set(node_name)

        if self.source_method:
            command = python.methodToStringCommand(self.source_method)
            transform.attr(pcfg.method_attribute).set(command)

    def _mesh(self, piper_node, settings, textures, attribute_all=False):
        """
        Moves the contents to export out of the piper node and into the world, exports, and moves everything back.

        Args:
            piper_node (pm.nodetypes.Transform): Node to export its content.

            settings (any): Settings to include with the export method.

            textures (boolean): If True, will attempt to export textures.

            attribute_all (boolean): If True, writes export attributes to all the meshes under the piper_node.
            Else, will look for a child with a name defined in piper.config to write attributes to.

        Returns:
            (string): Path where file wrote to.
        """
        children = piper_node.getChildren()
        if attribute_all:
            [self.writeExportAttributes(child, piper_node=piper_node) for child in children]
        else:
            attribute_mesh = mesh.getAttributed(piper_node)
            self.writeExportAttributes(attribute_mesh, piper_node=piper_node)

        pm.parent(children, w=True)
        pm.select(children)
        name = piper_node.name(stripNamespace=True)
        export_path = self.export_method(name, settings, textures=textures)
        pm.parent(children, piper_node)
        return export_path

    def mesh(self, piper_meshes=None, textures=True, ignore=None, warn=True):
        """
        Exports all or selected piper mesh groups.

        Args:
            piper_meshes (list): Piper meshes to export.

            textures (boolean): If True, will attempt to export textures.

            ignore (string): If given and piper node is a child of given ignore type, do not return the piper node.

            warn (boolean): If True, warns the user of no nodes found.

        Returns:
            (list): All export paths.
        """
        if not piper_meshes:
            piper_meshes = selection.get('piperMesh', ignore=ignore)

        if not piper_meshes:
            pm.warning('No Piper Meshes found! Please select or make Piper Export Node') if warn else None

        export_paths = []
        for piper_mesh in piper_meshes:
            export_path = self._mesh(piper_mesh, self.mesh_settings, textures, attribute_all=True)
            self.onExportMesh(export_path)
            export_paths.append(export_path)

        return export_paths

    def skinnedMesh(self, skinned_meshes, textures=True, ignore=None, warn=True):
        """
        Exports all or selected piper skinned mesh groups.

        Args:
            skinned_meshes (list): Piper skinned mesh groups to export.

            textures (boolean): If True, will attempt to export textures.

            ignore (string): If given and piper node is a child of given ignore type, do not return the piper node.

            warn (boolean): If True, warns the user of no nodes found.

        Returns:
            (list): All export paths.
        """
        export_paths = []
        if not skinned_meshes:
            skinned_meshes = selection.get('piperSkinnedMesh', ignore=ignore)

        if not skinned_meshes:
            pm.warning('No Piper Skin nodes found! Please select or make Piper Export Node') if warn else None

        # export skinned meshes and delete any joints in the fbx file that have the delete attribute on them
        for skinned_mesh in skinned_meshes:
            root = bone.getRoot(skinned_mesh=skinned_mesh)
            self.writeExportAttributes(transform=root, piper_node=skinned_mesh)
            export_path = self._mesh(skinned_mesh, self.skinned_mesh_settings, textures, attribute_all=False)
            self.onExportSkinnedMesh(export_path)
            export_paths.append(export_path)

        return export_paths

    def animation(self, animations, ignore=None, warn=True):
        """
        Exports all or given piper animation groups.

        Args:
            animations (list): Piper animation nodes to export.

            ignore (string): If given and piper node is a child of given ignore type, do not return the piper node.

            warn (boolean): If True, warns the user of no nodes found.

        Returns:
            (list): All export paths.
        """
        export_paths = []
        pm.refresh(suspend=True)
        self.animation_errors.clear()
        start = pm.playbackOptions(q=True, min=True)
        end = pm.playbackOptions(q=True, max=True)

        if not animations:
            animations = selection.get('piperAnimation', ignore=ignore)

        # check to make sure animation is healthy
        if mcfg.check_anim_health_on_export:
            namespaces = {pig.namespace() for anim in animations for pig in anim.getChildren(ad=True, type='piperRig')}
            self.animation_errors = animation.health(namespaces, resume=False)

        for anim in animations:

            root = bone.getRoot(start=anim, namespace=mcfg.skeleton_namespace, warn=warn)
            if not root:
                continue

            piper_rig = anim.getChildren(ad=True, type='piperRig')
            if not piper_rig:
                pm.warning('{} has no piper rig!'.format(anim.name())) if warn else None
                continue

            # get joints from rig
            self.writeExportAttributes(transform=root, piper_node=anim)
            joints = root.getChildren(ad=True, type='joint')
            joints.append(root)

            # duplicate rig joints
            root_duplicate = pm.duplicate(root)[0]
            pm.parent(root_duplicate, w=True)
            duplicates = root_duplicate.getChildren(ad=True, type='joint')
            duplicates.append(root_duplicate)

            # get root control to turn off squash stretch attribute temporarily for proper export scale values
            piper_rig = piper_rig[0]
            root_control = rig.getRootControl(piper_rig)

            # only exporting sides curve since up can be re-created by taking inverse of side curve value
            pm.deleteAttr(root_duplicate.attr(mcfg.root_scale_up))
            if mcfg.export_root_scale_curves:
                root_control.attr(mcfg.squash_stretch_weight_attribute).set(0)
                root.attr(mcfg.root_scale_sides) >> root_duplicate.attr(mcfg.root_scale_sides)
            else:
                pm.deleteAttr(root_duplicate.attr(mcfg.root_scale_sides))

            # delete unwanted attributes
            for joint, duplicate in zip(joints, duplicates):
                attributes = duplicate.listAttr()
                for attr in attributes:
                    attribute_name = attr.name().split('.')[-1]

                    if attribute_name.startswith(mcfg.use_attributes) or attribute_name.endswith(mcfg.space_suffix):
                        pm.setAttr(attr, lock=False)
                        pm.deleteAttr(attr)

                # connect channels from original to duplicate
                [joint.attr(attr) >> duplicate.attr(attr) for attr in ['t', 'r', 's']]

            # get clip data
            starts = []
            ends = []
            data = anim.clipData.get()  # could be empty string, empty dictionary, or dictionary with data
            data = json.loads(data) if data else {}  # json.loads fails with empty string

            if not data:
                data = {'': {'export': True, 'start': start, 'end': end}}

            for clip_name, clip_data in data.items():
                starts.append(clip_data['start'])
                ends.append(clip_data['end'])

            # bake animation keys onto duplicate joints and export
            pm.select(duplicates)
            pm.bakeResults(sm=True, time=(min(starts), max(ends)))

            # export each clip
            for clip_name, clip_data in data.items():

                # if export is not checked, then continue with other clips
                if not clip_data.get('export'):
                    continue

                pm.playbackOptions(min=clip_data['start'], max=clip_data['end'])
                anim_name = anim.name(stripNamespace=True)
                export_name = anim_name + '_' + clip_name if clip_name else anim_name
                export_path = self.export_method(export_name, self.animation_settings)  # export happens here
                self.onExportAnimation(export_path)
                export_paths.append(export_path)

            pm.delete(root_duplicate)
            root_control.attr(mcfg.squash_stretch_weight_attribute).set(1)

        pm.playbackOptions(min=start, max=end)
        pm.refresh(suspend=False)

        if not export_paths:
            pm.warning('No skinned meshes found under any animation nodes! Export failed. ') if warn else None

        return export_paths

    def piperNodes(self, warn=False):
        """
        Exports all piper nodes from scene.

        Returns:
            (list): All export paths.
        """
        mesh_export = []
        skin_export = []
        anim_export = []
        selected = pm.selected()  # store selection
        piper_meshes = selection.get('piperMesh', ignore='piperSkinnedMesh')
        piper_skinned_meshes = selection.get('piperSkinnedMesh', ignore='piperRig')
        piper_animation = selection.get('piperAnimation')

        if not piper_meshes and not piper_skinned_meshes and not piper_animation:
            pm.warning('No Piper Nodes found! Please select or make a Piper Export node. (Piper>Nodes>Create)')
            return

        if piper_meshes:
            mesh_export = self.mesh(piper_meshes, warn=warn)

        if piper_skinned_meshes:
            skin_export = self.skinnedMesh(piper_skinned_meshes, warn=warn)

        if piper_animation:
            anim_export = self.animation(piper_animation, warn=warn)

        pm.select(selected)  # select originally selected nodes
        exports = mesh_export + skin_export + anim_export

        if len(exports) > 0:
            size = sum([filer.getFileSize(export_path, string=False) for export_path in exports])
            text = 'Finished exporting {} file(s) for a total of {} MB '.format(str(len(exports)), str(round(size, 2)))
            display = pm.displayInfo

            if self.animation_errors:
                display = pm.warning
                text += 'with export warnings! See Script Editor for details.'

            display(text)
        else:
            pm.warning('No files exported. Export must have failed.')

        return exports

    def onExportMesh(self, export_path):
        pass

    def onExportSkinnedMesh(self, export_path):
        pass

    def onExportAnimation(self, export_path):
        pass

    @staticmethod
    def onStart(export_path):
        """
        Called when the export is about happen, before writing the file.

        Args:
            export_path (string): Path to export to.
        """
        # make export directory if it does not exist already
        export_directory = os.path.dirname(export_path)
        pather.validateDirectory(export_directory)

    @staticmethod
    def onFinished(export_path):
        """
        Called when the export is finished, after writing the file.

        Args:
            export_path (string): Path exported to, supposedly.
        """
        if not os.path.exists(export_path):
            pm.error(export_path + ' does not exist! Did you specify the export_method of the class?')

        size = filer.getFileSize(export_path)
        pm.displayInfo(size + ' exported to: ' + export_path)


class FBX(Export):

    def __init__(self):
        super(FBX, self).__init__()
        plugin.load('fbxmaya')
        self.extension = '.fbx'
        self.mesh_settings = fbxpreset.mesh
        self.skinned_mesh_settings = fbxpreset.skinnedMesh
        self.animation_settings = fbxpreset.animation
        self.delete_fbx_attributes = mcfg.delete_fbx_attributes

    def cleanUpFBX(self, export_path):
        """
        Deletes attributes that may be extraneous data in FBX file as specified in the config file.

        Args:
            export_path (string): Path of FBX file

        Returns:
            (boolean): True if attributes were deleted and file was saved. False if no attributes delete.
        """
        if not self.delete_fbx_attributes:
            return False

        fbx_file = fbx_sdk.PiperFBX(export_path)
        nodes = fbx_file.getSceneNodes()
        removed = [fbx_file.removeNodeProperty(node, attr) for node in nodes for attr in mcfg.fbx_attributes_to_delete]
        deleted = fbx_file.deleteNodesWithPropertyValue(mcfg.delete_node_attribute, True)
        result = any(removed + deleted)

        fbx_file.save() if result else fbx_file.close()
        return result

    def write(self, export_path, preset):
        # set the given preset and export
        preset()
        pm.FBXExport('-s', '-f', export_path)
        self.cleanUpFBX(export_path)


class FBXtoSelf(FBX):

    def __init__(self):
        super(FBXtoSelf, self).__init__()
        self.export_method = self.toSelf


class FBXtoGame(FBX):

    def __init__(self):
        super(FBXtoGame, self).__init__()
        self.export_method = self.toGame


class OBJ(Export):

    def __init__(self):
        super(OBJ, self).__init__()
        plugin.load('objExport')
        self.extension = '.obj'
        self.mesh_settings = 'groups=1;ptgroups=1;materials=0;smoothing=1;normals=1'

    def write(self, export_path, options):
        pm.exportSelected(export_path, type='OBJexport', options=options)


class OBJtoSelf(OBJ):

    def __init__(self):
        super(OBJtoSelf, self).__init__()
        self.export_method = self.toSelf


class OBJtoGame(OBJ):

    def __init__(self):
        super(OBJtoGame, self).__init__()
        self.export_method = self.toGame


def piperNodesToSelfAsFBX():
    """
    Convenience method for exporting all piper nodes to the current directory as .fbx
    """
    exporter = FBXtoSelf()
    exporter.source_method = piperNodesToSelfAsFBX
    exporter.piperNodes()


def piperNodesToGameAsFBX():
    """
    Convenience method for exporting all piper nodes to the set game directory as .fbx
    """
    exporter = FBXtoGame()
    exporter.source_method = piperNodesToGameAsFBX
    exporter.piperNodes()


def piperMeshToSelfAsOBJ():
    """
    Convenience method for exporting piper mesh export nodes to the current directory as .obj
    """
    OBJtoSelf().mesh()


def fromJSON(json_file):
    """
    Reads a json file with appropriate data used to export the files in the json file.

    Args:
        json_file (string): Full path to the json file with data to export.
    """
    dcc_names = python.readJson(json_file)
    app = dcc.get()

    for data in dcc_names[app]:
        source_path = data[pcfg.relative_attribute]
        piper_node = data[pcfg.pipernode_attribute]
        export_method = data[pcfg.method_attribute]

        pm.openFile(source_path, force=True)
        pm.select(piper_node)
        exec(export_method)
