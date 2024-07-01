#  Copyright (c) Christian Corsica. All Rights Reserved.

import maya.api.OpenMaya as om2

from Qt import QtCompat

import piper.config as pcfg
import piper.config.maya as mcfg
from piper.ui.browser import Browser
from piper.ui.widget import manager
from piper.mayapy.ui.widget import Controller
from piper.mayapy.pipe.export import maya_export
from piper.mayapy.pipe.paths import maya_paths
from piper.mayapy.pipe.store import maya_store


class MayaBrowser(Browser):

    label = pcfg.browser_name
    instance = None  # useful to be singleton while window is open
    ui_name = label
    create_command = 'import {0}; {0}.show()'.format(__name__)
    closed_command = 'import {0}; {0}.unregister()'.format(__name__)

    @property
    def mesh_config(self):
        return mcfg.browser_mesh_filter

    @property
    def skeleton_config(self):
        return mcfg.browser_skeleton_filter

    @property
    def rig_config(self):
        return mcfg.browser_rig_filter

    @property
    def animation_config(self):
        return mcfg.browser_animation_filter

    @property
    def other_config(self):
        return mcfg.browser_other_filter

    @property
    def expanded_directories_config(self):
        return mcfg.browser_expanded_directories

    def __init__(self, *args, **kwargs):
        super(MayaBrowser, self).__init__(*args, **kwargs)
        manager.register(self, self.create_command)
        self.callbacks = [om2.MSceneMessage.addCallback(om2.MSceneMessage.kBeforeSave, self.onBeforeSave),
                          om2.MSceneMessage.addCallback(om2.MSceneMessage.kAfterSave, self.onAfterSave),
                          om2.MSceneMessage.addCallback(om2.MSceneMessage.kAfterOpen, self.onAfterOpen)]
        self.setObjectName(self.__class__.ui_name)
        self.controller = None
        self.needs_reload = False

    def build(self):
        self.dcc_paths = maya_paths
        self.dcc_export = maya_export
        self.store = maya_store
        super(MayaBrowser, self).build()

    def onBeforeSave(self, *_):
        """
        Called before scene is saved to know if file doesn't exist and widget tree needs to reload to add new file.
        """
        self.needs_reload = not bool(self.dcc_paths.getCurrentScene())

    def onAfterSave(self, *_):
        """
        Called after scene is saved to know if new file was added and file path exists now.
        """
        if self.needs_reload and self.dcc_paths.getCurrentScene():
            self.reload(select_current=True, save_expanded_directories=True)

        self.needs_reload = False

    def onAfterOpen(self, *_):
        """
        Called after scene is opened to select the item that is associated with the current scene.
        """
        if not self.is_batching:
            self.selectScene(display_not_found=False)

    def onClosePressed(self):
        """
        This method should be called when window closes. Stores window's settings and removes callback(s).
        """
        om2.MMessage.removeCallbacks(self.callbacks)
        super(MayaBrowser, self).onClosePressed()

    def showInMaya(self):
        """
        Creates the controller to handle Maya integration with this class' widget. This replaces widget.show
        """
        self.controller = Controller(self.__class__.ui_name)

        if self.controller.exists():
            self.controller.restore(self)
        else:
            self.controller.create(self.label, self, ui_script=self.create_command, close_script=self.closed_command)

        self.controller.setVisible(True)


def get():
    """
    Gets the instance to the widget since it is meant to be a singleton.

    Returns:
        (MayaBrowser): Widget created.
    """
    MayaBrowser.instance = MayaBrowser() if MayaBrowser.instance is None else MayaBrowser.instance
    return MayaBrowser.instance


def unregister():
    """
    Unregisters widget from the widget manager.
    """
    if MayaBrowser.instance is None:
        return

    MayaBrowser.instance.onClosePressed()
    manager.unregister(MayaBrowser.instance)
    QtCompat.delete(MayaBrowser.instance)
    MayaBrowser.instance = None


def show():
    """
    Convenience method for showing MayaProjects.

    Returns:
        (MayaProjects): QtWidget being shown.
    """
    art_directory = maya_paths.getArtDirectory()
    if not art_directory:
        maya_paths.warn('Please set art directory in Projects before opening Browser window.')
        return None

    instance = get()
    instance.showInMaya()
    return instance
