#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

from PySide2 import QtWidgets, QtCore
from piper.ui.widget import separator


class Switcher(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(Switcher, self).__init__(*args, **kwargs)

        self.setWindowTitle('Switcher')
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
        self.build()

    def build(self):
        main_layout = QtWidgets.QGridLayout(self)

        # update on selection changed if this box is set to True
        self.self_update = QtWidgets.QCheckBox('Update')
        self.self_update.setChecked(True)
        self.self_update.stateChanged.connect(self.onUpdatePressed)
        main_layout.addWidget(self.self_update, 0, 0)

        # keyframe checkbox
        self.keyframe_box = QtWidgets.QCheckBox('Key')
        self.keyframe_box.setChecked(True)
        main_layout.addWidget(self.keyframe_box, 0, 1)

        # used only for fk/ik so that we match position without changing FK/IK attribute
        self.match_only = QtWidgets.QCheckBox('FK/IK Match Only')
        main_layout.addWidget(self.match_only, 0, 2)

        separator(main_layout, 1, 0, 1, 3)

        # inherit translate from space if True
        self.translate = QtWidgets.QCheckBox('Translate')
        self.translate.setChecked(True)
        main_layout.addWidget(self.translate, 2, 0)

        # inherit rotate from space if True
        self.rotate = QtWidgets.QCheckBox('Rotate')
        self.rotate.setChecked(True)
        main_layout.addWidget(self.rotate, 2, 1)

        # inherit scale from space if True
        self.scale = QtWidgets.QCheckBox('Scale')
        self.scale.setChecked(True)
        main_layout.addWidget(self.scale, 2, 2)

        # widget list views, setting focus off so user can use keyboard shortcuts after changing space
        self.spaces_list = QtWidgets.QListWidget()
        self.spaces_list.itemClicked.connect(self.onSpacePressed)
        self.spaces_list.setFocusPolicy(QtCore.Qt.NoFocus)
        main_layout.addWidget(self.spaces_list, 3, 0, 1, 3)

        self.switcher_list = QtWidgets.QListWidget()
        self.switcher_list.itemClicked.connect(self.onSwitcherPressed)
        self.switcher_list.setFocusPolicy(QtCore.Qt.NoFocus)
        main_layout.addWidget(self.switcher_list, 4, 0, 1, 3)

        self.pivots_list = QtWidgets.QListWidget()
        self.pivots_list.itemClicked.connect(self.onPivotPressed)
        self.pivots_list.setFocusPolicy(QtCore.Qt.NoFocus)
        main_layout.addWidget(self.pivots_list, 5, 0, 1, 2)

        self.rest_list = QtWidgets.QListWidget()
        self.rest_list.itemClicked.connect(self.onPivotRestPressed)
        self.rest_list.setFocusPolicy(QtCore.Qt.NoFocus)
        main_layout.addWidget(self.rest_list, 5, 2)

        main_layout.setRowStretch(6, 1)

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
