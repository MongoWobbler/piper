#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys
import maya.cmds


# adds the piper directory to the system's path to look for python scripts
piper_directory = os.environ['PIPER_DIR']
if piper_directory not in sys.path:
    sys.path.append(piper_directory)


def piperTools(is_headless=False):
    """
    Loads all piper plug-ins, loads piper settings, creates the menu, and welcomes the user.
    """
    import piper.core.vendor

    version = maya.cmds.about(version=True)
    piper.core.vendor.addPaths(dcc_version=version)  # sets up vendor paths for dcc

    import piper.mayapy.plugin as plugin
    import piper.mayapy.settings as settings

    plugin.loadAll()
    settings.startup()

    if not is_headless:
        import piper.mayapy.ui.menu as mymenu
        mymenu.create()

    settings.welcome()
