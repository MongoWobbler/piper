#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import copy
import unreal as ue

import piper.config as pcfg
import piper.config.unreal as ucfg

import piper.core.dcc as dcc
from piper.core.store import piper_store

import piper.unrealpy.browser as browser


# caching tag dictionary here for easy look-up.
metadata_tags = {}


def getTags():
    """
    Gets all the valid metadata tags associated with each Unreal class.

    Returns:
        (dictionary): Class as key, then dict with attribute as key and tag as value.
    """
    global metadata_tags

    if metadata_tags:
        return metadata_tags

    # static mesh
    static_mesh_dcc_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.dcc_attribute])
    static_mesh_source_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.relative_attribute])
    static_mesh_node_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.pipernode_attribute])
    static_mesh_method_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.method_attribute])
    static_mesh_project_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.project_attribute])

    # skeleton and animations
    root_dcc_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.root_joint_name, pcfg.dcc_attribute])
    root_source_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.root_joint_name, pcfg.relative_attribute])
    root_node_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.root_joint_name, pcfg.pipernode_attribute])
    root_method_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.root_joint_name, pcfg.method_attribute])
    root_project_tag = ucfg.meta_separator.join([ucfg.fbx_meta_prefix, pcfg.root_joint_name, pcfg.project_attribute])

    # skeletal/skinned mesh
    skin_mesh_dcc_tag = [ucfg.fbx_meta_prefix, pcfg.mesh_with_attribute_name, pcfg.dcc_attribute]
    skin_mesh_dcc_tag = ucfg.meta_separator.join(skin_mesh_dcc_tag)
    skin_mesh_source_tag = [ucfg.fbx_meta_prefix, pcfg.mesh_with_attribute_name, pcfg.relative_attribute]
    skin_mesh_source_tag = ucfg.meta_separator.join(skin_mesh_source_tag)
    skin_mesh_node_tag = [ucfg.fbx_meta_prefix, pcfg.mesh_with_attribute_name, pcfg.pipernode_attribute]
    skin_mesh_node_tag = ucfg.meta_separator.join(skin_mesh_node_tag)
    skin_mesh_method_tag = [ucfg.fbx_meta_prefix, pcfg.mesh_with_attribute_name, pcfg.method_attribute]
    skin_mesh_method_tag = ucfg.meta_separator.join(skin_mesh_method_tag)
    skin_mesh_project_tag = [ucfg.fbx_meta_prefix, pcfg.mesh_with_attribute_name, pcfg.project_attribute]
    skin_mesh_project_tag = ucfg.meta_separator.join(skin_mesh_project_tag)

    metadata_tags = {ucfg.static_mesh: {pcfg.dcc_attribute: static_mesh_dcc_tag,
                                        pcfg.relative_attribute: static_mesh_source_tag,
                                        pcfg.pipernode_attribute: static_mesh_node_tag,
                                        pcfg.method_attribute: static_mesh_method_tag,
                                        pcfg.project_attribute: static_mesh_project_tag},
                     ucfg.skeleton: {pcfg.dcc_attribute: root_dcc_tag,
                                     pcfg.relative_attribute: root_source_tag,
                                     pcfg.pipernode_attribute: root_node_tag,
                                     pcfg.method_attribute: root_method_tag,
                                     pcfg.project_attribute: root_project_tag},
                     ucfg.skeletal_mesh: {pcfg.dcc_attribute: skin_mesh_dcc_tag,
                                          pcfg.relative_attribute: skin_mesh_source_tag,
                                          pcfg.pipernode_attribute: skin_mesh_node_tag,
                                          pcfg.method_attribute: skin_mesh_method_tag,
                                          pcfg.project_attribute: skin_mesh_project_tag},
                     ucfg.anim_sequence: {pcfg.dcc_attribute: root_dcc_tag,
                                          pcfg.relative_attribute: root_source_tag,
                                          pcfg.pipernode_attribute: root_node_tag,
                                          pcfg.method_attribute: root_method_tag,
                                          pcfg.project_attribute: root_project_tag}}

    return metadata_tags


