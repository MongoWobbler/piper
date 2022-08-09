#  Copyright (c) Christian Corsica. All Rights Reserved.

# Unwanted plug-ins
unwanted_plugins = ['xgenToolkit',
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

# Units
hotkey_set_name = 'PiperKeySet'
default_time = 'ntsc'
default_length = 'cm'
workspace_control_suffix = 'WorkspaceControl'

# Graphics
default_rendering_api = 'DirectX11'
default_tone_map = 'Un-tone-mapped (sRGB)'
default_initial_material = 'lambert'

# Skeleton
skeleton_namespace = 'SKL'
bind_namespace = 'BIND'
length_attribute = 'bindLength'
distance_suffix = '_distance'
bind_attributes = [length_attribute]
required_preferred_angle = ['calf', 'lowerarm', 'elbow', 'knee']
scale_buffer_suffix = '_scale_buffer'

# Matrices
mult_matrix_suffix = '_MM'
compose_matrix_suffix = '_CM'
decompose_matrix_suffix = '_DM'
blend_matrix_suffix = '_BM'
orient_matrix_suffix = '_OM'
aim_matrix_suffix = '_AM'

# Rig
rig_suffix = 'Rig'
rig_namespace = 'RIG'
skinned_mesh_grp = 'Skinned_Mesh_grp'
inner_suffix = '_inner'
banker_suffix = '_bank'
reverse_suffix = '_reverse'
root_joint_name = 'root'
body_base_joint_name = 'pelvis'
dynamic_pivot_suffix = '_dPivot'
dynamic_pivot_rest = 'pivotRest'
bind_matrix_suffix = '_bindMatrix' + mult_matrix_suffix
group_suffix = '_grp'
visibility_suffix = 'Visibility'
control_set = 'controls'
inner_controls_set = 'inner'
movable_controls_set = 'anchors'
ik_controls_set = 'iks'
maya_rig_suffixes = (rig_suffix + '.mb', rig_suffix + '.ma')

# Rig Colors
middle_color = 'yellow'
middle_inner_color = 'salmon'
middle_bendy_color = 'salmon'
middle_inner_bendy_color = 'pink'
left_color = 'red'
left_inner_color = 'magenta'
left_bendy_color = 'magenta'
left_inner_bendy_color = 'light brown'
right_color = 'blue'
right_inner_color = 'light blue'
right_bendy_color = 'light blue'
right_inner_bendy_color = 'baby blue'

# Export
fbx_default_version = 2018
mesh_prefix = 'SM_'
skinned_mesh_prefix = 'SKM_'
animation_prefix = 'A_'
delete_node_attribute = 'delete'
check_anim_health_on_export = True
export_root_scale_curves = True

# Root Squash/Stretch attributes
squash_stretch_attribute = 'squashStretch'
squash_stretch_weight_attribute = 'squashStretchWeight'
root_scale_up = 'scaleUp'
root_scale_sides = 'scaleSides'

# Messages
message_source = 'msgSource'
message_target = 'msgTarget'
message_reverse_driver = 'msgReverseDriver'
message_reverse_target = 'msgReverseTarget'
message_space_blender = 'msgSpaceBlender'
message_space_target = 'msgSpaceTarget'
message_root_control = 'msgRootControl'

# Controls
offset_suffix = '_offset'
control_suffix = '_ctrl'
separator_character = '_'
temp_namespace = 'TEMP'

# Parent Matrix
parent_matrix_mult_suffix = 'ParentMatrix' + mult_matrix_suffix
parent_matrix_decomp_suffix = '_ParentMatrix' + decompose_matrix_suffix
parent_matrix_rot_comp_suffix = '_ParentMatrix_Rot' + compose_matrix_suffix
parent_matrix_rot_mult_suffix = '_ParentMatrix_Rot' + mult_matrix_suffix + '_01'
parent_matrix_rot_inv_suffix = '_ParentMatrix_Rot_Inv'
parent_matrix_rot_decomp_suffix = '_ParentMatrix_Rot' + decompose_matrix_suffix

# Offset Constraint
offset_and_parent_mult_suffix = '_OC_ParentOffset' + mult_matrix_suffix
offset_parent_mult_suffix = '_OC_Parent' + mult_matrix_suffix
offset_only_mult_suffix = '_OC_Offset' + mult_matrix_suffix
offset_parent_decomp_suffix = '_OC_ParentOffset' + decompose_matrix_suffix
offset_parent_comp_suffix = '_OC_ParentOffset' + compose_matrix_suffix

# Spaces
spaces_name = 'spaces'
space_suffix = 'Space'
space_world_name = 'world' + space_suffix
space_use_translate = 'useTranslate'
space_use_rotate = 'useRotate'
space_use_orient = 'useOrient'
space_use_scale = 'useScale'
space_blend_matrix_suffix = '_Spaces' + blend_matrix_suffix
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
twist_blend_suffix = '_twist' + blend_matrix_suffix
twist_weight_attribute = 'twistWeight'
twist_blend_weight_attribute = 'distanceWeight'

# Bendy
bendy_suffix = '_bendy'
bendy_control_set = 'bendy'
bendy_aim_attribute = 'aimWeight'
bendy_locator_suffix = '_driven'
