#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import sys
import traceback
from piper.core.maya_dcc import Maya
from piper.core.houdini_dcc import Houdini


def getInstallPaths(install_file):
    """
    Gets the paths needed to install environment variables onto a dcc.

    Args:
        install_file (string): Name of file used to write environment variables in dcc.

    Returns:
        (list): Install script as first value, piper directory as second value
    """
    # the installer MUST be placed right inside the piper directory.
    current_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    piper_directory = os.path.dirname(current_path)
    install_script_path = os.path.join(piper_directory, 'piper', 'core', install_file)
    piper_directory = piper_directory.replace('\\', '/')

    if not os.path.exists(install_script_path):
        raise FileNotFoundError(install_script_path + ' does not exist! Is installer.exe in the correct directory?')

    return install_script_path, piper_directory


def installDCC(script_name, dcc_class):
    """
    Convenience method for installing environment variables on all versions of given dcc_class using given script.

    Args:
        script_name (string): Name of python script to look for in piper/core directory.

        dcc_class (DCC): class inheriting from piper.core.dcc.DCC that has installer functionalities.
    """
    dcc_install_script, piper_directory = getInstallPaths(script_name)
    dcc_class().runInstaller(dcc_install_script, piper_directory)


def installMaya():
    """
    Convenience method for installing environment variables on all versions of Maya.
    """
    installDCC('maya_install.py', Maya)


def installHoudini():
    """
    Convenience method for installing environment variables on all versions of Houdini.
    """
    installDCC('houdini_install.py', Houdini)


def finish():
    """
    Convenience method for asking user for input. Also good for pausing console execution and reviewing log.
    """
    print("\nPress Enter to continue ...")
    input()


if __name__ == '__main__':
    # catches any errors and displays them in the console for user to see.
    try:
        installMaya()
        installHoudini()
    except BaseException:
        print(sys.exc_info()[0])
        traceback.print_exc()
    finally:
        finish()
