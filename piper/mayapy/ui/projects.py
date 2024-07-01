#  Copyright (c) Christian Corsica. All Rights Reserved.

import maya.api.OpenMaya as om2

from Qt import QtCompat

import piper.config as pcfg
from piper.ui.widget import manager
from piper.ui.projects import Projects
from piper.mayapy.ui.widget import Controller
from piper.mayapy.settings import setStartupWorkspace
from piper.mayapy.pipe.paths import maya_paths
from piper.mayapy.pipe.export import maya_export
from piper.mayapy.ui.widget import maya_widget


class MayaProjects(Projects):

    label = pcfg.projects_name
    instance = None  # useful to be singleton while window is open
    ui_name = label
    create_command = 'import {0}; {0}.show()'.format(__name__)
    closed_command = 'import {0}; {0}.unregister()'.format(__name__)

    def __init__(self, *args, **kwargs):
        super(MayaProjects, self).__init__(*args, **kwargs)
        manager.register(self, self.create_command)
        self.callbacks = [om2.MSceneMessage.addCallback(om2.MSceneMessage.kAfterOpen, self.updateDirectoryLines),
                          om2.MSceneMessage.addCallback(om2.MSceneMessage.kAfterNew, self.updateDirectoryLines)]
        self.setObjectName(self.__class__.ui_name)
        self.controller = None

    def build(self):
        self.dcc_paths = maya_paths
        self.dcc_export = maya_export
        self.dcc_widget = maya_widget
        super(MayaProjects, self).build()

    def showInMaya(self):
        """
        Creates the controller to handle Maya integration with this class' widget. This replaces widget.show
        """
        self.controller = Controller(self.__class__.ui_name, alm=True)

        if self.controller.exists():
            self.controller.restore(self)
        else:
            self.controller.create(self.label, self, ui_script=self.create_command, close_script=self.closed_command)

        self.controller.setVisible(True)

    def setProject(self, name):
        """
        Sets the current project to the given name.

        Args:
            name (string or None): Name of project to be used as the current project.
        """
        super(MayaProjects, self).setProject(name)
        setStartupWorkspace()

    def close(self, *_, **__):
        """
        Overriding close method to use the controller class function instead.

        Returns:
            (string): Name of workspace control closed.
        """
        self.controller.close()


def get():
    """
    Gets the instance to the widget since it is meant to be a singleton.

    Returns:
        (MayaProjects): Widget created.
    """
    MayaProjects.instance = MayaProjects() if MayaProjects.instance is None else MayaProjects.instance
    return MayaProjects.instance


def unregister():
    """
    Unregisters widget from the widget manager.
    """
    if MayaProjects.instance is None:
        return

    om2.MMessage.removeCallbacks(MayaProjects.instance.callbacks)
    manager.unregister(MayaProjects.instance)
    QtCompat.delete(MayaProjects.instance)
    MayaProjects.instance = None


def show():
    """
    Convenience method for showing MayaProjects.

    Returns:
        (MayaProjects): QtWidget being shown.
    """
    instance = get()
    instance.showInMaya()
    return instance
