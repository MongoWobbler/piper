#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
from PySide2 import QtWidgets, QtGui
import piper.core.util as pcu


class PiperMenu(QtWidgets.QMenu):

    def __init__(self, title, parent=None):
        super(PiperMenu, self).__init__(title, parent=parent)
        self.setTearOffEnabled(True)
        self.icon = QtGui.QIcon(os.path.join(pcu.getPiperDirectory(), 'icons', 'piper.png'))

    def add(self, name, on_pressed):
        """
        Convenience method for adding a new item to the menu.

        Args:
            name (string): Name for the item to have on the menu

            on_pressed (method): This will be called when the item is pressed.

        Returns:
            (QtWidgets.QAction): Action item added.
        """
        action = QtWidgets.QAction(name.decode('utf-8'), self)
        action.triggered.connect(on_pressed)
        self.addAction(action)
        return action


class PiperSceneMenu(PiperMenu):

    def __init__(self, title='Scene', parent=None):
        super(PiperSceneMenu, self).__init__(title, parent=parent)

        # must store QActions in class so that garbage collector doesn't delete them
        self.open_current = None
        self.reload_scene = None
        self.open_documentation = None
        self.build()

    def build(self):
        self.open_current = self.add('Open Current Scene in OS', self.openSceneInOS)
        self.addSeparator()

        self.reload_scene = self.add('Reload Current Scene', self.reloadCurrentScene)
        self.addSeparator()

        self.open_documentation = self.add('Open Piper Documentation', self.openDocumentation)

    def openSceneInOS(self):
        pass

    def reloadCurrentScene(self):
        pass

    @staticmethod
    def openDocumentation():
        pcu.openDocumentation()


class PiperExportMenu(PiperMenu):

    def __init__(self, title='Export', parent=None):
        super(PiperExportMenu, self).__init__(title, parent=parent)
        self.export_to_game = None
        self.set_art_directory = None
        self.set_game_directory = None
        self.build()

    def build(self):
        self.export_to_game = self.add('Export To Game', self.exportToGame)
        self.addSeparator()

        self.set_art_directory = self.add('Set Art Directory', self.setArtDirectory)
        self.set_game_directory = self.add('Set Game Directory', self.setGameDirectory)

    def exportToGame(self):
        pass

    def setArtDirectory(self):
        pass

    def setGameDirectory(self):
        pass


class _PiperMainMenu(PiperMenu):

    # used to keep track of piper main menu in order to make it a singleton.
    instance = None

    def __init__(self, title='Piper', parent=None):
        # NOTE: PiperMainMenu needs its submenus defined in the DCC and its build() called by the DCC.
        super(_PiperMainMenu, self).__init__(title=title, parent=parent)
        self.scene_menu = None
        self.export_menu = None
        self.reload_all = None

    def build(self):
        self.addMenu(self.scene_menu)
        self.addMenu(self.export_menu)
        self.addSeparator()

        self.reload_all = self.add('Reload All', self.reloadAll)

    def reloadAll(self):
        pcu.reloadALl(path=pcu.getPiperDirectory())
        self.deleteLater()

        import scripts.setup
        scripts.setup.mayaPiper()


def getPiperMainMenu():
    """
    Used to create or get the Piper Main Menu, there can only be ONE in the scene at a time.

    Returns:
        (_PiperMainMenu): Piper main menu class.
    """
    _PiperMainMenu.instance = _PiperMainMenu() if _PiperMainMenu.instance is None else _PiperMainMenu.instance
    return _PiperMainMenu.instance
