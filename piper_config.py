#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

# Documentation
documentation_link = 'https://github.com/MongoWobbler/piper'

# Maths
axes = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]

# Sides
left_suffix = '_l'
right_suffix = '_r'
default_mirror_axis = 'x'

# Store
art_directory = 'art_directory'
game_directory = 'game_directory'
use_piper_units = 'use_piper_units'
export_ascii = 'export_ascii'
hdr_image_path = 'hdr_image_path'
unload_unwanted = 'unload_unwanted_plugins'
store_defaults = {art_directory: None,
                  game_directory: None,
                  use_piper_units: True,
                  unload_unwanted: True,
                  export_ascii: 0,
                  hdr_image_path: ''}

# Maya unwanted plug-ins
maya_unwanted_plugins = ['xgenToolkit',
                         'AbcExport',
                         'AbcImport',
                         'hairPhysicalShader',
                         'mayaCharacterization',
                         'mayaHIK',
                         'OpenEXRLoader',
                         'retargeterNodes',
                         'sceneAssembly',
                         'stereoCamera',
                         'Turtle',
                         'svgFileTranslator',
                         'VectorRender',
                         'Type',
                         'MASH']

# Maya units
hotkey_set_name = 'PiperKeySet'
maya_default_time = 'ntsc'
maya_default_length = 'cm'

# Maya graphics
maya_default_rendering_api = 'DirectX11'
maya_default_tone_map = 'Stingray tone-map'
maya_default_initial_material = 'lambert'

# Geometry
low_poly_suffix = '_low'
high_poly_suffix = '_high'

# Export
mesh_prefix = 'SM_'
skinned_mesh_prefix = 'SKM_'
animation_prefix = 'A_'
delete_node_attribute = 'delete'

# Rig
rig_suffix = '_Rig'
root_joint_name = 'root'

# Controls
offset_suffix = '_offset'
control_suffix = '_ctrl'

# Parent Matrix
parent_matrix_mult_suffix = '_ParentMatrix_Mult'
parent_matrix_decomp_suffix = '_ParentMatrix_Decomp'
parent_matrix_rot_comp_suffix = '_ParentMatrix_Rot_Comp'
parent_matrix_rot_mult_suffix = '_ParentMatrix_Rot_Mult_01'
parent_matrix_rot_inv_suffix = '_ParentMatrix_Rot_Inv'
parent_matrix_rot_decomp_suffix = '_ParentMatrix_Rot_Decomp'

# Spaces
spaces_name = 'spaces'
space_suffix = 'Space'
space_world_name = 'world' + space_suffix
space_use_translate = 'useTranslate'
space_use_rotate = 'useRotate'
space_use_scale = 'useScale'
space_blend_matrix_suffix = '_Spaces_BlendMatrix'

# FKIK
banker_attribute = 'banker'
fk_prefix = 'fk_'
ik_prefix = 'ik_'
fk_ik_attribute = 'fk_ik'
proxy_fk_ik = 'FK_IK'
switcher_attribute = 'switcher'
switcher_suffix = '_switcher'
switcher_fk = 'fkControls'
switcher_ik = 'ikControls'
switcher_transforms = 'transforms'
switcher_attributes = [fk_ik_attribute, switcher_fk, switcher_ik, switcher_transforms]

# Textures
art_textures_directory_name = '/Textures'
game_textures_directory_name = '/Materials'
textures_directory = '../..' + art_textures_directory_name
texture_file_types = ('.png', '.tga')
diffuse_suffix = '_D'
normal_suffix = '_N'
ambient_occlusion_suffix = '_AO'
roughness_suffix = '_R'
metal_suffix = '_M'
emissive_suffix = '_E'
ao_r_m_suffix = ambient_occlusion_suffix + roughness_suffix + metal_suffix

# Materials
material_prefix = 'MI_'
piper_material_attribute = 'piperMaterial'
norrsken_name = 'Norrsken'
shader_engine_suffix = '_SG'
geometry_to_mat_suffixes = (low_poly_suffix, high_poly_suffix)
