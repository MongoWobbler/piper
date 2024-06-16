#  Copyright (c) Christian Corsica. All Rights Reserved.

import os

from Qt import QtWidgets, QtGui

import piper.config as pcfg
import piper.core
import piper.core.pythoner as python
from piper.core.dcc.template.paths import dcc_paths
from piper.core.dcc.template.export import dcc_export
from piper.ui.widget import SecondaryAction, validateName, addMenuItem, manager


class PiperMenu(QtWidgets.QMenu):

    def __init__(self, *args, **kwargs):
        super(PiperMenu, self).__init__(*args, **kwargs)
        self.setTearOffEnabled(True)
        self.setToolTipsVisible(True)
        self.icon = QtGui.QIcon(os.path.join(piper.core.getPiperDirectory(), 'icons', 'piper.png'))
        self.parent_menu = None
        self.actions = []  # stores QWidgets so that they are not garbage collected
        self.setObjectName(self.__class__.__name__.lstrip('_'))

    def onBeforePressed(self):
        pass

    def onAfterPressed(self, method):
        pass

    def afterAdded(self):
        """
        Gets called after menu is added to a PiperMenu through the addMenuP function. Meant to be overridden.
        """
        pass

    def add(self, on_pressed, name=None, *args, **kwargs):
        """
        Convenience method for adding a new item to the menu.

        Args:
            on_pressed (method): This will be called when the item is pressed.

            name (string): Name for the item to have on the menu. If None given, will use given method's name.

        Returns:
            (QtWidgets.QAction): Action item added.
        """
        def wrapper():
            self.onBeforePressed()
            on_pressed(*args, **kwargs)
            self.onAfterPressed(on_pressed)

        action = addMenuItem(menu=self, on_pressed=wrapper, name=name, unwrapped=on_pressed)
        self.actions.append(action)
        return action

    def addSecondary(self, on_pressed, on_option, name=None, *args, **kwargs):
        """
        Adds an action item to the menu with an option box.

        Args:
            on_pressed (method): This will be called when the item is pressed.

            on_option (method): This will be called when the option box is pressed.

            name (string): Name for the item to have on the menu.

        Returns:
            (piper.ui.widget.SecondaryAction): Action item added.
        """

        def pressed_wrapper():
            self.onBeforePressed()
            on_pressed(*args, **kwargs)
            self.onAfterPressed(on_pressed)

        def option_wrapper():
            self.onBeforePressed()
            on_option(*args, **kwargs)
            self.onAfterPressed(on_pressed)

        name = validateName(on_pressed, name)
        action = SecondaryAction(name, pressed_wrapper, option_wrapper, on_pressed, on_option, self)
        self.addAction(action)
        self.actions.append(action)

        return action

    def addCheckbox(self, state, on_pressed, name=None):
        """
        Convenience method for adding a checkbox item to the menu.

        Args:
            state (boolean): Initial state of checkbox.

            on_pressed (method): This will be called when the item is pressed.

            name (string): Name for the checkbox item to have on the menu.

        Returns:
            (QtWidgets.QAction): Action item added.
        """
        name = validateName(on_pressed, name)
        action = QtWidgets.QAction(name, self)
        action.setCheckable(True)
        action.setChecked(state)
        action.triggered.connect(on_pressed)
        self.addAction(action)
        self.actions.append(action)
        return action

    def addMenuP(self, menu):
        """
        Convenience method for adding sub-menus.

        Args:
            menu (QtWidgets.QMenu): Menu to add as submenu to self.

        Returns:
            (QtWidgets.QMenu): Menu added.
        """
        if not menu or not menu.actions:
            return None

        result = self.addMenu(menu)
        menu.parent_menu = self
        menu.afterAdded()
        return result


class PiperSceneMenu(PiperMenu):

    def __init__(self, title='Scene', *args, **kwargs):
        super(PiperSceneMenu, self).__init__(title, *args, **kwargs)
        self.dcc_paths = dcc_paths
        self.build()

    def build(self):
        self.add(self.dcc_paths.openSceneInOS, 'Open Current Scene in OS')
        self.add(self.dcc_paths.openArtDirectoryInOS, 'Open Art Directory in OS')
        self.add(self.dcc_paths.openGameDirectoryInOS, 'Open Game Directory in OS')
        self.add(piper.core.openPiperDirectoryInOS, 'Open Piper Directory in OS')
        self.add(self.openSelectedReference, 'Open Selected Reference File')
        self.addSeparator()

        self.add(self.dcc_paths.copyCurrentSceneToClipboard)
        self.add(self.reloadCurrentScene)
        self.addSeparator()

        self.add(piper.core.openDocumentation, 'Open Piper Documentation')

    def openSelectedReference(self):
        pass

    def reloadCurrentScene(self):
        pass


class PiperPerforceMenu(PiperMenu):

    def __init__(self, title='Perforce', *args, **kwargs):
        super(PiperPerforceMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add(self.addScene, 'Add/Checkout Scene')
        self.addCheckbox(self.addSceneAfterSaving(), self.onAddSceneAfterSavingPressed, 'Add Scene After Saving')

    def addScene(self):
        pass

    def addSceneAfterSaving(self):
        """
        App dependent.

        Returns:
            (boolean): Setting stored in store.
        """
        return False

    def onAddSceneAfterSavingPressed(self, state):
        pass


class PiperExportMenu(PiperMenu):

    def __init__(self, title='Export', *args, **kwargs):
        super(PiperExportMenu, self).__init__(title, *args, **kwargs)
        self.dcc_paths = dcc_paths
        self.dcc_export = dcc_export
        self.game_export = None
        self.current_export = None
        self.build()

    def build(self):
        self.game_export = self.add(dcc_export.exportToGame)
        self.current_export = self.add(dcc_export.exportToCurrentDirectory)
        self.addSeparator()
        self.add(dcc_export.exportMeshesToCurrentAsObj, 'Export Meshes to Current as OBJ')
        self.aboutToShow.connect(self.updateTooltips)

    def updateTooltips(self):
        game_export = self.dcc_paths.getGameExport(error=False)
        game_tip = f'\n    Exports to: {game_export} \n' if game_export else pcfg.game_not_set
        self.game_export.setToolTip(game_tip)

        current_directory = self.dcc_paths.getSelfExport(error=False)
        art_tip = f'\n    Exports to: {current_directory} \n' if current_directory else pcfg.art_not_set
        self.current_export.setToolTip(art_tip)

    def exportToGame(self):
        pass

    def exportToCurrentDirectory(self):
        pass

    def exportMeshesToCurrentAsObj(self):
        pass


class _PiperMainMenu(PiperMenu):

    # used to keep track of piper main menu in order to make it a singleton.
    instance = None

    def __init__(self, title='Piper', *args, **kwargs):
        # NOTE: PiperMainMenu needs its submenus defined in the DCC and its build() called by the DCC.
        super(_PiperMainMenu, self).__init__(title, *args, **kwargs)
        self.scene_menu = None
        self.perforce_menu = None
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
        self.addMenuP(self.perforce_menu)
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

        self.add(self.reloadPiper)

    def reloadPiper(self):
        """
        Reloads all the piper python modules and windows.
        """
        manager.closeAll()
        self.on_before_reload()
        python.removeModules(path=piper.core.getPiperDirectory())
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
