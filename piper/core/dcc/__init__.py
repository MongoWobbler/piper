#  Copyright (c) Christian Corsica. All Rights Reserved.

import sysconfig

import piper.config as pcfg

from .maya_dcc import Maya
from .houdini_dcc import Houdini


mapping = {pcfg.maya_name: Maya,
           pcfg.houdini_name: Houdini}


def get(error=True):
    """
    Gets the application that is running the current python script.

    Args:
        error (boolean): Raises ValueError if no valid DCC app found.

    Returns:
        (string): Maya, Houdini, UnrealEngine, or 3dsMax.
    """
    path = sysconfig.get_path('scripts')

    if 'Maya' in path:
        return pcfg.maya_name
    elif 'HOUDIN' in path:
        return pcfg.houdini_name
    elif 'Engine\\Binaries\\' in path:
        return pcfg.unreal_name
    elif '3ds' in path and 'Max' in path:
        return pcfg.max_3ds_name
    elif error:
        raise ValueError('No compatible software found in ' + path + '. Please see piper/config for compatible DCCs.')
    else:
        return None


def getInstalled():
    """
    Gets all the installed DCCs versions and paths.

    Returns:
        (Dictionary): Name of DCC as key, then dictionary of path as key and version as value.
    """
    return {dcc_name: installer().getInstallDirectories() for dcc_name, installer in mapping.items()}
