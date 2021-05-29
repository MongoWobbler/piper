#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os

from PySide2 import QtWidgets, QtCore, QtGui

import piper_config as pcfg
import piper.core.util as pcu
from piper.ui.widget import separator


class Switcher(QtWidgets.QDialog):

    def __init__(self, dcc_store=None, *args, **kwargs):
        super(Switcher, self).__init__(*args, **kwargs)

        piper_directory = pcu.getPiperDirectory()
        self.icons_directory = os.path.join(piper_directory, 'maya', 'icons')

        self.setWindowTitle('Switcher')
        self.store = dcc_store
        self.self_update = None
        self.keyframe_box = None
        self.match_only = None
        self.translate = None
        self.rotate = None
        self.scale = None
        self.spaces_list = None
        self.switcher_list = None
        self.pivots_list = None
        self.rest_list = None
        self.all_controls_button = None
        self.all_inner_button = None
        self.selected_inner_button = None
        self.joints_button = None
        self.hide_play_button = None
        self.build()

        self.store_data = {self.self_update: pcfg.switcher_update_box,
                           self.keyframe_box: pcfg.switcher_key_box,
                           self.match_only: pcfg.switcher_match_box,
                           self.translate: pcfg.switcher_translate_box,
                           self.rotate: pcfg.switcher_rotate_box,
                           self.scale: pcfg.switcher_scale_box}

        self.restorePrevious()

    def createButton(self, icon, layout, on_pressed):
        """
        Convenience method for creating a toggleable button.

        Args:
            icon (string): Name of .png file in icons directory to assign to button as icon

            layout (QtWidgets.QLayout): Layout to add button to.

            on_pressed (method): Called when button is pressed.

        Returns:
            (QtWidgets.QPushButton): Button created.
        """
        button = QtWidgets.QToolButton()
        button.setCheckable(True)
        button.setToolTip(on_pressed.__doc__)
        button.setStatusTip(on_pressed.__doc__)
        icon = QtGui.QIcon(self.icons_directory + '/{}.png'.format(icon))
        button.setIcon(icon)
        button.clicked.connect(on_pressed)
        layout.addWidget(button)

        return button

    def build(self):
        main_layout = QtWidgets.QGridLayout(self)
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(0)

        # select all controls button
        select_button = QtWidgets.QToolButton()
        select_button.setToolTip(self.onSelectAllPressed.__doc__)
        select_button.setStatusTip(self.onSelectAllPressed.__doc__)
        icon = QtGui.QIcon(self.icons_directory + '/{}.png'.format('selectAll'))
        select_button.setIcon(icon)
        select_button.clicked.connect(self.onSelectAllPressed)
        buttons_layout.addWidget(select_button)

        # toggle buttons
        self.all_controls_button = self.createButton('allControls', buttons_layout, self.onAllControlsPressed)
        self.all_inner_button = self.createButton('innerControls', buttons_layout, self.onInnerControlsPressed)
        self.selected_inner_button = self.createButton('selectedInner', buttons_layout, self.onSelectedInnerPressed)
        self.joints_button = self.createButton('joints', buttons_layout, self.onJointsPressed)
        self.hide_play_button = self.createButton('hideOnPlay', buttons_layout, self.onHideOnPlayPressed)

        # reset/zero out/bind pose button
        reset_button = QtWidgets.QToolButton()
        reset_button.setToolTip(self.onResetPressed.__doc__)
        reset_button.setStatusTip(self.onResetPressed.__doc__)
        icon = QtGui.QIcon(self.icons_directory + '/{}.png'.format('reset'))
        reset_button.setIcon(icon)
        reset_button.clicked.connect(self.onResetPressed)
        buttons_layout.addWidget(reset_button)

        main_layout.addLayout(buttons_layout, 0, 0, 1, 3)

        # used only for fk/ik so that we match position without changing FK/IK attribute
        self.match_only = QtWidgets.QCheckBox('Match Only')
        main_layout.addWidget(self.match_only, 1, 0)

        # update on selection changed if this box is set to True
        self.self_update = QtWidgets.QCheckBox('Update')
        self.self_update.setChecked(True)
        self.self_update.stateChanged.connect(self.onUpdatePressed)
        main_layout.addWidget(self.self_update, 1, 1)

        # keyframe checkbox
        self.keyframe_box = QtWidgets.QCheckBox('Key')
        self.keyframe_box.setChecked(True)
        main_layout.addWidget(self.keyframe_box, 1, 2)

        # separator(main_layout, 2, 0, 1, 3)
        main_layout.setRowMinimumHeight(2, 0)

        # inherit translate from space if True
        self.translate = QtWidgets.QCheckBox('Translate')
        self.translate.setChecked(True)
        main_layout.addWidget(self.translate, 3, 0)

        # inherit rotate from space if True
        self.rotate = QtWidgets.QCheckBox('Rotate')
        self.rotate.setChecked(True)
        main_layout.addWidget(self.rotate, 3, 1)

        # inherit scale from space if True
        self.scale = QtWidgets.QCheckBox('Scale')
        self.scale.setChecked(True)
        main_layout.addWidget(self.scale, 3, 2)

        # widget list views, setting focus off so user can use keyboard shortcuts after changing space
        self.spaces_list = QtWidgets.QListWidget()
        self.spaces_list.itemClicked.connect(self.onSpacePressed)
        self.spaces_list.setFocusPolicy(QtCore.Qt.NoFocus)
        main_layout.addWidget(self.spaces_list, 4, 0, 1, 3)

        self.switcher_list = QtWidgets.QListWidget()
        self.switcher_list.itemClicked.connect(self.onSwitcherPressed)
        self.switcher_list.setFocusPolicy(QtCore.Qt.NoFocus)
        main_layout.addWidget(self.switcher_list, 5, 0, 1, 3)

        self.pivots_list = QtWidgets.QListWidget()
        self.pivots_list.itemClicked.connect(self.onPivotPressed)
        self.pivots_list.setFocusPolicy(QtCore.Qt.NoFocus)
        main_layout.addWidget(self.pivots_list, 6, 0, 1, 2)

        self.rest_list = QtWidgets.QListWidget()
        self.rest_list.itemClicked.connect(self.onPivotRestPressed)
        self.rest_list.setFocusPolicy(QtCore.Qt.NoFocus)
        main_layout.addWidget(self.rest_list, 7, 2)
        main_layout.setRowStretch(8, 1)

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

        {self.store.set(name, box.isChecked()) for box, name in self.store_data.items()}

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
