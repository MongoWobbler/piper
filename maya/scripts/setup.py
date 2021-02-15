#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.


import os
import sys

# adds the piper directory to the system's path to look for python scripts
piper_directory = os.environ['PIPER_DIR']
if piper_directory not in sys.path:
    sys.path.append(piper_directory)


def mayaPiper():
    """
    Loads all piper plug-ins, loads piper settings, creates the menu, and welcomes the user
    """
    import piper.core.util as pcu
    import piper.mayapy.plugin as plugin
    import piper.mayapy.ui.menu as mymenu
    import piper.mayapy.settings as settings

    plugin.loadAll()
    settings.startup()
    mymenu.create()
    pcu.welcome()
