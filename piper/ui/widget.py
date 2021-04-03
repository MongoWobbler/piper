#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

from PySide2 import QtWidgets


class _Manager(object):

    # used to keep track of Manager in order to make it a singleton.
    instance = None

    def __init__(self, *args, **kwargs):
        """
        Holds all open Piper PySide GUIs. Useful for closing all of them in case of reload.
        """
        super(_Manager, self).__init__(*args, **kwargs)
        self.widgets = set()
        self.is_looping = False

    def register(self, widget):
        """
        Adds a widget to the manager's list.

        Args:
            widget (QtWidget): Widget to register
        """
        self.widgets.add(widget)

    def unregister(self, widget):
        """
        Removes a widget from the manager list.

        Args:
            widget (QtWidget): Widget to remove from manager.
        """
        if not self.is_looping:
            self.widgets.remove(widget)

    def closeAll(self):
        """
        Calls the close method on all widgets currently held by manager and unregisters them.
        """
        self.is_looping = True
        [widget.close() for widget in self.widgets]
        self.widgets = set()
        self.is_looping = False


def getManager():
    """
    Used to create or get the Piper Main Menu, there can only be ONE in the scene at a time.

    Returns:
        (_Manager): Piper main menu class.
    """
    _Manager.instance = _Manager() if _Manager.instance is None else _Manager.instance
    return _Manager.instance


def separator(layout=None, *args, **kwargs):
    """
    Creates a separator widget (horizontal line)

    Args:
        layout (QtWidgets.QLayout): Layout to add separator to.

    Returns:
        (QtWidgets.QFrame): Widget created.
    """
    line = QtWidgets.QFrame()
    line.setFixedHeight(20)
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    line.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

    if layout:
        layout.addWidget(line, *args, **kwargs)

    return line


manager = getManager()
