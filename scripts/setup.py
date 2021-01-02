#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.


import os
import sys


piper_directory = os.environ['PIPER_DIR']
if piper_directory not in sys.path:
    sys.path.append(piper_directory)


def mayaPiper():
    """
    Adds the piper directory to the system's path to look for python scripts
    As well as creating menus, and welcoming user when everything is done.
    """
    import piper.core.util as pcu
    import piper.mayapy.plugin as plugin
    import piper.mayapy.ui.menu as mymenu
    import piper.mayapy.settings as settings

    plugin.loadAll()
    settings.startup()
    mymenu.create()
    pcu.welcome()
