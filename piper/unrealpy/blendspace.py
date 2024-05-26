#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue
import piper.config.unreal as ucfg


asset_filter = ue.ARFilter(class_names=[ucfg.blendspace, ucfg.blendspace1D])


def isSampleRepeated(blendspace):
    """
    Gets whether the given blendspace has a sample that is repeated.

    Args:
        blendspace (unreal.AssetData): Blendspace to check samples of.

    Returns:
        (bool): True if any sample is repeated, false if all samples have unique animation sequences.
    """
    blendspace = ue.AssetRegistryHelpers.get_asset(blendspace)
    samples = blendspace.get_editor_property('sample_data')
    animations = [sample.get_editor_property('animation') for sample in samples]

    # if the set has the same amount of data as the list, then all elements must be unique, else must be repeated
    return len(set(animations)) != len(animations)


def hasOneSample(blendspace):
    """
    Gets whether the given blendspace has more than one sample.

    Args:
        blendspace (unreal.AssetData): Blendspace to check to see if it has multiple samples or not.

    Returns:
        (bool): True if it has more than one sample, false if it has one or no samples.
    """
    blendspace = ue.AssetRegistryHelpers.get_asset(blendspace)
    return len(blendspace.get_editor_property('sample_data')) < 2


def get(directory):
    """
    Gets all the blendspaces in the given directory

    Args:
        directory (str): Directory to start recursive search for blendspaces.

    Returns:
         (list): All blendspace assets found under the given directory.
    """
    registry = ue.AssetRegistryHelpers.get_asset_registry()

    assets = registry.get_assets_by_path(ue.Name(directory), True)
    return registry.run_assets_through_filter(assets, asset_filter)


def getAllWithOneSample(directory):
    """
    Gets all the blendspaces with one or no samples.

    Args:
        directory (str): Directory to start recursive search for blendspaces.

    Returns:
        (list): All blendspace asset data with that only have one or no samples.
    """
    blendspaces = get(directory)
    return filter(hasOneSample, blendspaces)


def getAllWithRepeatedSamples(directory):
    """
    Gets all blendspaces with repeated animations sequences as samples.

    Args:
        directory (str): Directory to start recursive search for blendspaces.

    Returns:
        (list): All blendspace asset data that have repeated animation sequences as samples.
    """
    blendspaces = get(directory)
    return filter(isSampleRepeated, blendspaces)
