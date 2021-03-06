#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMaya as om
import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
from piper.ui.widget import manager
from piper.ui.switcher import Switcher
from piper.mayapy.pipe.store import store
import piper.mayapy.rig as rig
import piper.mayapy.rig.space as space
import piper.mayapy.rig.control as control
import piper.mayapy.rig.switcher as switcher
import piper.mayapy.pipernode as pipernode


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

    def restorePrevious(self):
        """
        Restores the previous settings the window had when it was closed.
        """
        # all controls state
        rigs = pm.ls(type='piperRig')
        states = [attr.get() for gig in rigs for attr in gig.listAttr(v=True, k=True, st='*' + pcfg.visibility_suffix)]
        state = not all(states)
        self.all_controls_button.setChecked(state)

        # joints state
        state = not all([joint.visibility.get() for joint in pm.ls(type='joint')])
        self.joints_button.setChecked(state)

        # hide/play state
        controls = control.getAll()
        state = all([ctrl.hideOnPlayback.get() for ctrl in controls]) if controls else False
        self.hide_play_button.setChecked(state)

        # inner controls state
        controls = control.getAllInnerControls()
        state = not all([ctrl.visibility.get() for ctrl in controls])
        self.all_inner_button.setChecked(state)
        super(MayaSwitcher, self).restorePrevious()

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
                child_name = child.name(stripNamespace=True)

                if child_name.endswith(pcfg.dynamic_pivot_suffix + pcfg.control_suffix):
                    self.pivots.add(child_name)
                    self.rests.add(child.attr(pcfg.dynamic_pivot_rest).get())

                # adding inner controls for visibility toggle
                if child_name.startswith(pcfg.fk_prefix) and child != node:
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
        o = self.orient.isChecked()
        s = self.scale.isChecked()
        k = self.keyframe_box.isChecked()

        # parsing name since None == local space in space.switch argument
        name = item.text()
        if name == 'local':
            name = None

        pm.undoInfo(openChunk=True)
        [space.switch(n, name, t=t, r=r, o=o, s=s, key=k) for n in self.selected if name is None or n.hasAttr(name)]
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

    def onSelectAllPressed(self):
        """
        Selects all the controls.
        """
        controls = control.getAll()
        pm.select(controls)

    def onAllControlsPressed(self):
        """
        Toggles between showing/hiding all controls.
        """
        rigs = pm.ls(type='piperRig')
        state = not self.all_controls_button.isChecked()
        pm.undoInfo(openChunk=True)
        [attr.set(state) for r in rigs for attr in r.listAttr(ud=True, v=True, k=True, st='*' + pcfg.visibility_suffix)]
        pm.undoInfo(closeChunk=True)

    def onInnerControlsPressed(self):
        """
        Toggles between showing/hiding all inner controls.
        """
        controls = control.getAllInnerControls()
        state = not self.all_inner_button.isChecked()
        pm.undoInfo(openChunk=True)
        [ctrl.visibility.set(state) for ctrl in controls]
        pm.undoInfo(closeChunk=True)

    def onSelectedInnerPressed(self):
        """
        Toggles between showing/hiding selected controls' inner control.
        """
        state = not self.selected_inner_button.isChecked()
        pm.undoInfo(openChunk=True)
        [ctrl.visibility.set(state) for ctrl in self.inners]
        pm.undoInfo(closeChunk=True)

    def onJointsPressed(self):
        """
        Toggles between showing/hiding all joints in scene.
        """
        joints = pm.ls(type='joint')
        state = not self.joints_button.isChecked()
        pm.undoInfo(openChunk=True)
        [joint.visibility.set(state) for joint in joints]
        pm.undoInfo(closeChunk=True)

    def onHideOnPlayPressed(self):
        """
        Toggles between showing/hiding controls during playback.
        """
        controls = control.getAll()
        state = self.hide_play_button.isChecked()
        pm.undoInfo(openChunk=True)
        [ctrl.hideOnPlayback.set(state) for ctrl in controls]
        pm.undoInfo(closeChunk=True)

    def onResetPressed(self):
        """
        Sets the selected controls to zero/bind pose. If no controls selected, zeroes out all controls in scene.
        """
        pm.undoInfo(openChunk=True)
        rig.zeroOut()
        pm.undoInfo(closeChunk=True)

    def onRigPressed(self):
        """
        Selects the rigs associated with current selection. If nothing selected, selects all piperRigs in scene.
        """
        rigs = pipernode.get('piperRig')
        pm.select(rigs)

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
