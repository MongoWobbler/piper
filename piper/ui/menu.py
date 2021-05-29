#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import sys
from PySide2 import QtWidgets, QtGui
from piper.ui.widget import manager
import piper.core.util as pcu


class PiperMenu(QtWidgets.QMenu):

    def __init__(self, *args, **kwargs):
        super(PiperMenu, self).__init__(*args, **kwargs)
        self.setTearOffEnabled(True)
        self.setToolTipsVisible(True)
        self.icon = QtGui.QIcon(os.path.join(pcu.getPiperDirectory(), 'icons', 'piper.png'))
        self.actions = []  # stores QWidgets so that they are not garbage collected

    def onBeforePressed(self):
        pass

    def onAfterPressed(self, method):
        pass

    def add(self, name, on_pressed, *args, **kwargs):
        """
        Convenience method for adding a new item to the menu.

        Args:
            name (string): Name for the item to have on the menu

            on_pressed (method): This will be called when the item is pressed.

        Returns:
            (QtWidgets.QAction): Action item added.
        """
        def wrapper():
            self.onBeforePressed()
            on_pressed(*args, **kwargs)
            self.onAfterPressed(on_pressed)

        name = name.decode('utf-8') if sys.version.startswith('2') else name
        action = QtWidgets.QAction(name, self)
        action.triggered.connect(wrapper)

        # getting the documentation from the function
        documentation = on_pressed.__doc__
        method = on_pressed.__module__ + '.' + on_pressed.__name__
        status_tip = method + ': ' + documentation.split('Args:')[0].split('Returns:')[0] if documentation else method

        action.setToolTip(documentation)
        action.setStatusTip(status_tip)
        self.addAction(action)
        self.actions.append(action)
        return action

    def addCheckbox(self, name, state, on_pressed):
        name = name.decode('utf-8') if sys.version.startswith('2') else name
        action = QtWidgets.QAction(name, self)
        action.setCheckable(True)
        action.setChecked(state)
        action.triggered.connect(on_pressed)
        self.addAction(action)
        self.actions.append(action)
        return action

    def addMenuP(self, menu):
        return self.addMenu(menu) if menu else None


class PiperSceneMenu(PiperMenu):

    def __init__(self, title='Scene', *args, **kwargs):
        super(PiperSceneMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add('Open Current Scene in OS', self.openSceneInOS)
        self.add('Open Art Directory in OS', self.openArtDirectoryInOS)
        self.add('Open Game Directory in OS', self.openGameDirectoryInOS)
        self.add('Open Piper Directory in OS', self.openPiperDirectoryInOS)
        self.add('Open Selected Reference File', self.openSelectedReference)
        self.addSeparator()

        self.add('Copy Current Scene to Clipboard', self.copyCurrentSceneToClipboard)
        self.add('Reload Current Scene', self.reloadCurrentScene)
        self.addSeparator()

        self.add('Open Piper Documentation', self.openDocumentation)

    def openSceneInOS(self):
        pass

    def openArtDirectoryInOS(self):
        pass

    def openGameDirectoryInOS(self):
        pass

    def openSelectedReference(self):
        pass

    @staticmethod
    def openPiperDirectoryInOS():
        piper_directory = pcu.getPiperDirectory()
        pcu.openWithOS(piper_directory)

    def copyCurrentSceneToClipboard(self):
        pass

    def reloadCurrentScene(self):
        pass

    @staticmethod
    def openDocumentation():
        pcu.openDocumentation()


class PiperExportMenu(PiperMenu):

    def __init__(self, title='Export', *args, **kwargs):
        super(PiperExportMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add('Export To Game', self.exportToGame)
        self.add('Export To Current Directory', self.exportToCurrentDirectory)
        self.addSeparator()
        self.add('Export Meshes to Current as OBJ', self.exportMeshesToCurrentAsObj)
        self.addSeparator()
        self.add('Set Art Directory', self.setArtDirectory)
        self.add('Set Game Directory', self.setGameDirectory)

    def exportToGame(self):
        pass

    def exportToCurrentDirectory(self):
        pass

    def exportMeshesToCurrentAsObj(self):
        pass

    def setArtDirectory(self):
        pass

    def setGameDirectory(self):
        pass


class _PiperMainMenu(PiperMenu):

    # used to keep track of piper main menu in order to make it a singleton.
    instance = None

    def __init__(self, title='Piper', *args, **kwargs):
        # NOTE: PiperMainMenu needs its submenus defined in the DCC and its build() called by the DCC.
        super(_PiperMainMenu, self).__init__(title, *args, **kwargs)
        self.scene_menu = None
        self.nodes_menu = None
        self.export_menu = None
        self.curves_menu = None
        self.bones_menu = None
        self.rig_menu = None
        self.reference_menu = None
        self.animation_menu = None
        self.graphics_menu = None
        self.settings_menu = None
        self.on_before_reload = lambda: None

    def build(self):
        self.addMenuP(self.scene_menu)
        self.addMenuP(self.nodes_menu)
        self.addMenuP(self.export_menu)
        self.addMenuP(self.curves_menu)
        self.addMenuP(self.bones_menu)
        self.addMenuP(self.rig_menu)
        self.addMenuP(self.reference_menu)
        self.addMenuP(self.animation_menu)
        self.addMenuP(self.graphics_menu)
        self.addMenuP(self.settings_menu)
        self.addSeparator()

        self.add('Reload Piper', self.reloadPiper)

    def reloadPiper(self):
        manager.closeAll()
        self.on_before_reload()
        pcu.removeModules(path=pcu.getPiperDirectory())
        self.deleteLater()

        import setup
        setup.piperTools()


def getPiperMainMenu():
    """
    Used to create or get the Piper Main Menu, there can only be ONE in the scene at a time.

    Returns:
        (_PiperMainMenu): Piper main menu class.
    """
    _PiperMainMenu.instance = _PiperMainMenu() if _PiperMainMenu.instance is None else _PiperMainMenu.instance
    return _PiperMainMenu.instance
