#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys


# adds the piper directory to the system's path to look for python scripts
piper_directory = os.environ['PIPER_DIR']
if piper_directory not in sys.path:
    sys.path.append(piper_directory)


def piperTools():
    """
    Used to load piper stuff.
    """
    import piper.core.vendor

    piper.core.vendor.addPaths()  # sets up vendor paths for dcc
