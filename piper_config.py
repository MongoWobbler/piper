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
use_piper_render = 'use_tone_map'
switcher_update_box = 'switcher_update_box'
switcher_key_box = 'switcher_key_box'
switcher_match_box = 'switcher_match_box'
switcher_translate_box = 'switcher_translate_box'
switcher_rotate_box = 'switcher_rotate_box'
switcher_orient_box = 'switcher_orient_box'
switcher_scale_box = 'switcher_scale_box'

store_defaults = {art_directory: None,
                  game_directory: None,
                  use_piper_units: True,
                  use_piper_render: True,
                  unload_unwanted: True,
                  export_ascii: 0,  # 0 instead of False because FBX options takes int, not bool
                  hdr_image_path: '',
                  switcher_update_box: True,
                  switcher_key_box: True,
                  switcher_match_box: False,
                  switcher_translate_box: True,
                  switcher_rotate_box: True,
                  switcher_orient_box: False,
                  switcher_scale_box: True}

# Maya unwanted plug-ins
maya_unwanted_plugins = ['xgenToolkit',
                         'AbcExport',
                         'AbcImport',
                         'hairPhysicalShader',
                         'mayaCharacterization',
                         'mayaHIK',
                         'gameVertexCount'
                         'OpenEXRLoader',
                         'retargeterNodes',
                         'sceneAssembly',
                         'stereoCamera',
                         'Turtle',
                         'svgFileTranslator',
                         'VectorRender',
                         'Type',
                         'mtoa',
                         'MASH']

# Maya units
hotkey_set_name = 'PiperKeySet'
maya_default_time = 'ntsc'
maya_default_length = 'cm'

# Maya graphics
maya_default_rendering_api = 'DirectX11'
maya_default_tone_map = 'Un-tone-mapped (sRGB)'
maya_default_initial_material = 'lambert'

# Geometry
low_poly_suffix = '_low'
high_poly_suffix = '_high'
high_poly_namespace = 'HIGH'
high_poly_file_suffix = '_High'

# Skeleton
skeleton_namespace = 'SKL'
bind_namespace = 'BIND'
length_attribute = 'bindLength'
distance_suffix = '_distance'
bind_attributes = [length_attribute]
required_preferred_angle = ['calf', 'lowerarm', 'elbow', 'knee']
scale_buffer_suffix = '_scale_buffer'

# Rig
rig_suffix = 'Rig'
rig_namespace = 'RIG'
skinned_mesh_grp = 'Skinned_Mesh_grp'
inner_suffix = '_inner'
banker_suffix = '_bank'
reverse_suffix = '_reverse'
root_joint_name = 'root'
dynamic_pivot_suffix = '_dPivot'
dynamic_pivot_rest = 'pivotRest'
bind_matrix_suffix = '_bindMatrix_MM'
group_suffix = '_grp'
visibility_suffix = 'Visibility'
control_set = 'controls'
inner_controls = 'inner'
rig_colors = {'middle': 'yellow',
              'middle_inner': 'salmon',
              'left': 'red',
              'left_inner': 'magenta',
              'right': 'blue',
              'right_inner': 'light blue'}

# Export
fbx_default_version = 2018
mesh_prefix = 'SM_'
skinned_mesh_prefix = 'SKM_'
animation_prefix = 'A_'
delete_node_attribute = 'delete'
check_anim_health_on_export = True

# messages
message_source = 'msgSource'
message_target = 'msgTarget'
message_reverse_driver = 'msgReverseDriver'
message_reverse_target = 'msgReverseTarget'
message_space_blender = 'msgSpaceBlender'
message_space_target = 'msgSpaceTarget'

# Controls
offset_suffix = '_offset'
control_suffix = '_ctrl'
separator_character = '_'

# Parent Matrix
parent_matrix_mult_suffix = 'ParentMatrix_MM'
parent_matrix_decomp_suffix = '_ParentMatrix_DM'
parent_matrix_rot_comp_suffix = '_ParentMatrix_Rot_CM'
parent_matrix_rot_mult_suffix = '_ParentMatrix_Rot_MM_01'
parent_matrix_rot_inv_suffix = '_ParentMatrix_Rot_Inv'
parent_matrix_rot_decomp_suffix = '_ParentMatrix_Rot_DM'

# Offset Constraint
offset_and_parent_mult_suffix = '_OC_ParentOffset_MM'
offset_parent_mult_suffix = '_OC_Parent_MM'
offset_only_mult_suffix = '_OC_Offset_MM'
offset_parent_decomp_suffix = '_OC_ParentOffset_DM'
offset_parent_comp_suffix = '_OC_ParentOffset_CM'

# Spaces
spaces_name = 'spaces'
space_suffix = 'Space'
space_world_name = 'world' + space_suffix
space_use_translate = 'useTranslate'
space_use_rotate = 'useRotate'
space_use_orient = 'useOrient'
space_use_scale = 'useScale'
space_blend_matrix_suffix = '_Spaces_BM'
use_attributes = (space_use_translate, space_use_rotate, space_use_scale, separator_character)

# FKIK
banker_attribute = 'banker'
fk_prefix = 'fk_'
ik_prefix = 'ik_'
fk_ik_attribute = 'fk_ik'
proxy_fk_ik = 'FK_IK'
switcher_visibility = 'switcherVisibility'
switcher_attribute = 'switcher'
switcher_suffix = '_switcher'
switcher_transforms = 'transforms'
switcher_fk = 'fkControls'
switcher_ik = 'ikControls'
switcher_reverses = 'reverses'
switcher_attributes = [switcher_transforms, switcher_fk, switcher_ik, switcher_reverses, fk_ik_attribute]

# Twist
twist_blend_suffix = '_twist_BM'
twist_weight_attribute = 'twistWeight'
twist_blend_weight_attribute = 'distanceWeight'

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
