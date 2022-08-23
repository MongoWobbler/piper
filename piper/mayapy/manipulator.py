#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.mayapy.selection as selection


def getManipulatorPosition(transform):
    """
    Gets position of move manipulator where control is.

    Args:
        transform (string, PyNode, list, tuple, or set): Name of object(s) to get position from.

    Returns:
        (list): [x, y, z], World position of object in three coordinates.
    """
    pm.select(transform)
    pm.setToolTo('Move')
    position = pm.manipMoveContext('Move', q=1, p=1)
    pm.select(clear=True)
    return position


def cycleManipulatorSpace():
    """
    Cycles through the different manipulator spaces. Usually parent, world, and object.
    """
    selection.validate()
    current_context = pm.currentCtx()
    context_title = pm.contextInfo(current_context, t=True)

    if 'Move' in context_title:
        context_mode = pm.manipMoveContext('Move', q=True, mode=True)
        if context_mode == 0:
            pm.manipMoveContext('Move', edit=True, mode=context_mode + 1)
            pm.displayInfo('In Parent space.')
        elif context_mode == 1:
            pm.manipMoveContext('Move', edit=True, mode=context_mode + 1)
            pm.displayInfo('In World space.')
        else:
            pm.manipMoveContext('Move', edit=True, mode=0)
            pm.displayInfo('In Object space.')

    elif 'Rotate' in context_title:
        context_mode = pm.manipRotateContext('Rotate', q=True, mode=True)
        if context_mode == 0:
            pm.manipRotateContext('Rotate', edit=True, mode=context_mode + 1)
            pm.displayInfo('In World space.')
        elif context_mode == 1:
            pm.manipRotateContext('Rotate', edit=True, mode=context_mode + 1)
            pm.displayInfo('In Gimbal space.')
        else:
            pm.manipRotateContext('Rotate', edit=True, mode=0)
            pm.displayInfo('In Object space.')

    elif 'Scale' in context_title:
        context_mode = pm.manipScaleContext('Scale', q=True, mode=True)
        if context_mode == 0:
            pm.manipScaleContext('Scale', edit=True, mode=context_mode + 1)
            pm.displayInfo('In Parent space.')
        elif context_mode == 1:
            pm.manipScaleContext('Scale', edit=True, mode=context_mode + 1)
            pm.displayInfo('In World space.')
        else:
            pm.manipScaleContext('Scale', edit=True, mode=0)
            pm.displayInfo('In Object space.')
