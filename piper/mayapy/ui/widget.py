#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import sys
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


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
