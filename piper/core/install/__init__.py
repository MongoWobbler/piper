#  Copyright (c) Christian Corsica. All Rights Reserved.

import os

import piper.core
import piper.config as pcfg


def getScriptPath(dcc):
    """
    Gets the path to the installs script of the given dcc by joining piper directory, and other piper directories.

    Args:
        dcc (string): Digital Content Creation Package to get install script path for.

    Returns:
        (string): Full path to python install script.
    """
    piper_directory = piper.core.getPiperDirectory()
    install_script = pcfg.install_scripts[dcc]
    install_script_path = os.path.join(piper_directory, pcfg.install_script_path, install_script)

    if not os.path.exists(install_script_path):
        raise FileNotFoundError(install_script_path + ' does not exist! Is installer.exe in the correct directory?')

    return install_script_path
