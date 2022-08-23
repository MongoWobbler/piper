#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue

import piper.config.unreal as ucfg
import piper.core
import piper.core.namer as namer
import piper.core.pythoner as python
import piper.unrealpy.copier as copier


class _PiperMenu(object):

    # used to keep track of piper main menu in order to make it a singleton.
    instance = None

    def __init__(self, label=ucfg.menu_label, section=None):
        self.main = None
        self.owner = None
        self.menus = []
        self.section = 'Scripts'
        self.label = label
        self.on_before_reload = lambda: None
        self.main_menu_name = 'LevelEditor.MainMenu'
        self.context_menu_name = 'ContentBrowser.AssetContextMenu'
        self.folder_context_menu_name = 'ContentBrowser.FolderContextMenu'
        self.actor_context_menu_name = 'LevelEditor.ActorContextMenu'
        self.piper_main_menu_name = self.main_menu_name + '.' + self.label
        self.piper_context_menu_name = self.context_menu_name + '.' + self.label
        self.piper_folder_menu_name = self.folder_context_menu_name + '.' + self.label
        self.tool = ue.ToolMenus.get()

        if section:
            self.section = section

    def __enter__(self):
        """
        Context manager enter method.

        Returns:
            (piper.uepy.ui.menu._PiperMenu): Class that holds all methods for creating menu in Unreal.
        """
        self.buildContext()
        self.buildFolder()
        self.buildMain()
        return self.instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method.
        """
        self.refresh()

    def setOwner(self, owner_name, section):
        """
        Set the owning menu for when the add method is used.

        Args:
            owner_name (string): Full name to menu, such as LevelEditor.MainMenu.Piper

            section (string): Section to set.

        Returns:
            (unreal.ToolMenu): Tool Menu with matching given owner_name. Will raise Error if not found.
        """
        self.owner = self.tool.find_menu(ue.Name(owner_name))
        self.section = section

        if not self.owner:
            raise ValueError(f'{owner_name} Menu not found to attach custom python menu.')

        return self.owner

    def setMainMenuAsOwner(self, section):
        """
        Convenience method for setting Unreal Main Menu as the owner.
        """
        return self.setOwner(self.main_menu_name, section)

    def setContextMenuAsOwner(self, section):
        """
        Convenience method for setting Unreal Right Click Context Menu as the owner.
        """
        return self.setOwner(self.context_menu_name, section)

    def setFolderContextMenuAsOwner(self, section):
        """
        Convenience method for setting Unreal Right Click Folder Context Menu as the owner.
        """
        return self.setOwner(self.folder_context_menu_name, section)

    def setPiperMainMenuAsOwner(self, section):
        """
        Convenience method for setting Piper Main Menu as the owner.
        """
        return self.setOwner(self.piper_main_menu_name, section)

    def setPiperContextMenuAsOwner(self, section):
        """
        Convenience method for setting Piper Right Click Asset Browser Context Menu as the owner.
        """
        return self.setOwner(self.piper_context_menu_name, section)

    def setPiperFolderMenuAsOwner(self, section):
        """
        Convenience method for setting Piper Right Click Folder Browser Context Menu as the owner.
        """
        return self.setOwner(self.piper_folder_menu_name, section)

    def _build(self, method, section):
        """
        Used to build main menus

        Args:
            method (method): Must set the owning menu.

            section (string): Section name to be set as current section.
        """
        method(section)
        name = self.owner.get_name()
        new_menu = self.owner.add_sub_menu(name, ue.Name(self.section), ue.Name(self.label), ue.Text(self.label))
        self.menus.append(new_menu)

    def buildMain(self):
        """
        Convenience method for building the Piper Main Menu.
        """
        self._build(self.setMainMenuAsOwner, 'Main')

    def buildContext(self):
        """
        Convenience method for building the Piper Right Click Asset Browser Context Menu.
        """
        self._build(self.setContextMenuAsOwner, 'Common')

    def buildFolder(self):
        """
        Convenience method for building the Piper Right Click Folder Browser Context Menu.
        """
        self._build(self.setFolderContextMenuAsOwner, 'Common')

    def add(self, method, label=None):
        """
        Adds an entry to the currently set owning menu.

        Args:
            method (method): Function to execute when entry is pressed.

            label (string): Label that entry will have. If None given, will use method's sentence case as label.

        Returns:
            (unreal.ToolMenuEntry): Entry object created for unreal menus.
        """
        module = method.__module__
        full_method = module + '.' + method.__name__
        command = f'import {module}; {full_method}()'
        label = namer.toSentenceCase(method.__name__) if label is None else label
        entry = ue.ToolMenuEntry(name=full_method, type=ue.MultiBlockType.MENU_ENTRY)

        entry.set_label(ue.Text(label))
        entry.set_tool_tip(method.__doc__ + f'\n\nFound in: {full_method}')
        entry.set_string_command(ue.ToolMenuStringCommandType.PYTHON, ue.Name(''), command)
        self.owner.add_menu_entry(self.section, entry)
        return entry

    def refresh(self):
        """
        Refreshes all widgets. Must be called after menu or entry is added for it to show up.
        """
        self.tool.refresh_all_widgets()

    def remove(self, menu):
        """
        Unregisters and removes the given menu from Unreal.

        Args:
            menu (unreal.ToolMenu): Tool Menu to remove from Unreal UI.
        """
        self.tool.unregister_owner_by_name(menu.menu_name)
        self.tool.remove_menu(menu.menu_name)
        self.menus.remove(menu)

    def removeAll(self):
        """
        Unregisters and removes all menus added by _PiperMenu.
        """
        [self.remove(menu) for menu in reversed(self.menus)]
        self.menus = []
        self.refresh()


def getPiperMenu():
    """
    Used to create or get the Piper Main Menu, there can only be ONE in the scene at a time.

    Returns:
        (piper.uepy.ui.menu._PiperMenu): Piper main menu class.
    """
    _PiperMenu.instance = _PiperMenu() if _PiperMenu.instance is None else _PiperMenu.instance
    return _PiperMenu.instance


def reloadPiper():
    """
    Reloads all the piper python modules and windows.
    """
    menu = getPiperMenu()
    menu.removeAll()
    python.removeModules(path=piper.core.getPiperDirectory())

    import setup
    setup.piperTools()


def create():
    """
    Creates the piper main menu and adds it to Unreal's main menu bar.
    """
    menu = getPiperMenu()
    with menu:
        menu.setPiperMainMenuAsOwner('Developer')
        menu.add(reloadPiper)

        menu.setPiperContextMenuAsOwner('Scripts')
        menu.add(copier.assetNames, 'Copy Asset Names')
        menu.add(copier.packageNames, 'Copy Package Names')

        menu.setPiperFolderMenuAsOwner('Scripts')
        menu.add(copier.directoryPaths, 'Copy Directories\' Paths')
        menu.add(copier.directoryAssetNames, 'Copy Directories\' Asset Names')
        menu.add(copier.directoryPackageNames, 'Copy Directories\' Package Names')
