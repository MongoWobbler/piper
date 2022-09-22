#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm

import piper.config as pcfg
import piper.config.maya as mcfg

import piper.core
import piper.core.namer as namer
import piper.core.pather as pather
import piper.core.pythoner as python

import piper.mayapy.plugin as plugin
import piper.mayapy.pipe.paths as paths
from piper.mayapy.pipe.store import maya_store


# shader FX needed for materials
plugin.load('shaderFXPlugin')


class PiperShader(object):

    def __init__(self):
        """
        Some functions could be overridden to create a new material, mainly createMaterial, and connectTextures
        """
        self.materials = []
        self.texture_paths = []
        self.shader_engines = []
        self.textures_directory = None

    @staticmethod
    def getHdrImagePath():
        """
        Gets the path to the HDR image set in the piper settings. Tries to make path relative to art directory.

        Returns:
            (string): Path to the user set HDR image. Empty string if not set.
        """
        # get user defined settings
        hdr_image_path = maya_store.get(mcfg.hdr_image_path)
        return paths.getRelativeArt(hdr_image_path) if hdr_image_path else ''

    def getTextures(self, warn=True):
        """
        Gets all the textures belonging to the open scene. Texture directory set in piper config.

        Args:
            warn (boolean): If True, will warn user if no textures are found.

        Returns:
            (list): Paths to all textures in texture directory.
        """
        scene_path = pm.sceneName()

        if not scene_path:
            return pm.error('Scene is not saved. Please save scene to search for textures') if warn else None

        # using abspath lets the texture directory use terminal paths like "../Textures"
        self.textures_directory = os.path.abspath(os.path.join(scene_path, pcfg.textures_directory))
        if not os.path.exists(self.textures_directory):
            return pm.warning(self.textures_directory + ' does not exist!') if warn else None

        self.texture_paths = pather.getAllFilesEndingWithWord(pcfg.texture_file_types, self.textures_directory)
        return self.texture_paths

    def createMaterial(self):
        """
        Creates the material. In this instance, it imports a shaderFX material made by Pontus Canback.
        https://pontus-canback.artstation.com/pages/norrsken-pbr

        Returns:
            (pm.nodetypes.ShaderfxShader): Material
        """
        # get the path to the material to import
        hdr_image_path = self.getHdrImagePath()
        piper_directory = piper.core.getPiperDirectory()
        norrsken_material_path = os.path.join(piper_directory, 'maya', 'scenes', 'NorrskenPBR.mb')
        nodes = pm.importFile(norrsken_material_path, rnn=True)

        # the material is the only ShaderfxShader imported, set the HDR image attribute
        material = pm.ls(nodes, type='ShaderfxShader')[0]
        material.HDRI.set(hdr_image_path)

        # delete all the other nodes that might have been imported
        self.materials.append(material)
        nodes.remove(material)
        pm.delete(nodes)

        return material

    def connectTextures(self, material, warn=True):
        """
        Connects the textures in self.texture_paths to the given material. Will attempt to use relative paths.

        Args:
            material (pm.nodetypes.ShaderfxShader): Norrsken PBR shaderFX material used to connect textures to.

            warn (boolean): If True, will warn user if no textures found.
        """
        if material.type() != 'ShaderfxShader':
            pm.error(material.nodeName() + ' is not a ShaderfxShader!')

        if not self.texture_paths:
            self.getTextures(warn=warn)

        # odd check to make sure we don't over warn user if textures are not found by getting textures
        if not self.texture_paths and self.texture_paths is not None:
            return pm.warning('No textures found in ' + self.textures_directory) if warn else None

        material_name = material.nodeName().lstrip(pcfg.material_prefix)

        for texture_path in self.texture_paths:
            texture_name, _ = os.path.splitext(os.path.basename(texture_path))

            if not (material_name in texture_name):
                continue

            # use relative texture path if possible
            texture_path = paths.getRelativeArt(texture_path)

            # diffuse/base color
            if texture_name.endswith(pcfg.diffuse_suffix):
                material.Use_Base_Color.set(True)
                material.Base_Color.set(texture_path)

                # file nodes have a nice attribute that tests whether a file has alpha or not
                opacity_tester = pm.createNode('file', name='opacityTest')
                opacity_tester.fileTextureName.set(texture_path)

                # set opacity blending mode to blending instead of clipping if file has alpha
                if opacity_tester.fileHasAlpha.get():
                    pm.mel.eval('shaderfx -sfxnode "{}" -edit_bool 1291 "value" false;'.format(material.nodeName()))

                pm.delete(opacity_tester)

            # packed ambient occlusion, roughness, and metallic
            elif texture_name.endswith(pcfg.ao_r_m_suffix):
                material.Use_Occlusion_Roughness_Metallic.set(True)
                material.Occ_Rgh_Mtl.set(texture_path)

            # normal
            elif texture_name.endswith(pcfg.normal_suffix):
                material.Use_Normal.set(True)
                material.Normal.set(texture_path)

            # emissive/glow
            elif texture_name.endswith(pcfg.emissive_suffix):
                material.Use_Emissive.set(True)
                material.Emissive.set(texture_path)

            elif warn:
                pm.warning(texture_path + ' does not have a valid suffix!')

        # display textures in the main model viewport pane
        pm.modelEditor('modelPanel4', e=True, tx=True, dtx=True)

    @staticmethod
    def getOldMaterials():
        """
        Gets all the materials that need updating. Uses piper config's material prefix to look for them.

        Returns:
            (list): Materials that match prefix.
        """
        return [material for material in pm.ls(mat=True) if material.nodeName().startswith(pcfg.material_prefix)]

    def updateMaterials(self, warn=True):
        """
        Updates the old materials with by creating new ones.

        Args:
            warn (boolean): If True, will warn if no old materials are found.

        Returns:
            (list): Materials created.
        """
        new_materials = []
        materials = self.getOldMaterials()

        if not materials:
            return pm.warning('No materials to update found!') if warn else None

        imported_material = self.createMaterial()
        for material in materials:

            # if material is not connected to shader engine, then it's not being used, and it's not worth updating
            shading_engine = material.outColor.connections()
            if not shading_engine:
                continue

            shading_engine = shading_engine[0]
            material_name = material.nodeName()

            # avoids importing several files, instead import one file and duplicate material as needed
            new_material = imported_material if material == materials[-1] else pm.duplicate(imported_material)[0]
            material.outColor.disconnect()
            new_material.outColor >> shading_engine.surfaceShader
            pm.delete(material)
            new_materials.append(new_material)
            new_material.rename(material_name)
            self.connectTextures(new_material, warn=warn)

        return new_materials


