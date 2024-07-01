#  Copyright (c) Christian Corsica. All Rights Reserved.

import copy
from Qt import QtWidgets, QtCore

import piper.config as pcfg
import piper.ui.widget as widget


class Clipper(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(Clipper, self).__init__(*args, **kwargs)
        self.setWindowTitle(pcfg.clipper_name)
        self.anim_widgets = []
        self.main_layout = None

        self.build()
        self.refresh()

    def build(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        button_layout = QtWidgets.QHBoxLayout()

        widget.separator(self.main_layout)

        refresh_button = QtWidgets.QPushButton('Refresh')
        refresh_button.clicked.connect(self.refresh)
        button_layout.addWidget(refresh_button)

        save_button = QtWidgets.QPushButton('Save')
        save_button.clicked.connect(self.onSavePressed)
        button_layout.addWidget(save_button)

        self.main_layout.addLayout(button_layout)

    def refresh(self, *args):
        """
        Refreshes the clipper widget with all the animation nodes in scene and their data.

        Returns:
            (Dictionary): All animations found in scene as key with their clip_data as value.
        """
        [clip_widget.remove() for clip_widget in self.anim_widgets]
        animations = self.getAnimations()
        self.anim_widgets = []

        for animation, clip_data in animations.items():
            clip_widget = AnimClip(animation_name=animation, clip_data=clip_data)
            self.main_layout.insertWidget(0, clip_widget)
            self.anim_widgets.append(clip_widget)

        return animations

    def getAnimations(self):
        """
        App dependent.

        Returns:
            (Dictionary): All animations found in scene
        """
        pass

    def onSavePressed(self):
        """
        App dependent.
        """
        pass


class AnimClip(QtWidgets.QWidget):
    """
    Widget that holds the animation clip information.
    """
    def __init__(self, animation_name='', clip_data=None, *args, **kwargs):
        super(AnimClip, self).__init__(*args, **kwargs)

        self.animation_name = animation_name
        self.column_labels = ['Clip Suffix', 'Start', 'End']
        self.default_data = {self.animation_name: {}}
        self.table = None

        self.build()

        if clip_data:
            self.setData(clip_data)

    def build(self):
        # layout
        main_layout = QtWidgets.QGridLayout(self)

        # clip name
        label = QtWidgets.QLabel(self.animation_name)
        main_layout.addWidget(label, 0, 0)

        # table
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(self.column_labels)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setShowGrid(True)
        self.onAddLinePressed()  # creating first line
        main_layout.addWidget(self.table, 1, 0)

        # add/remove buttons
        buttons_layout = widget.addRemoveButtons(self.onAddLinePressed, self.onRemoveLinePressed)
        main_layout.addLayout(buttons_layout, 1, 1)

    def getSelectedRows(self):
        """
        Gets the selected rows.

        Returns:
            (list): A bunch of integers representing the selected row number(s).
        """
        return list(set(index.row() for index in self.table.selectedIndexes()))

    def onAddLinePressed(self):
        """
        Adds a row line to the table widget to the row after the one selected.
        """
        current_row = self.table.currentIndex().row()
        new_row = current_row + 1
        self.table.insertRow(new_row)

        clip_item = QtWidgets.QTableWidgetItem()
        clip_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        clip_item.setCheckState(QtCore.Qt.Checked)
        self.table.setItem(new_row, 0, clip_item)

    def onRemoveLinePressed(self):
        """
        Removes all the selected row lines.
        """
        rows = self.getSelectedRows()
        rows.sort(reverse=True)  # reversing since deleting lines will throw off row number, reversing prevents that.
        [self.table.removeRow(row) for row in rows]

    def remove(self):
        """
        Convenience method for deleting the AnimClip widget.
        """
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()

    def getData(self):
        """
        Gets all the data stored in the table view as a dictionary.

        Returns:
            (dictionary): Data that was written into the table widget.
        """
        data = copy.deepcopy(self.default_data)

        for row in range(self.table.rowCount()):
            clip_item = self.table.item(row, 0)
            start = self.table.item(row, 1)
            end = self.table.item(row, 2)

            if clip_item and start and end:
                should_export = clip_item.checkState() == QtCore.Qt.Checked
                clip_name = clip_item.text()
                start = int(start.text())
                end = int(end.text())
                data[self.animation_name][clip_name] = {'export': should_export, 'start': start, 'end': end}

        return data

    def setData(self, clip_data):
        """
        Sets the given clip_data onto the table widget to easily view/edit.

        Args:
            clip_data (dictionary): Data to set into table widget.
        """
        self.table.setRowCount(len(clip_data))
        for i, (clip_name, data) in enumerate(clip_data.items()):
            state = QtCore.Qt.Checked if data.get('export') else QtCore.Qt.Unchecked
            clip_item = QtWidgets.QTableWidgetItem(clip_name)
            clip_item.setText(clip_name)
            clip_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            clip_item.setCheckState(state)

            start_item = QtWidgets.QTableWidgetItem(str(data['start']))
            end_item = QtWidgets.QTableWidgetItem(str(data['end']))
            [self.table.setItem(i, n, item) for n, item in enumerate([clip_item, start_item, end_item])]
