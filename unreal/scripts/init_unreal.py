#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys


if 'PIPER_DIR' not in os.environ:
    current_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    piper_directory = os.path.abspath(current_path + '/../../..')
    os.environ['PIPER_DIR'] = piper_directory

import setup
setup.piperTools()
