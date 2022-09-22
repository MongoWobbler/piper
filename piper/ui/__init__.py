#  Copyright (c) Christian Corsica. All Rights Reserved.

import piper.config as pcfg
from piper.core.store import piper_store


def openPrevious(reset=True):
    """
    Opens all the widgets store in the previous widget settings.

    Args:
        reset (boolean): If true, will set the previous widgets in settings back to an empty list.
    """
    previous_widgets = piper_store.get(pcfg.previous_widgets)

    # exec doesn't work in list comprehension because of scope issues due to it being a statement in 2.x
    # however, exec is a function in 3.x so list comprehension does work on it in that version.
    for create_command in previous_widgets:
        exec(create_command)

    if reset:
        piper_store.set(pcfg.previous_widgets, [])
