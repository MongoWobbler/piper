#  Copyright (c) Christian Corsica. All Rights Reserved.

from functools import partial
from PySide2 import QtWidgets
import piper.core.util as pcu
import piper.ui.widget as widget


class VertSelector(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(VertSelector, self).__init__(*args, **kwargs)
        self.setWindowTitle('Weighted Vert Selector')
        self.combobox = None
        self.slider = None
        self.last_selected = None
        self.last_selected_button = None

        self.build()

    def build(self):
        # layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        input_layout = QtWidgets.QHBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()

        # combo box with operators
        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(pcu.operators.keys())
        input_layout.addWidget(self.combobox)

        # slider with threshold value
        self.slider = QtWidgets.QDoubleSpinBox()
        self.slider.setMaximum(1.0)
        self.slider.setValue(1.0)
        self.slider.setSingleStep(0.05)
        input_layout.addWidget(self.slider)

        # buttons for commonly used values
        for i in [0.05, 0.25, 0.5, 0.75, 1.0]:
            weight_button = QtWidgets.QPushButton(str(i))
            weight_button.clicked.connect(partial(self.slider.setValue, i))
            weight_button.setMinimumWidth(10)
            button_layout.addWidget(weight_button)

        # button that calls select weighted verts function
        self.last_selected_button = QtWidgets.QPushButton('Use Select Weighted Verts First!')
        self.last_selected_button.clicked.connect(self.onLastSelectedPressed)

        # button that calls select weighted verts function
        select_verts_button = QtWidgets.QPushButton('Select Weighted Verts')
        select_verts_button.clicked.connect(self.onSelectPressed)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)

        widget.separator(main_layout)
        main_layout.addWidget(select_verts_button)
        main_layout.addWidget(self.last_selected_button)

    def onSelectPressed(self, *args, **kwargs):
        """
        To be implemented in inherited child class.
        """
        pass

    def onLastSelectedPressed(self, *args, **kwargs):
        """
        To be implemented in inherited child class.
        """
        pass
