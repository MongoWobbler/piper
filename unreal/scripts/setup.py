#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys


# adds the piper directory to the system's path to look for python scripts
piper_directory = os.environ['PIPER_DIR']
if piper_directory not in sys.path:
    sys.path.append(piper_directory)


def piperTools():
    """
    Loads all piper plug-ins, loads piper settings, creates the menu, and welcomes the user.
    """
    import piper.unrealpy.ui.menu as uemenu
    import piper.unrealpy.settings as settings

    uemenu.create()
    settings.welcome()
