#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue
import piper.core.filer as filer
import piper.unrealpy.browser as browser


def formatAssetName(asset_data):
    """
    Formats the given asset data into a string with each asset name and newline separators.

    Args:
        asset_data (list): Asset data struct for all the assets to format into string.

    Returns:
        (string): Line containing all asset names separated by newline separator.
    """
    return '\n'.join([str(data.asset_name) for data in asset_data])


def formatPackageName(asset_data):
    """
    Formats the given asset data into a string with each package name and newline separators.

    Args:
        asset_data (list): Asset data struct for all the assets to format into string.

    Returns:
        (string): Line containing all package names separated by newline separator.
    """
    return '\n'.join([str(data.package_name) for data in asset_data])


def assetNames():
    """
    Copies the asset names to the clipboard.
    """
    asset_data = browser.getSelectedAssetData()
    names = formatAssetName(asset_data)
    return filer.copyToClipboard(names)


def packageNames():
    """
    Copies the full package names to the clipboard.
    """
    asset_data = browser.getSelectedAssetData()
    names = formatPackageName(asset_data)
    return filer.copyToClipboard(names)


def folderPaths():
    """
    Copies the selected folders relative game path to the clipboard.
    """
    folder_paths = browser.getSelectedFolders()
    folder_paths = '\n'.join([str(path) for path in folder_paths])
    return filer.copyToClipboard(folder_paths)


def level():
    """
    Copies the full package name of the open level to the clipboard.
    """
    current_level = ue.get_editor_subsystem(ue.LevelEditorSubsystem).get_current_level()
    name = ue.SystemLibrary.get_path_name(current_level).split(".")[0]
    filer.copyToClipboard(name)
