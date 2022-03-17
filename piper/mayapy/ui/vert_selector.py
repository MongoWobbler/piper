#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from piper.ui.vert_selector import VertSelector
from piper.ui.widget import manager
import piper.mayapy.rig.skin as skin
import piper.mayapy.util as myu


class MayaVertSelector(MayaQWidgetDockableMixin, VertSelector):

    def __init__(self, *args, **kwargs):
        super(MayaVertSelector, self).__init__(*args, **kwargs)
        manager.register(self)

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

    def dockCloseEventTriggered(self):
        """
        Happens when VertSelector window closes, useful to unregister for widget window manager.
        """
        manager.unregister(self)
        super(MayaVertSelector, self).dockCloseEventTriggered()


def show():
    """
    Convenience method for showing the MayaVertSelector widget.

    Returns:
        (MayaVertSelector): Widget created.
    """
    gui = MayaVertSelector()
    gui.show(dockable=True)
    return gui
