#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue


def getSelectedFolders():
    """
    Gets the selected folders game relative path.

    Returns:
        (list): Folders that are selected in the content browser.
    """
    utilities = ue.EditorUtilityLibrary()
    paths = utilities.get_selected_folder_paths()
    return [ue.Name(str(path).split('/All', 1)[-1]) for path in paths]


def getSelectedFolderData(recursive=False):
    """
    Gets the asset data for all the assets in the selected folders non-recursively.

    Returns:
        (list): Asset data struct for all the assets in the selected folders.
    """
    paths = getSelectedFolders()
    registry = ue.AssetRegistryHelpers.get_asset_registry()
    data = registry.get_assets_by_paths(paths, recursive=recursive)
    return data if data else []


def getSelectedAssetData(recursive=True):
    """
    Gets selected asset data from folders AND assets.

    Args:
        recursive (boolean): If True, will search for assets inside folders of selected folders.

    Returns:
        (list): Asset data struct for all selected assets and assets in selected folders.
    """
    utilities = ue.EditorUtilityLibrary()
    asset_data = utilities.get_selected_asset_data()
    folder_data = getSelectedFolderData(recursive=recursive)
    data = asset_data + folder_data

    if not data:
        print('Nothing was selected!')

    return asset_data + folder_data


def getCurrentLevel():
    """
    Gets the package name of the current level.

    Returns:
        (string): Package name of level opened in editor.
    """
    current_level = ue.get_editor_subsystem(ue.LevelEditorSubsystem).get_current_level()
    return ue.SystemLibrary.get_path_name(current_level).split(".")[0]


def selectCurrentLevel():
    """
    Selects the current level in the content browser.
    """
    level = getCurrentLevel()
    paths = ue.Array(str)
    paths.append(level)
    ue.EditorAssetLibrary.sync_browser_to_objects(paths)