def getConnectedMaterialsAndShaders(transform, include_default=True):
    """
    Gets all the connected materials and shader engines for a given transform.

    Args:
        transform (pm.nodetypes.transform): Transform with geometry to get connected materials and shaders from

        include_default (boolean): If True, will include the default materials that cannot be deleted.

    Returns:
        (set): Connected materials and transforms
    """
    # ungodly one-liner for fun.
    materials_and_shaders = [[material, shader] for shader in transform.listFuture(type='shadingEngine')
                             for material in shader.surfaceShader.listConnections()] \
        if include_default else [[material, shader]
                                 for shader in transform.listFuture(type='shadingEngine') if
                                 shader.nodeName() != 'initialShadingGroup' for material in
                                 shader.surfaceShader.listConnections() if material.nodeName() != 'lambert1']

    # not 100% sure that maya returns duplicates or not, so turning list into set to remove duplicates
    materials_and_shaders = python.flatten(materials_and_shaders)
    return set(materials_and_shaders)


def createInitialMaterial(transforms=None, delete_old=True):
    """
    Creates basic lambert materials with smart names and assigns them to the meshes.

    Args:
        transforms (list): If given, will create and assign materials to these transforms.

        delete_old (boolean): If True, will delete any of the previous materials and shading engines connected.

    Returns:
        (list): Materials created and assigned.
    """
    scene_name = None

    if not transforms:
        scene_name = None
        transforms = pm.selected()

    if not transforms:
        scene_name = pm.sceneName().basename()
        transforms = [mesh.getParent() for mesh in pm.ls(type='mesh')]

    if not transforms:
        pm.error('No meshes found!')

    if delete_old:
        old_nodes = set()
        [old_nodes.update(getConnectedMaterialsAndShaders(node, include_default=False)) for node in transforms]
        pm.delete(old_nodes)

    # Use the scene name if scene saved and no objects selected else use the name of the last object selected
    material_name = os.path.splitext(scene_name)[0] if scene_name else transforms[-1].nodeName()
    material_name = namer.removeSuffixes(material_name, pcfg.geometry_to_mat_suffixes).title()
    shader = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=material_name + pcfg.shader_engine_suffix)

    # add material prefix to material name, create material, material to shader engine to view, and assign
    material_name = pcfg.material_prefix + material_name
    material = pm.shadingNode(mcfg.default_initial_material, asShader=True, skipSelect=True, name=material_name)
    material.outColor >> shader.surfaceShader
    pm.sets(shader, edit=True, forceElement=transforms)

    return material


def updateMaterials():
    """
    Convenience method for updating materials.
    """
    shader = PiperShader()
    shader.updateMaterials()
