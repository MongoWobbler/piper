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


class _PiperMainMenu(QtWidgets.QMenu):

    # used to keep track of piper main menu in order to make it a singleton.
    piper_menu_instance = None

    def __init__(self, title='Piper', parent=None):
        super(_PiperMainMenu, self).__init__(title=title, parent=parent)
        self.setTearOffEnabled(True)


def PiperMainMenu():
    """
    Used to create the Piper Main Menu, there can only be ONE in the scene at a time.

    Returns:
        (_PiperMainMenu): Piper main menu class.
    """
    if _PiperMainMenu.piper_menu_instance is None:
        _PiperMainMenu.piper_menu_instance = _PiperMainMenu()
    return _PiperMainMenu.piper_menu_instance


class PiperSceneMenu(PiperMenu):

    def __init__(self, title='Scene', parent=None):
        super(PiperSceneMenu, self).__init__(title, parent=parent)

        # must store QActions in class so that garbage collector doesn't delete them
        self.open_current = None
        self.reload_scene = None
        self.open_documentation = None
        self.reload_all = None

        self.build()

    def build(self):
        self.open_current = self.add('Open Current Scene in OS', self.openSceneInOS)
        self.addSeparator()

        self.reload_scene = self.add('Reload Current Scene', self.reloadCurrentScene)
        self.addSeparator()

        self.open_documentation = self.add('Open Piper Documentation', self.openDocumentation)
        self.reload_all = self.add('Reload All', self.reloadAll)

    def openSceneInOS(self):
        pass

    def reloadCurrentScene(self):
        pass

    @staticmethod
    def reloadAll():
        piper_main_menu = PiperMainMenu()
        pcu.reloadALl(path=pcu.getPiperDirectory())
        piper_main_menu.deleteLater()

        import scripts.setup
        scripts.setup.mayaPiper()

    @staticmethod
    def openDocumentation():
        pcu.openDocumentation()
