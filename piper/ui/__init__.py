#  Copyright (c) Christian Corsica. All Rights Reserved.

import piper_config as pcfg
import piper.core.store as store


def openPrevious(reset=True):
    """
    Opens all the widgets store in the previous widget settings.

    Args:
        reset (boolean): If true, will set the previous widgets in settings back to an empty list.
    """
    settings = store.get()
    previous_widgets = settings.get(pcfg.previous_widgets)
    [exec(create_command) for create_command in previous_widgets]

    if reset:
        settings.set(pcfg.previous_widgets, [])
