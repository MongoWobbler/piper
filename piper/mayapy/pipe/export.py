#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import shutil
import pymel.core as pm
import piper_config as pcfg
import piper.core.util as pcu
import piper.core.fbx_sdk as fbx_sdk
import piper.mayapy.plugin as plugin
import piper.mayapy.graphics as graphics
import piper.mayapy.pipernode as pipernode
import piper.mayapy.pipe.fbxpreset as fbxpreset
import piper.mayapy.pipe.paths as paths


# FBX and OBJ plugin needed to export.
plugin.load('fbxmaya')
plugin.load('objExport')


class Export(object):

    def __init__(self):
        self.extension = None
        self.mesh_settings = None
        self.skinned_mesh_settings = None
        self.animation_settings = None
        self.export_method = self._write

    def write(self, export_path, settings):
        """
        Dependent on export method. Meant to be overridden by child class.

        Args:
            export_path (string): Path to export to.

            settings (any): Extra argument to pass on. Helpful for setting presets or options of write function.
        """
        pass

    def _write(self, export_path, settings, *args, **kwargs):
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

    def toSelf(self, name, settings, *args, **kwargs):
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

    def toGame(self, name, settings, *args, **kwargs):
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

        for texture in textures:
            export_path = paths.getGameTextureExport(texture)
            pcu.validateDirectory(os.path.dirname(export_path))
            shutil.copyfile(texture, export_path)
            print('Copying ' + texture + ' to ' + export_path)

        print('Finished copying textures ' + '=' * 40)

    def _mesh(self, piper_node, settings, textures):
        """
        Moves the contents to export out of the piper node and into the world, exports, and moves everything back.

        Args:
            piper_node (pm.nodetypes.Transform): Node to export its content.

            settings (any): Settings to include with the export method.

            textures (boolean): If True, will attempt to export textures.

        Returns:
            (string): Path where file wrote to.
        """
        children = piper_node.getChildren()
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
        """
        if not piper_meshes:
            piper_meshes = pipernode.get('piperMesh', ignore=ignore)

        if not piper_meshes:
            return pm.warning('No Piper Meshes found! Please select or make Piper Export Node') if warn else None

        [self._mesh(piper_mesh, self.mesh_settings, textures) for piper_mesh in piper_meshes]

    def skinnedMesh(self, skinned_meshes, textures=True, ignore=None, warn=True):
        """
        Exports all or selected piper skinned mesh groups.

        Args:
            skinned_meshes (list): Piper skinned mesh groups to export.

            textures (boolean): If True, will attempt to export textures.

            ignore (string): If given and piper node is a child of given ignore type, do not return the piper node.

            warn (boolean): If True, warns the user of no nodes found.
        """
        if not skinned_meshes:
            skinned_meshes = pipernode.get('piperSkinnedMesh', ignore=ignore)

        if not skinned_meshes:
            return pm.warning('No Piper Skin nodes found! Please select or make Piper Export Node') if warn else None

        # export skinned meshes and delete any joints in the fbx file that have the delete attribute on them
        for skinned_mesh in skinned_meshes:
            export_path = self._mesh(skinned_mesh, self.skinned_mesh_settings, textures)
            fbx_file = fbx_sdk.PiperFBX(export_path)
            deleted = fbx_file.deleteNodesWithPropertyValue(pcfg.delete_node_attribute, True)
            fbx_file.save() if deleted else fbx_file.close()

    def animation(self, animations, ignore=None, warn=True):
        pass

    def piperNodes(self):
        """
        Exports all piper nodes from scene.
        """
        selected = pm.selected()  # store selection
        piper_meshes = pipernode.get('piperMesh', ignore='piperSkinnedMesh')
        piper_skinned_meshes = pipernode.get('piperSkinnedMesh', ignore='piperRig')
        piper_animation = pipernode.get('piperAnimation')

        if not piper_meshes and not piper_skinned_meshes and not piper_animation:
            pm.warning('No Piper Nodes found! Please select or make a Piper Export node. (Piper>Nodes>Create)')
            return

        if piper_meshes:
            self.mesh(piper_meshes, warn=False)

        if piper_skinned_meshes:
            self.skinnedMesh(piper_skinned_meshes, warn=False)

        if piper_animation:
            self.animation(piper_animation, warn=False)

        pm.select(selected)  # selected originally selected nodes

    @staticmethod
    def onStart(export_path):
        """
        Called when the export is about happen, before writing the file.

        Args:
            export_path (string): Path to export to.
        """
        # make export directory if it does not exist already
        export_directory = os.path.dirname(export_path)
        pcu.validateDirectory(export_directory)

    @staticmethod
    def onFinished(export_path):
        """
        Called when the export is finished, after writing the file.

        Args:
            export_path (string): Path exported to, supposedly.
        """
        if not os.path.exists(export_path):
            pm.error(export_path + ' does not exist! Did you specify the export_method of the class?')

        size = pcu.getFileSize(export_path)
        pm.displayInfo(size + ' exported to: ' + export_path)


class FBX(Export):

    def __init__(self):
        super(FBX, self).__init__()
        self.extension = '.fbx'
        self.mesh_settings = fbxpreset.mesh
        self.skinned_mesh_settings = fbxpreset.skinnedMesh

    def write(self, export_path, preset):
        # set the given preset and export
        preset()
        pm.FBXExport('-s', '-f', export_path)


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
    FBXtoSelf().piperNodes()


def piperNodesToGameAsFBX():
    """
    Convenience method for exporting all piper nodes to the set game directory as .fbx
    """
    FBXtoGame().piperNodes()


def piperMeshToSelfAsOBJ():
    """
    Convenience method for exporting piper mesh export nodes to the current directory as .obj
    """
    OBJtoSelf().mesh()
