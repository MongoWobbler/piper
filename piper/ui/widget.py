#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

from PySide2 import QtWidgets, QtCore, QtGui


BOX_ICON = [
    '16 16 4 1',
    '  c None',
    '. c #c6c4c4',
    'l c #888888',
    ': c #909090',
    '                ',
    '                ',
    '                ',
    '                ',
    '    llllllll    ',
    '    l      l    ',
    '    l      l    ',
    '    l      l    ',
    '    l      l    ',
    '    l      l    ',
    '    l      l    ',
    '    l      l    ',
    '    llllllll    ',
    '                ',
    '                ',
    '                ',
    '                ',
    '                ',
]


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


def setTips(method, widget):
    """
    Sets the tool and status tips on the given widget based on the given method.

    Args:
        method (method): Method to get documentation, module, and name from.

        widget (QtWidget): Widget to set status and tool tip with method's documentation.
    """
    # getting the documentation from the function
    documentation = method.__doc__
    module = method.__module__ + '.' + method.__name__
    status_tip = module + ': ' + documentation.split('Args:')[0].split('Returns:')[0] if documentation else module
    widget.setToolTip(documentation)
    widget.setStatusTip(status_tip)


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


class SecondaryAction(QtWidgets.QWidgetAction):

    def __init__(self, name, main_wrapped, secondary_wrapped, main_action, secondary_action, *args, **kwargs):
        """
        Custom action with a clickable icon.
        NOTE: STYLE SHEET NEEDS WORK TO MATCH!!!
        Credit to the authors: https://groups.google.com/g/python_inside_maya/c/um49_7Ou56g

        Args:
            name (string): Name for action/text.

            main_wrapped (method): Method to run when main label is pressed (documentation is hidden).

            secondary_wrapped (method): Method to run when icon is pressed (documentation is hidden).

            main_action (method): Method unwrapped to get documentation from.

            secondary_action (method): Method unwrapped to get documentation from.
        """
        super(SecondaryAction, self).__init__(*args, **kwargs)
        self.label = None
        self.icon = None
        self.name = name
        self.main_wrapped = main_wrapped
        self.main_action = main_action
        self.secondary_wrapped = secondary_wrapped
        self.secondary_action = secondary_action

    def createWidget(self, parent):
        frame = QtWidgets.QFrame(parent)
        frame.setObjectName('mainWidget')

        self.label = SecondaryLabel(self.name, parent)
        self.label.setObjectName('myLabel')
        setTips(self.main_action, self.label)

        self.icon = SecondaryLabel(parent)
        self.icon.setPixmap(QtGui.QPixmap(BOX_ICON))
        setTips(self.secondary_action, self.icon)

        layout = QtWidgets.QHBoxLayout(frame)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label, stretch=1)
        layout.addWidget(self.icon, stretch=0)

        frame.setStyleSheet("""
            #mainWidget { padding: 4px; margin:0px; }
            #myLabel { padding-left: 14px; background-color: transparent; }
            #mainWidget:hover, #myLabel:hover {
                background: palette(highlight);
                color: palette(highlighted-text);
                }
                """)

        self.label.clicked.connect(self.trigger)
        self.label.clicked.connect(self.main_wrapped)
        self.icon.clicked.connect(self.trigger)
        self.icon.clicked.connect(self.secondary_wrapped)

        return frame

    def trigger(self):
        super(SecondaryAction, self).trigger()
        e = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Escape, QtCore.Qt.NoModifier)
        QtCore.QCoreApplication.postEvent(self.parent(), e)


class SecondaryLabel(QtWidgets.QLabel):
    clicked = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        """
        Label to be used with SecondaryAction class in order to get clicked mouse events.
        """
        super(SecondaryLabel, self).__init__(*args, **kwargs)

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()


manager = getManager()
