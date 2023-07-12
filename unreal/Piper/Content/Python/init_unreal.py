#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys
import pathlib


if 'PIPER_DIR' not in os.environ:
    current_path = sys.executable if getattr(sys, 'frozen', False) else __file__
    current_path = pathlib.Path(current_path).resolve()
    piper_directory = current_path.parents[4].as_posix()
    os.environ['PIPER_DIR'] = piper_directory

import setup
setup.piperTools()
