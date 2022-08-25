#  Copyright (c) Christian Corsica. All Rights Reserved.

import hou
import setup


# if in batch mode, don't load deferred eval since it is only available in graphical mode
if hou.applicationName() != 'hbatch':
    import hdefereval

    hdefereval.executeDeferred(setup.piperTools)
