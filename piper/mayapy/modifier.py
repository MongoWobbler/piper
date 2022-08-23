#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm


def isShiftHeld():
    """
    Gets whether shift is held or not. Returns false during batch.

    Returns:
        (bool): True if shift is held.
    """
    return False if pm.about(batch=True) else (pm.getModifiers() & 1) > 0


def isCtrlHeld():
    """
    Gets whether CTRL key is held or not. Returns false during batch.

    Returns:
        (bool): True if ctrl is held.
    """
    return False if pm.about(batch=True) else (pm.getModifiers() & 4) > 0


def isAltHeld():
    """
    Gets whether ALT key is held or not. Returns false during batch.

    Returns:
        (bool): True if alt is held.
    """
    return False if pm.about(batch=True) else (pm.getModifiers() & 8) > 0
