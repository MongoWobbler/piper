#  Copyright (c) Christian Corsica. All Rights Reserved.

# Documentation
documentation_link = 'https://github.com/MongoWobbler/piper'

# Digital Content Creation (DCC)
maya_name = 'Maya'
houdini_name = 'Houdini'
unreal_name = 'Unreal Engine'
max_3ds_name = '3dsMax'
dcc_agnostic_name = 'agnostic'
valid_dccs = [maya_name, houdini_name, unreal_name]  # DCCs that piper currently supports
install_script_path = 'piper/core/install'
install_scripts = {maya_name:    'maya_install.py',
                   houdini_name: 'houdini_install.py'}
dcc_tooltips = {maya_name:    'Path to Maya Install directory, such as C:/Program Files/Autodesk/Maya2022/',
                houdini_name: 'Path to Houdini Install directory, such as C:/Program Files/Side Effects '
                              'Software/Houdini 18.5.0',
                unreal_name:  'Path to .uproject file, such as C:/MyGame/MyGame.uproject'}

# Maths
axes = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]

# Sides
left_suffix = '_l'
right_suffix = '_r'
left_name = 'Left '
right_name = 'Right '
sides = {left_suffix: left_name,
         right_suffix: right_name}
default_mirror_axis = 'x'

# Vendors
vendors = {dcc_agnostic_name: ['Qt', 'p4'],
           maya_name: ['fbx'],
           houdini_name: [],
           unreal_name: [],
           max_3ds_name: []
           }

# Store
art_directory = 'art_directory'
game_directory = 'game_directory'
use_perforce = 'use_p4'
p4_add_after_save = 'p4_add_after_save'
previous_widgets = 'previous_widgets'  # used when reloading, to re-open any previously opened widgets.
store_defaults = {art_directory: None,
                  game_directory: None,
                  use_perforce: False,
                  p4_add_after_save: False,
                  previous_widgets: []}  # previous widgets are reloaded in piper agnostic file, so storing globally

# Geometry
low_poly_suffix = '_low'
high_poly_suffix = '_high'
high_poly_namespace = 'HIGH'
high_poly_file_suffix = '_High'

# Materials
material_prefix = 'MI_'
piper_material_attribute = 'piperMaterial'
norrsken_name = 'Norrsken'
shader_engine_suffix = '_SG'
geometry_to_mat_suffixes = (low_poly_suffix, high_poly_suffix)

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

# Skeleton
root_joint_name = 'root'

# Export Attributes
dcc_attribute = 'DCC'
relative_attribute = 'relative_source'
pipernode_attribute = 'piper_node'
method_attribute = 'export_method'
export_attributes = [dcc_attribute, relative_attribute, pipernode_attribute, method_attribute]
mesh_with_attribute_name = 'body_low'  # due to UE metadata limitations, a mesh name will be shared across characters
export_file_name = 'export.json'
