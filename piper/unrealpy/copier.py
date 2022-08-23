#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue
import piper.core.filer as filer


class Copier(object):

    instance = None

    def __init__(self):
        super(Copier, self).__init__()
        self.utilities = ue.EditorUtilityLibrary()
        self.registry = ue.AssetRegistryHelpers.get_asset_registry()

    def getSelectedFolders(self):
        """
        Gets the selected folders game relative path.

        Returns:
            (list): Folders that are selected in the content browser.
        """
        paths = self.utilities.get_selected_folder_paths()
        return [ue.Name(str(path).split('/All', 1)[-1]) for path in paths]

    def getSelectedFolderData(self):
        """
        Gets the asset data for all the assets in the selected folders non-recursively.

        Returns:
            (list): Asset data struct for all the assets in the selected folders.
        """
        paths = self.getSelectedFolders()
        return self.registry.get_assets_by_paths(paths)

    @staticmethod
    def formatAssetName(asset_data):
        """
        Formats the given asset data into a string with the each asset name and newline separators.

        Args:
            asset_data (list): Asset data struct for all the assets to format into string.

        Returns:
            (string): Line containing all asset names separated by newline separator.
        """
        return '\n'.join([str(data.asset_name) for data in asset_data])

    @staticmethod
    def formatPackageName(asset_data):
        """
        Formats the given asset data into a string with the each package name and newline separators.

        Args:
            asset_data (list): Asset data struct for all the assets to format into string.

        Returns:
            (string): Line containing all package names separated by newline separator.
        """
        return '\n'.join([str(data.package_name) for data in asset_data])

    def assetNames(self):
        """
        Copies the asset names to the clipboard.
        """
        asset_data = self.utilities.get_selected_asset_data()
        names = self.formatAssetName(asset_data)
        return filer.copyToClipboard(names)

    def packageNames(self):
        """
        Copies the asset names to the clipboard.
        """
        asset_data = self.utilities.get_selected_asset_data()
        names = self.formatPackageName(asset_data)
        return filer.copyToClipboard(names)

    def directoryPaths(self):
        """
        Copies the selected directories paths to the clipboard.
        """
        paths = self.getSelectedFolders()
        names = '\n'.join([str(path) for path in paths])
        return filer.copyToClipboard(names)

    def directoryAssetNames(self):
        """
        Copies all of the contents (not recursively) names of the selected directories to the clipboard.
        """
        asset_data = self.getSelectedFolderData()
        names = self.formatAssetName(asset_data)
        return filer.copyToClipboard(names)

    def directoryPackageNames(self):
        """
        Copies all the contents (not recursively) game relative paths of the selected directories to the clipboard.
        """
        asset_data = self.getSelectedFolderData()
        names = self.formatPackageName(asset_data)
        return filer.copyToClipboard(names)


def getCopier():
    """
    Used to create or get the Piper Main Menu, there can only be ONE in the scene at a time.

    Returns:
        (piper.uepy.ui.menu._PiperMenu): Piper main menu class.
    """
    Copier.instance = Copier() if Copier.instance is None else Copier.instance
    return Copier.instance


# rewriting the above as functions below to hook into Unreal menus.
copier = getCopier()


def assetNames():
    """
    Copies the asset names to the clipboard.
    """
    return copier.assetNames()


def packageNames():
    """
    Copies the package name to the clipboard.
    """
    return copier.packageNames()


def directoryPaths():
    """
    Copies the selected directories paths to the clipboard.
    """
    return copier.directoryPaths()


def directoryAssetNames():
    """
    Copies all of the contents (not recursively) names of the selected directories to the clipboard.
    """
    return copier.directoryAssetNames()


def directoryPackageNames():
    """
    Copies all the contents (not recursively) game relative paths of the selected directories to the clipboard.
    """
    return copier.directoryPackageNames()
