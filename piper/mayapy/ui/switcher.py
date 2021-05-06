#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMaya as om
import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
from piper.ui.widget import manager
from piper.ui.switcher import Switcher
from piper.mayapy.pipe.store import store
import piper.mayapy.rig.space as space
import piper.mayapy.rig.switcher as switcher


class MayaSwitcher(MayaQWidgetDockableMixin, Switcher):

    def __init__(self, maya_store=None, *args, **kwargs):
        super(MayaSwitcher, self).__init__(dcc_store=maya_store, *args, **kwargs)
        manager.register(self)
        self.callback = om.MEventMessage.addEventCallback('SelectionChanged', self.onSelectionChanged)
        self.selected = None
        self.inners = []
        self.pivots = []
        self.rests = []

        self.onSelectionChanged()  # called to load/update switcher on startup

    def onSelectionChanged(self, *args):
        """
        Main update function called every time user selects a node.
        """
        # don't update list if user does not want to update.
        if not self.self_update.isChecked():
            return

        # declare iterables to add to
        names = []
        inners_state = []
        self.inners.clear()
        spaces = pcu.OrderedSet(['local'])
        switchers = set()
        self.pivots = pcu.OrderedSet()
        self.rests = pcu.OrderedSet()
        self.selected = pm.selected()

        # gather info we need
        for node in self.selected:

            # skip over is node is not a transform, for example: don't need verts, faces, etc.
            if not isinstance(node, pm.nodetypes.Transform):
                continue

            node_name = node.name()
            names.append(node_name)

            # get all the space attributes from the node
            node_spaces = space.getAll(node)
            spaces.update(node_spaces)

            # get fk/ik switcher controls
            fk_ik_switcher = switcher.get(node, error=False, name=True)
            if fk_ik_switcher:
                switchers.add(fk_ik_switcher)

            # grabs children of node and node to see if any are dynamic pivots
            for child in node.getChildren() + [node]:
                child_name = child.nodeName()

                if child_name.endswith(pcfg.dynamic_pivot_suffix + pcfg.control_suffix):
                    self.pivots.add(child_name)
                    self.rests.add(child.attr(pcfg.dynamic_pivot_rest).get())

                # adding inner controls for visibility toggle
                if child.startswith(pcfg.fk_prefix) and child != node:
                    visibility = child.visibility.get()
                    inners_state.append(visibility)
                    self.inners.append(child)

        # update window title with selected and lists widgets with info we gathered
        text = ' - ' + ', '.join(names) if names else ''
        self.setWindowTitle('Switcher' + text)
        self.updateList(self.spaces_list, spaces, minimum=1)
        self.updateList(self.switcher_list, switchers)
        self.updateList(self.pivots_list, self.pivots)
        self.updateList(self.rest_list, self.rests)

        inner_state = not all(inners_state)
        self.selected_inner_button.setChecked(inner_state)

    def onSpacePressed(self, item):
        """
        Called when a space item is clicked. Attempts to match all selected items to that space.

        Args:
            item (QtWidgets.QListWidgetItem): Space pressed that will match selected objects if they have the space.
        """
        t = self.translate.isChecked()
        r = self.rotate.isChecked()
        s = self.scale.isChecked()
        k = self.keyframe_box.isChecked()

        # parsing name since None == local space in space.switch argument
        name = item.text()
        if name == 'local':
            name = None

        pm.undoInfo(openChunk=True)
        [space.switch(node, name, t=t, r=r, s=s, key=k) for node in self.selected if name is None or node.hasAttr(name)]
        pm.undoInfo(closeChunk=True)

    def onSwitcherPressed(self, item):
        """
        Called when a FK/IK switcher item is clicked.

        Args:
            item (QtWidgets.QListWidgetItem): FK/IK switcher clicked that will have its FK or IK matched.
        """
        key = self.keyframe_box.isChecked()
        match = self.match_only.isChecked()

        pm.undoInfo(openChunk=True)
        space.switchFKIK(pm.PyNode(item.text()), key=key, match_only=match)
        pm.undoInfo(closeChunk=True)

    def onPivotPressed(self, item):
        """
        Called when dynamic pivot item is clicked. Will set dynamic pivot transforms to 0.
        #
        Args:
            item (QtWidgets.QListWidgetItem): Dynamic pivot to reset when clicked.
        """
        pm.undoInfo(openChunk=True)
        space.resetDynamicPivot(pm.PyNode(item.text()), key=self.keyframe_box.isChecked())
        pm.undoInfo(closeChunk=True)

    def onPivotRestPressed(self, item):
        """
        Called when dynamic pivot item is clicked. Will move dynamic pivot to its rest position.

        Args:
            item (QtWidgets.QListWidgetItem): Dynamic pivot to move to rest position when clicked.
        """
        pm.undoInfo(openChunk=True)
        index = self.rest_list.indexFromItem(item)
        pivot_item = self.pivots_list.item(index.row())
        space.resetDynamicPivot(pm.PyNode(pivot_item.text()), key=self.keyframe_box.isChecked(), rest=True)
        pm.undoInfo(closeChunk=True)

    def onAllControlsPressed(self):
        """
        App dependent.
        """
        if not pm.objExists(pcfg.control_set):
            return

        control_set = pm.PyNode(pcfg.control_set)
        controls = control_set.members() if self.all_inner_button.isChecked() else control_set.members(flatten=True)
        controls = filter(lambda node: not isinstance(node, pm.nodetypes.ObjectSet), controls)
        state = not self.all_controls_button.isChecked()
        [ctrl.visibility.set(state) for ctrl in controls]

    def onInnerControlsPressed(self):
        """
        App dependent.
        """
        if not pm.objExists(pcfg.inner_controls):
            return

        control_set = pm.PyNode(pcfg.inner_controls)
        controls = control_set.members()
        state = not self.all_inner_button.isChecked()
        [ctrl.visibility.set(state) for ctrl in controls]

    def onSelectedInnerPressed(self):
        """
        App dependent.
        """
        state = not self.selected_inner_button.isChecked()
        [ctrl.visibility.set(state) for ctrl in self.inners]

    def onJointsPressed(self):
        """
        App dependent.
        """
        joints = pm.ls(type='joint')
        state = not self.joints_button.isChecked()
        [joint.visibility.set(state) for joint in joints]

    def dockCloseEventTriggered(self):
        self.onClosedPressed()
        manager.unregister(self)
        om.MMessage.removeCallback(self.callback)
        super(MayaSwitcher, self).dockCloseEventTriggered()


def show():
    """
    Convenience method for showing MayaSwitcher.

    Returns:
        (MayaSwitcher): QtWidget being shown.
    """
    gui = MayaSwitcher(maya_store=store)
    gui.show(dockable=True)
    return gui
