#  Copyright (c) Christian Corsica. All Rights Reserved.

import shiboken2
import pymel.core as pm

from piper.ui.vert_selector import VertSelector
from piper.ui.widget import manager
from piper.mayapy.ui.widget import Controller
import piper.mayapy.rig.skin as skin
import piper.mayapy.util as myu


class MayaVertSelector(VertSelector):

    label = 'Weighted Vert Selector'
    instance = None  # useful to be singleton while window is open
    ui_name = label.replace(' ', '')  # same as label, but without spaces
    create_command = 'import {0}; {0}.show()'.format(__name__)
    closed_command = 'import {0}; {0}.unregister()'.format(__name__)

    def __init__(self, *args, **kwargs):
        super(MayaVertSelector, self).__init__(*args, **kwargs)

        self.setObjectName(self.__class__.ui_name)
        self.controller = None
        manager.register(self)

    def showInMaya(self):
        """
        Creates the controller to handle Maya integration with this class' widget. This replaces widget.show
        """
        self.controller = Controller(self.__class__.ui_name)

        if self.controller.exists():
            self.controller.restore(self)
        else:
            self.controller.create(self.label, self, ui_script=self.create_command, close_script=self.closed_command)

        self.controller.setVisible(True)

    def onSelectPressed(self, *args, **kwargs):
        """
        Selects the verts based on the input of the operator and slider value.
        """
        threshold = self.slider.value()
        operator = self.combobox.currentText()
        joints = myu.validateSelect(find='joint', minimum=1)
        skin.selectWeightedVerts(joints=joints, operator=operator, threshold=threshold)
        self.last_selected = joints
        self.last_selected_button.setText('Previously: ' + ', '.join([joint.name() for joint in joints]))

    def onLastSelectedPressed(self, *args, **kwargs):
        """
        Selects the verts based on the input of the operator and slider value and the last selected joints
        """
        joints = self.last_selected

        if not joints:
            warning = 'Use Select Weighted Verts First!'
            self.last_selected_button.setText(warning)
            pm.warning(warning)
            return

        threshold = self.slider.value()
        operator = self.combobox.currentText()
        skin.selectWeightedVerts(joints=joints, operator=operator, threshold=threshold)

    def close(self, *args, **kwargs):
        """
        Overriding close method to use the controller class function instead.

        Returns:
            (string): Name of workspace control closed.
        """
        self.controller.close()


def get():
    """
    Gets the instance to the widget since it is meant to be a singleton.

    Returns:
        (MayaVertSelector): Widget created.
    """
    MayaVertSelector.instance = MayaVertSelector() if MayaVertSelector.instance is None else MayaVertSelector.instance
    return MayaVertSelector.instance


def unregister():
    """
    Unregisters widget from the widget manager.
    """
    if MayaVertSelector.instance is None:
        return

    manager.unregister(MayaVertSelector.instance)
    shiboken2.delete(MayaVertSelector.instance)
    MayaVertSelector.instance = None


def show():
    """
    Convenience method for showing the MayaVertSelector widget.

    Returns:
        (MayaVertSelector): Widget shown.
    """
    instance = get()
    instance.showInMaya()
    return instance
