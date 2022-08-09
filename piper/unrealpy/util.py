#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue
import piper.core.util as pcu


def copyPackageNames():
    """
    Copies the package name to the clipboard.
    """
    utilities = ue.EditorUtilityLibrary()
    asset_data = utilities.get_selected_asset_data()
    names = '\n'.join([str(data.package_name) for data in asset_data])
    return pcu.copyToClipboard(names)


def copyAssetNames():
    """
    Copies the asset names to the clipboard.
    """
    utilities = ue.EditorUtilityLibrary()
    asset_data = utilities.get_selected_asset_data()
    names = '\n'.join([str(data.asset_name) for data in asset_data])
    return pcu.copyToClipboard(names)
