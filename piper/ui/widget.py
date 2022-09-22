#  Copyright (c) Christian Corsica. All Rights Reserved.

from Qt import QtWidgets, QtCore, QtGui

import piper.config as pcfg
from piper.core.store import piper_store


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
        self.widgets = {}
        self.is_looping = False

    def register(self, widget, create_command):
        """
        Adds a widget to the manager's list.

        Args:
            widget (QtWidget): Widget to register

            create_command (string): Command used to create and show widget.
        """
        self.widgets[widget] = create_command

    def unregister(self, widget):
        """
        Removes a widget from the manager list.

        Args:
            widget (QtWidget): Widget to remove from manager.
        """
        if not self.is_looping:
            self.widgets.pop(widget)

    def closeAll(self, store_previous=True):
        """
        Calls the close method on all widgets currently held by manager and unregisters them.

        Args:
            store_previous (boolean): If True, will store the opened widgets into the settings.
        """
        self.is_looping = True

        if store_previous:
            commands = list(self.widgets.values())
            piper_store.set(pcfg.previous_widgets, commands)

        [widget.close() for widget in self.widgets]
        self.widgets = {}
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


def getUserInput(title, description, parent=None, password=False):
    """
    Asks the user for input, displays a dialog box for user to type in input.

    Args:
        title (string): Window title for dialog box.

        description (string): Description of what to ask user.

        parent (QtWidget): Parent of QInputDialog.

        password (boolean): If True, will hide characters that user types.

    Returns:
        (string or boolean): If pressed OK, and user typed something in, return True, else False.
    """
    input_dialog = QtWidgets.QInputDialog(parent=parent)
    line_type = QtWidgets.QLineEdit.Password if password else QtWidgets.QLineEdit.Normal
    answer, pressed_ok = input_dialog.getText(input_dialog, title, description, line_type)
    return str(answer) if answer and pressed_ok else False


def addRemoveButtons(on_add_pressed, on_remove_pressed):
    """
    Creates two buttons vertically that are connected to the given methods

    Args:
        on_add_pressed (method): Called when the "+" button is pressed.

        on_remove_pressed (method): Called when the "-" button is pressed.

    Returns:
        (QtWidgets.QVBoxLayout): Layout that created buttons belong to.
    """
    buttons_layout = QtWidgets.QVBoxLayout()
    font = QtGui.QFont('Arial', 12)

    # add button
    add_line_button = QtWidgets.QPushButton('+')
    add_line_button.clicked.connect(on_add_pressed)
    add_line_button.setFont(font)
    buttons_layout.addWidget(add_line_button)

    # remove button
    remove_line_button = QtWidgets.QPushButton('-')
    remove_line_button.clicked.connect(on_remove_pressed)
    remove_line_button.setFont(font)
    buttons_layout.addWidget(remove_line_button, 1)

    buttons_layout.addStretch(1)
    return buttons_layout


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


class TreeNodeItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, *args, **kwargs):
        """
        QTreeWidgetItem with the ability to set multiple checkboxes of its TreeWidget when multiple are selected.
        """
        super(TreeNodeItem, self).__init__(*args, **kwargs)
        self.parent_widget = self.treeWidget()

    def setData(self, column, role, value):
        """
        Overriding setData function to set multiple checkboxes state when several rows are highlighted.
        Role == 10 means checkbox state is being updated.

        Args:
            column (int): Index of column to set data for.

            role (int): Data role that is being set.

            value (any): Data being passed.
        """
        # sets the checkbox state for all items selected
        if role == 10 and not self.parent_widget.is_updating and self.treeWidget().selectedItems():
            self.parent_widget.is_updating = True
            items = self.treeWidget().selectedItems()

            [item.setData(column, role, value) for item in items]
            self.parent_widget.items_to_select = items

        super(TreeNodeItem, self).setData(column, role, value)


class TreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, *args, **kwargs):
        """
        Tree Widget that holds whether the widget is being updated or not in order to prevent duplicate commands.
        As well as items to select when checkboxes get selected in order to not lose currently selected items.
        """
        super(TreeWidget, self).__init__(*args, **kwargs)
        self.is_updating = False
        self.items_to_select = []


manager = getManager()
