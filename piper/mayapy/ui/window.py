#  Copyright (c) Christian Corsica. All Rights Reserved.

import os

import pymel.core as pm
import piper.config.maya as mcfg
from piper.mayapy.pipe.store import maya_store


def save():
    """
    If scene is modified, a dialog box will appear asking to save the scene.
    """
    # if we are in batch mode, go ahead and continue
    if pm.about(batch=True):
        return True

    # if scene has not been modified, return True
    if not pm.ls(modified=True):
        return True

    scene_name = pm.sceneName()
    if not scene_name:
        scene_name = 'untitled scene'

    answer = pm.confirmDialog(title='Warning: Scene Not Saved',
                              message='Save changes to ' + scene_name + '?',
                              button=['Save', 'Don\'t Save', 'Cancel'],
                              defaultButton='Save', cancelButton='Cancel', dismissString='Cancel')

    if answer == 'Save':
        pm.saveFile()
        return True
    elif answer == 'Don\'t Save':
        return True
    elif answer == 'Cancel':
        return False


def beforeSave():
    """
    Opens window to prompt user what to do about writing permissions.

    Returns:
        (string): Option picked, could be None, 'Checkout', 'Make Writeable', or 'Cancel'.
    """
    # if we are in batch mode, don't do check for anything.
    if pm.about(batch=True):
        return

    # if we don't have a scene, then it is writeable, return.
    scene_path = pm.sceneName()
    if not scene_path:
        return

    # first time saves
    if not os.path.exists(scene_path):
        return

    # if is writeable then there is no need to ask for writing permissions.
    is_writeable = os.access(scene_path, os.W_OK)
    if is_writeable:
        return

    buttons = ['Make Writeable', 'Cancel']
    default_button = 'Make Writeable'

    use_p4 = maya_store.get(mcfg.use_perforce)
    if use_p4:
        buttons.insert(0, 'Checkout')
        default_button = 'Checkout'

    answer = pm.confirmDialog(title='Writing permissions', message='Scene is not writeable!', button=buttons,
                              defaultButton=default_button, cancelButton='Cancel', dismissString='Cancel')

    return answer


def beforeOpen():
    """
    Opens window to prompt user what to do about scene not being synced up in P4.

    Returns:
        (string): Option picked, could be 'Get Latest' or 'Continue'
    """
    buttons = ['Get Latest', 'Continue']
    default_button = 'Get Latest'

    answer = pm.confirmDialog(title='Out of Sync', message='Scene is not latest!', button=buttons,
                              defaultButton=default_button, cancelButton='Continue', dismissString='Continue')

    return answer
