#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm


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
