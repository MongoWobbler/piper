#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm
import piper.core.util as pcu
import piper.mayapy.ui.util as myui
import piper.mayapy.ui.window as mywindow
from piper.ui.menu import PiperMainMenu, PiperSceneMenu


class MayaSceneMenu(PiperSceneMenu):

    def openSceneInOS(self):
        """
        Opens the current scene in a OS window.
        """
        pcu.openWithOS(os.path.dirname(pm.sceneName()))

    def reloadCurrentScene(self):
        """
        Reopens the current scene. Prompts the user to save if there are unsaved changes.
        """
        scene_name = pm.sceneName()
        if not scene_name:
            return

        if not mywindow.save():
            return

        pm.openFile(scene_name, force=True)


def create():
    """
    Creates the menu set for Piper and adds it to maya's main Menu Bar.
    """
    piper_menu = PiperMainMenu()

    scene_menu = MayaSceneMenu()
    piper_menu.addMenu(scene_menu)

    main_menu = myui.getMainMenuBar()
    main_menu.addMenu(piper_menu)
