#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import copy
from PySide2 import QtWidgets
import piper.ui.widget as widget


class Clipper(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(Clipper, self).__init__(*args, **kwargs)
        self.setWindowTitle('Clipper')
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

    def refresh(self):
        """
        Refreshes the clipper widget with all the animation nodes in scene and their data.
        """
        [clip_widget.remove() for clip_widget in self.anim_widgets]
        animations = self.getAnimations()
        self.anim_widgets = []

        for animation, clip_data in animations.items():
            clip_widget = AnimClip(animation_name=animation, clip_data=clip_data)
            self.main_layout.insertWidget(0, clip_widget)
            self.anim_widgets.append(clip_widget)

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
        main_layout = QtWidgets.QGridLayout(self)
        buttons_layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel(self.animation_name)
        main_layout.addWidget(label, 0, 0)

        self.table = QtWidgets.QTableWidget(1, 3)
        self.table.setHorizontalHeaderLabels(self.column_labels)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setShowGrid(False)

        main_layout.addWidget(self.table, 1, 0)

        # add button
        add_line_button = QtWidgets.QPushButton('+')
        add_line_button.clicked.connect(self.onAddLinePressed)
        buttons_layout.addWidget(add_line_button)

        # remove button
        remove_line_button = QtWidgets.QPushButton('-')
        remove_line_button.clicked.connect(self.onRemoveLinePressed)
        buttons_layout.addWidget(remove_line_button, 1)

        buttons_layout.addStretch(1)

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
        self.table.insertRow(current_row + 1)

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
            clip_name = self.table.item(row, 0)
            start = self.table.item(row, 1)
            end = self.table.item(row, 2)

            if clip_name and start and end:
                clip_name = clip_name.text()
                start = int(start.text())
                end = int(end.text())
                data[self.animation_name][clip_name] = {'start': start, 'end': end}

        return data

    def setData(self, clip_data):
        """
        Sets the given clip_data onto the table widget to easily view/edit.

        Args:
            clip_data (dictionary): Data to set into table widget.
        """
        self.table.setRowCount(len(clip_data))
        for i, (clip_name, data) in enumerate(clip_data.items()):
            clip_name_item = QtWidgets.QTableWidgetItem(clip_name)
            start_item = QtWidgets.QTableWidgetItem(str(data['start']))
            end_item = QtWidgets.QTableWidgetItem(str(data['end']))
            [self.table.setItem(i, n, item) for n, item in enumerate([clip_name_item, start_item, end_item])]
