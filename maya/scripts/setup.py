#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import sys


# adds the piper directory and vendor directory to the system's path to look for python scripts
piper_directory = os.environ['PIPER_DIR']
vendor_directory = os.path.join(piper_directory, 'vendor', 'py')
vendor_directory += '2' if sys.version.startswith('2') else '3'
[sys.path.append(directory) for directory in [piper_directory, vendor_directory] if directory not in sys.path]


def piperTools():
    """
    Loads all piper plug-ins, loads piper settings, creates the menu, and welcomes the user
    """
    import piper.mayapy.plugin as plugin
    import piper.mayapy.ui.menu as mymenu
    import piper.mayapy.settings as settings

    plugin.loadAll()
    settings.startup()
    mymenu.create()
    settings.welcome()
