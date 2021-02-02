#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

# Maths
axes = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]

# Export
mesh_prefix = 'SM_'
skinned_mesh_prefix = 'SKM_'

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
