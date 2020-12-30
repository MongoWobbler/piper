#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import sys
import traceback
from piper.core.maya_dcc import Maya


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


def installMaya():
    """
    Convenience method for installing environment variables on all versions of Maya.
    """
    maya_install, piper_directory = getInstallPaths('maya_install.py')
    Maya().runInstaller(maya_install, piper_directory)


def finish():
    """
    Convenience method for asking user for input. Also good for pausing console execution and reviewing log.
    """
    print("Press Enter to continue ...")
    input()


if __name__ == '__main__':
    # catches any errors and displays them in the console for user to see.
    try:
        installMaya()
    except BaseException:
        print(sys.exc_info()[0])
        print(traceback.format_exc())
    finally:
        finish()
