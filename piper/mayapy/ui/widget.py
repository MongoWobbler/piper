#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import sys

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance, getCppPointer

import maya.OpenMayaUI as omui
import pymel.core as pm


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
    main_window = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
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


class WorkspaceControl(object):

    def __init__(self, name):
        self.name = name
        self.widget = None

    def create(self, label, widget, ui_script=None, close_script=None):

        pm.workspaceControl(self.name, label=label)

        if ui_script:
            pm.workspaceControl(self.name, e=True, uiScript=ui_script)

        if close_script:
            pm.workspaceControl(self.name, e=True, cc=close_script)

        self.addWidgetToLayout(widget)
        self.setVisible(True)

    def restore(self, widget):
        self.addWidgetToLayout(widget)

    def addWidgetToLayout(self, widget):
        if widget:
            self.widget = widget
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

            workspace_control_ptr = long(omui.MQtUtil.findControl(self.name))
            widget_ptr = long(getCppPointer(self.widget)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def exists(self):
        return pm.workspaceControl(self.name, q=True, exists=True)

    def isVisible(self):
        return pm.workspaceControl(self.name, q=True, visible=True)

    def setVisible(self, visible):
        if visible:
            pm.workspaceControl(self.name, e=True, restore=True)
        else:
            pm.workspaceControl(self.name, e=True, visible=False)

    def setLabel(self, label):
        pm.workspaceControl(self.name, e=True, label=label)

    def isFloating(self):
        return pm.workspaceControl(self.name, q=True, floating=True)

    def isCollapsed(self):
        return pm.workspaceControl(self.name, q=True, collapse=True)