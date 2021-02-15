#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import setup
import maya.cmds as mc


if mc.about(batch=True):
    os.environ['MAYA_SKIP_USERSETUP_PY'] = '1'
    os.environ['PYMEL_SKIP_MEL_INIT'] = '1'
else:
    import pymel.mayautils as pmu
    pmu.executeDeferred('pmu.executeDeferred(setup.mayaPiper)', lp=True)
