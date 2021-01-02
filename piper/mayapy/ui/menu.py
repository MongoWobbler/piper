#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm
import piper.core.util as pcu
import piper.mayapy.ui.util as myui
import piper.mayapy.pipe.store as store
import piper.mayapy.settings as settings
import piper.mayapy.ui.window as mywindow
from piper.ui.menu import PiperSceneMenu, PiperExportMenu, getPiperMainMenu
from PySide2 import QtWidgets


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


class MayaExportMenu(PiperExportMenu):

    def exportToGame(self):
        pass

    def setArtDirectory(self):
        dialog = QtWidgets.QFileDialog()
        starting_directory = pm.workspace(q=True, dir=True)
        directory = dialog.getExistingDirectory(self, 'Choose directory to export from', starting_directory)

        if not directory:
            return

        settings.setProject(directory)
        store.enter().set('art_directory', directory)

    def setGameDirectory(self):
        dialog = QtWidgets.QFileDialog()
        starting_directory = store.enter().get('game_directory')
        directory = dialog.getExistingDirectory(self, 'Choose directory to export to', starting_directory)

        if not directory:
            return

        store.enter().set('game_directory', directory)


def create():
    """
    Creates the menu set for Piper and adds it to maya's main Menu Bar.
    """
    piper_menu = getPiperMainMenu()
    piper_menu.scene_menu = MayaSceneMenu()
    piper_menu.export_menu = MayaExportMenu()
    piper_menu.build()

    main_menu = myui.getMainMenuBar()
    main_menu.addMenu(piper_menu)
