#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
from piper.mayapy.pipe.store import store


def default(  # geometry
                smoothing_groups=1,
                tangents=1,
                smooth_mesh=1,
                referenced_assets=1,

                # animation
                animation=1,
                animation_only=0,
                skins=1,
                shapes=1,
                constraints=0,

                # other
                cameras=1,
                lights=1,
                embed=1,
                connections=1,
                children=1,

                # scene
                instances=1,
                log=0,
                scene_name=0,
                version=2018,
                ascii=None):
    """
    Default Piper settings for the FBX options.

    Args:
        smoothing_groups (int): If True, FBX will convert edge information to smoothing groups.

        tangents (int): If True, FBX will create tangents and binormal data from UV and normal info on meshes.

        smooth_mesh (int): If True, mesh is not tessellated, and smooth mesh data is exported.

        referenced_assets (int): If True, include referenced assets in FBX.

        animation (int): If True, will include animation data.

        animation_only (int): If True, will include ONLY animation data.

        skins (int): If True, will include skin deformation data.

        shapes (int): If True, will include all geometry blendshapes used in scene.

        constraints (int): If True, will export constraints. Mainly used for MoBo to Maya and back.

        cameras (int): If True, will export camera settings.

        lights (int): If True, export lights, this may include point, spot and directional light types.

        embed (int): If True, export textures associated in scene.

        connections (int): If True, include anything associated with selected object.

        children (int): If True, child objects of selected parent are exported too.

        instances (int): If True, maintain instances, otherwise instances are converted to objects.

        log (int): If True, log what has been exported in a file.

        scene_name (int): If True, will use scene name as the animation take instead of default "Take 001".

        version (int): FBX version to use for exporting data.

        ascii (int): Whether FBX file is in Ascii or Binary. If None given, will use Piper's stored settings
    """
    # initial setup
    ascii = store.get(pcfg.export_ascii) if ascii is None else ascii
    pm.FBXResetExport()

    # geometry
    pm.FBXExportSmoothingGroups('-v', smoothing_groups)
    pm.FBXExportTangents('-v', tangents)
    pm.FBXExportSmoothMesh('-v', smooth_mesh)
    pm.FBXExportReferencedAssetsContent('-v', referenced_assets)

    # animation
    pm.FBXProperty('Export|IncludeGrp|Animation', '-v', animation)
    pm.FBXExportAnimationOnly('-v', animation_only)
    pm.FBXExportSkins('-v', skins)
    pm.FBXExportShapes('-v', shapes)
    pm.FBXExportConstraints('-v', constraints)

    # other
    pm.FBXExportCameras('-v', cameras)
    pm.FBXExportLights('-v', lights)
    pm.FBXExportEmbeddedTextures('-v', embed)
    pm.FBXExportInputConnections('-v', connections)
    pm.FBXExportIncludeChildren('-v', children)

    # scene
    pm.FBXExportInstances('-v', instances)
    pm.FBXExportGenerateLog('-v', log)
    pm.FBXExportUseSceneName('-v', scene_name)
    pm.FBXExportInAscii('-v', ascii)
    pm.FBXExportFileVersion('-v', 'FBX' + str(version) + '00')


def mesh(ascii=None):
    """
    FBX preset settings for a mesh export.

    Args:
        ascii (int): Whether FBX file is in Ascii or Binary. If None given, will use Piper's stored settings
    """
    default(animation=0, skins=0, shapes=0, cameras=0, lights=0, embed=0, ascii=ascii)
