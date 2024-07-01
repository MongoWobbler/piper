#  Copyright (c) Christian Corsica. All Rights Reserved.

from Qt import QtWidgets, QtCore, QtGui

import piper.core
import piper.config as pcfg
from piper.ui.widget import setTips


class Switcher(QtWidgets.QDialog):

    @property
    def update_config(self):
        raise NotImplementedError

    @property
    def key_config(self):
        raise NotImplementedError

    @property
    def match_config(self):
        raise NotImplementedError

    @property
    def translate_config(self):
        raise NotImplementedError

    @property
    def rotate_config(self):
        raise NotImplementedError

    @property
    def orient_config(self):
        raise NotImplementedError

    @property
    def scale_config(self):
        raise NotImplementedError

    def __init__(self, dcc_store=None, *args, **kwargs):
        super(Switcher, self).__init__(*args, **kwargs)

        self.icons_directory = piper.core.getIconsDirectory()
        self.setWindowTitle(pcfg.switcher_name)
        self.store = dcc_store
        self.self_update = None
        self.keyframe_box = None
        self.match_only = None
        self.translate = None
        self.rotate = None
        self.orient = None
        self.scale = None
        self.spaces_list = None
        self.switcher_list = None
        self.pivots_list = None
        self.rest_list = None
        self.all_controls_button = None
        self.all_inner_button = None
        self.selected_inner_button = None
        self.bendy_button = None
        self.joints_button = None
        self.hide_play_button = None
        self.build()

        self.store_data = {self.self_update: self.update_config,
                           self.keyframe_box: self.key_config,
                           self.match_only: self.match_config,
                           self.translate: self.translate_config,
                           self.rotate: self.rotate_config,
                           self.orient: self.orient_config,
                           self.scale: self.scale_config}

        self.restorePrevious()

    def createButton(self, icon, layout, on_pressed, checkable=True):
        """
        Convenience method for creating a toggleable button.

        Args:
            icon (string): Name of .png file in icons directory to assign to button as icon

            layout (QtWidgets.QLayout): Layout to add button to.

            on_pressed (method): Called when button is pressed.

            checkable (boolean): If True, will set button to be checkable type.

        Returns:
            (QtWidgets.QPushButton): Button created.
        """
        button = QtWidgets.QToolButton()
        button.setCheckable(checkable)
        setTips(on_pressed, button)
        icon = QtGui.QIcon(self.icons_directory + '/{}.png'.format(icon))
        button.setIcon(icon)
        button.clicked.connect(on_pressed)
        layout.addWidget(button)

        return button

    @staticmethod
    def createList(layout, on_pressed):
        """
        Convenience method for creating a QListWidget with no focus that gets added to given layout.

        Args:
            layout (QtWidgets.QLayout): Layout to add QListWidget to.

            on_pressed (method): Called when any item of list is clicked.

        Returns:
            (QtWidgets.QListWidget): List widget created.
        """
        widget = QtWidgets.QListWidget()
        widget.itemClicked.connect(on_pressed)
        widget.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(widget, alignment=QtCore.Qt.AlignTop)
        return widget

    @staticmethod
    def createBox(name, layout, checked=True, on_pressed=None):
        """
        Convenience method for creating a QCheckBox with given name in given layout with given checked state.

        Args:
            name (string): Name/text of QCheckbox.

            layout (QWidgets.QLayout): Layout to add QCheckBox to.

            checked (boolean): Checked state of box.

            on_pressed (method): If given, will connect to stateChanged signal of QCheckBox.

        Returns:
            (QtWidgets.QCheckBox): QCheckBox created.
        """
        box = QtWidgets.QCheckBox(name)
        box.setChecked(checked)
        layout.addWidget(box, alignment=QtCore.Qt.AlignJustify)

        if on_pressed:
            box.stateChanged.connect(on_pressed)

        return box

    def build(self):
        # creating layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        buttons_layout = QtWidgets.QHBoxLayout()
        function_boxes_layout = QtWidgets.QHBoxLayout()
        transform_boxes_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(0)

        # toggle buttons
        self.createButton('selectAll', buttons_layout, self.onSelectAllPressed, checkable=False)
        self.all_controls_button = self.createButton('allControls', buttons_layout, self.onAllControlsPressed)
        self.all_inner_button = self.createButton('innerControls', buttons_layout, self.onInnerControlsPressed)
        self.selected_inner_button = self.createButton('selectedInner', buttons_layout, self.onSelectedInnerPressed)
        self.bendy_button = self.createButton('bendyControls', buttons_layout, self.onBendyPressed)
        self.joints_button = self.createButton('joints', buttons_layout, self.onJointsPressed)
        self.hide_play_button = self.createButton('hideOnPlay', buttons_layout, self.onHideOnPlayPressed)
        self.createButton('reset', buttons_layout, self.onResetPressed, checkable=False)
        self.createButton('out_piperRig', buttons_layout, self.onRigPressed, checkable=False)

        main_layout.addLayout(buttons_layout)

        # function checkboxes
        self.match_only = self.createBox('Match Only', function_boxes_layout, False)
        self.self_update = self.createBox('Update', function_boxes_layout, on_pressed=self.onUpdatePressed)
        self.keyframe_box = self.createBox('Key', function_boxes_layout)

        main_layout.addLayout(function_boxes_layout)

        # transform checkboxes
        self.translate = self.createBox('T', transform_boxes_layout)
        self.rotate = self.createBox('R', transform_boxes_layout)
        self.orient = self.createBox('O', transform_boxes_layout, False)
        self.scale = self.createBox('S', transform_boxes_layout)

        main_layout.addLayout(transform_boxes_layout)

        # widget list views, setting focus off so user can use keyboard shortcuts after changing space
        self.spaces_list = self.createList(main_layout, self.onSpacePressed)
        self.switcher_list = self.createList(main_layout, self.onSwitcherPressed)
        self.pivots_list = self.createList(main_layout, self.onPivotPressed)
        self.rest_list = self.createList(main_layout, self.onPivotRestPressed)

        main_layout.addStretch()

    def restorePrevious(self):
        """
        Restores the previous settings the window had when it was closed.
        """
        if not self.store:
            return

        {box.setChecked(self.store.get(name)) for box, name in self.store_data.items()}

    @staticmethod
    def updateList(widget, spaces, minimum=0):
        """
        Updates the given widget with the given spaces list to be used as items as long as it meets the given minimum.
        If no spaces does not meet minimum, widget will be hidden.

        Args:
            widget (QtWidgets.QListWidget): Widget to add names in given spaces to.

            spaces (iterable): Strings that will be added as items to given widget.

            minimum (int): Minimum length given spaces must be to add and show widget.
        """
        widget.clear()

        if len(spaces) <= minimum:
            widget.hide()
            return

        [widget.addItem(QtWidgets.QListWidgetItem(item)) for item in spaces]
        widget.setFixedHeight(widget.sizeHintForRow(0) * widget.count() + 2 * widget.frameWidth())
        widget.show()

    def onUpdatePressed(self, state):
        """
        Updates the widget when the update checkbox is pressed to True.

        Args:
            state (boolean): State of checkbox.
        """
        if state:
            self.onSelectionChanged()

    def onClosedPressed(self):
        """
        This method should be called when window closes. Stores window's settings.
        """
        if not self.store:
            return

        {self.store.set(name, box.isChecked(), write=False) for box, name in self.store_data.items()}
        self.store.writeSettings()

    def onSelectionChanged(self, *args):
        """
        App dependent.
        """
        pass

    def onSpacePressed(self, item):
        """
        App dependent.
        """
        pass

    def onSwitcherPressed(self, item):
        """
        App dependent.
        """
        pass

    def onPivotPressed(self, item):
        """
        App dependent.
        """
        pass

    def onPivotRestPressed(self, item):
        """
        App dependent.
        """
        pass

    def onSelectAllPressed(self):
        """
        App dependent.
        """
        pass

    def onAllControlsPressed(self):
        """
        App dependent.
        """
        pass

    def onInnerControlsPressed(self):
        """
        App dependent.
        """
        pass

    def onSelectedInnerPressed(self):
        """
        App dependent.
        """
        pass

    def onBendyPressed(self):
        """
        App dependent.
        """
        pass

    def onJointsPressed(self):
        """
        App dependent.
        """
        pass

    def onHideOnPlayPressed(self):
        """
        App dependent.
        """
        pass

    def onResetPressed(self):
        """
        App dependent.
        """
        pass

    def onRigPressed(self):
        """
        App dependent.
        """
        pass
