#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import setup
import maya.cmds
import maya.utils


if maya.cmds.about(batch=True):
    # skip launching pymel and if Maya is in standalone/headless/batch mode
    # inherently, this also skips any UI setup for piper
    os.environ['MAYA_SKIP_USERSETUP_PY'] = '1'
    os.environ['PYMEL_SKIP_MEL_INIT'] = '1'
else:
    maya.utils.executeDeferred(setup.piperTools)
