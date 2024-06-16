#  Copyright (c) Christian Corsica. All Rights Reserved.

import sys

from Qt import QtWidgets, QtCore, QtCompat

import maya.OpenMayaUI as omui
import pymel.core as pm

import piper.config.maya as mcfg
from piper.core.dcc.template.widget_qt import WidgetQTDCC
from piper.mayapy.pipe.paths import maya_paths


if sys.version_info > (3,):
    long = int

# QObjects fall out of scope, so making them global here to keep them in scope
main_window = None
main_menu_bar = None


def getMainWindow():
    """
    Gets the Maya main window widget.

    Returns:
        (QWidget): Maya main window.
    """
    global main_window

    if main_window:
        return main_window

    main_window_ptr = omui.MQtUtil.mainWindow()
    main_window = QtCompat.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return main_window


def getMainMenuBar():
    """
    Gets the Maya main menu bar as a QMenuBar

    Returns:
        (QtWidgets.QMenuBar): The main menu bar for Maya.
    """
    global main_menu_bar

    if main_menu_bar:
        return main_menu_bar

    main_menu_bar = getMainWindow().findChild(QtWidgets.QMenuBar)
    return main_menu_bar


class Controller(object):

    def __init__(self, name, alm=False):
        """
        Class to handle interactions with pm.workspaceControl function used to add QT widgets to Maya.
        pm.workspaceControl handles docking, and stores window settings.

        Args:
            name (string): Name of the widget to pass to Maya to store.

            alm (bool): Controls whether this workspace control acts like Maya UI Elements.
            For example, this hides the tab bar and shows a toolbar grip on the end of the control to allow undocking.
        """
        self.name = name + mcfg.workspace_control_suffix
        self.alm = alm
        self.widget = None

    def create(self, label, widget, ui_script=None, close_script=None):
        """
        Creates the widget from the given ui_script and stores the window in Maya.

        Args:
            label (string): The window title.

            widget (PySide2.QtWidget): Widget to create.

            ui_script (string): Python code to run that creates widget.

            close_script (string): Python code to run when window is closed.
        """
        pm.workspaceControl(self.name, label=label)
        pm.workspaceControl(self.name, e=True, alm=self.alm)

        if ui_script:
            pm.workspaceControl(self.name, e=True, uiScript=ui_script)

        if close_script:
            pm.workspaceControl(self.name, e=True, cc=close_script)

        self.addWidgetToLayout(widget)
        self.setVisible(True)

    def restore(self, widget):
        """
        Restores the control according to the following rules:
            If collapsed then the control will be expanded
            If hidden then the control will be shown
            If minimized then the control will be restored
            If the control is an inactive tab into a tab group then it will become the active tab

        Args:
            widget (PySide2.QtWidget): Widget to restore.
        """
        self.addWidgetToLayout(widget)

    def addWidgetToLayout(self, widget):
        """
        Handles Pyside2 QtWidget implementation with pm.workspaceControl to restore window.

        Args:
            widget (PySide2.QWidget): Widget to add to Maya's layout.
        """
        if not widget:
            pm.error('No widget was given!')

        pm.workspaceControl(self.name, e=True, alm=self.alm)
        self.widget = widget
        self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

        workspace_control_ptr = long(omui.MQtUtil.findControl(self.name))
        widget_ptr = QtCompat.getCppPointer(self.widget)

        omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def exists(self):
        """
        Returns whether the widget associated with the workspace controller exists.

        Returns:
            (boolean): True if already exists.
        """
        return pm.workspaceControl(self.name, q=True, exists=True)

    def isVisible(self):
        """
        Returns whether the widget associated with the workspace controller is visible.

        Returns:
            (boolean): True if visible.
        """
        return pm.workspaceControl(self.name, q=True, visible=True)

    def setVisible(self, visible):
        """
        Sets the visibility of the widget associated with the workspace controller to the given visible value.

        Args:
            visible (boolean): Visibility to set to widget.
        """
        if visible:
            pm.workspaceControl(self.name, e=True, restore=True)
        else:
            pm.workspaceControl(self.name, e=True, visible=False)

    def setLabel(self, label):
        """
        Changes the label, aka window title, of the widget.

        Args:
            label (string): New window title.
        """
        pm.workspaceControl(self.name, e=True, label=label)

    def isFloating(self):
        """
        Returns whether the widget associated with the workspace controller is floating.

        Returns:
            (boolean): True if floating.
        """
        return pm.workspaceControl(self.name, q=True, floating=True)

    def isCollapsed(self):
        """
        Returns whether the widget associated with the workspace controller is collapsed.

        Returns:
            (boolean): True if collapsed.
        """
        return pm.workspaceControl(self.name, q=True, collapse=True)

    def close(self):
        """
        Closes the widget.

        Returns:
            (boolean): True if closing occurred.
        """
        return pm.workspaceControl(self.name, edit=True, close=True)


class MayaWidget(WidgetQTDCC):

    def __init__(self):
        super(MayaWidget, self).__init__()
        self.dcc_paths = maya_paths


maya_widget = MayaWidget()