def validatePath(project, relative_path):
    """
    Joints the given art directory with the given relative path and checks to make sure path exists.

    Args:
        project (string): Name of project to search for art directory.

        relative_path (string): Relative path to join with art directory.

    Returns:
        (string): Art directory and relative path joined together.
    """
    projects = piper_store.get(pcfg.projects)

    if not projects:
        raise LookupError('No projects exist! Please create a project.')

    directories = projects.get(project)

    if not directories:
        raise LookupError(f'Project {project} not found in current project list! '
                          f'Please make sure project {project} exists.')

    art_directory = directories[pcfg.art_directory]
    source_path = art_directory + '/' + relative_path

    if not os.path.exists(source_path):
        raise FileNotFoundError(f'Source path: {source_path} does not exist!')

    return source_path


def getAll(asset_data=None, instantiate=False, warn=True):
    """
    Gets all the piper source from the selected assets.

    Args:
        asset_data (list): asset data to get metadata from. If None given, will use selected assets.

        instantiate (boolean): If true, will fill out existing metadata with what is usually useful to have.

        warn (boolean): If True, will warn about metadata tags missing from assets

    Returns:
        (dictionary): All the piper metadata for each asset. Package path as key, dict with metadata as values.
    """
    metadata = {}
    tags = getTags()
    asset_library = ue.EditorAssetLibrary()
    registry_helper = ue.AssetRegistryHelpers()
    system_library = ue.SystemLibrary()

    if not asset_data:
        asset_data = browser.getSelectedAssetData()

    for data in asset_data:
        asset_class = registry_helper.get_class(data)
        class_name = system_library.get_class_display_name(asset_class)
        name = str(data.package_name)
        if class_name not in tags:
            ue.log_warning(f'{name} is not a supported class for piper metadata!') if warn else None
            continue

        asset = registry_helper.get_asset(data)

        dcc_tag = tags[class_name][pcfg.dcc_attribute]
        source_tag = tags[class_name][pcfg.relative_attribute]
        node_tag = tags[class_name][pcfg.pipernode_attribute]
        method_tag = tags[class_name][pcfg.method_attribute]
        project_tag = tags[class_name][pcfg.project_attribute]

        dcc_meta = asset_library.get_metadata_tag(asset, dcc_tag)
        source_meta = asset_library.get_metadata_tag(asset, source_tag)
        node_meta = asset_library.get_metadata_tag(asset, node_tag)
        method_meta = asset_library.get_metadata_tag(asset, method_tag)
        project_meta = asset_library.get_metadata_tag(asset, project_tag)

        attributes = {pcfg.dcc_attribute: dcc_meta,
                      pcfg.relative_attribute: source_meta,
                      pcfg.pipernode_attribute: node_meta,
                      pcfg.method_attribute: method_meta,
                      pcfg.project_attribute: project_meta}

        {ue.log_warning(f"{name} doesn't have any {at} data!") for at, meta in attributes.items() if not meta and warn}

        if instantiate:
            app = dcc.mapping[dcc_meta]()
            attributes[pcfg.dcc_attribute] = app
            source_path = validatePath(attributes[pcfg.project_attribute], source_meta)
            attributes[pcfg.relative_attribute] = source_path

        metadata[name] = attributes

    return metadata


def get():
    """
    Gets the piper metadata from the selected asset.

    Returns:
        (list): Metadata with source DCC, relative source path, piper_node, export method, and project.
    """
    data = getAll(instantiate=True)

    if len(data) != 1:
        raise ValueError(f'You have selected {str(len(data))} assets! Please select only 1.')

    data = list(data.values())[0]
    app = data[pcfg.dcc_attribute]
    source_path = data[pcfg.relative_attribute]
    piper_node = data[pcfg.pipernode_attribute]
    export_method = data[pcfg.method_attribute]
    project = data[pcfg.project_attribute]

    return app, source_path, piper_node, export_method, project


def getByDCC(absolute_path=False):
    """
    Gets the piper metadata organized by DCC as key and list of data as value.

    Args:
        absolute_path (boolean): If True, will return the art directory + relative path as the path data.

    Returns:
        (dictionary): DCC name as key, list of dictionaries as values.
    """
    metadata = {}
    assets = getAll()

    for asset, data in assets.items():
        dcc_name = data[pcfg.dcc_attribute]
        dcc_data = copy.deepcopy(data)
        dcc_data.pop(pcfg.dcc_attribute)
        dcc_data['package_name'] = asset

        if absolute_path:
            source_path = validatePath(data[pcfg.project_attribute], data[pcfg.relative_attribute])
            dcc_data[pcfg.relative_attribute] = source_path

        if dcc_name not in metadata:
            metadata[dcc_name] = []

        metadata[dcc_name].append(dcc_data)

    return metadata
