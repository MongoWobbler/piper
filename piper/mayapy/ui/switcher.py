#  Copyright (c) Christian Corsica. All Rights Reserved.

import maya.api.OpenMaya as om2
import pymel.core as pm

from Qt import QtCompat

import piper.config as pcfg
import piper.config.maya as mcfg
import piper.core.pythoner as python

from piper.ui.widget import manager
from piper.ui.switcher import Switcher

from piper.mayapy.pipe.store import maya_store
from piper.mayapy.ui.widget import Controller
import piper.mayapy.rig as rig
import piper.mayapy.rig.space as space
import piper.mayapy.rig.control as control
import piper.mayapy.rig.switcher as switcher
import piper.mayapy.selection as selection


class MayaSwitcher(Switcher):

    label = pcfg.switcher_name
    instance = None  # useful to be singleton while window is open
    ui_name = label.replace(' ', '')  # same as label, but without spaces
    create_command = 'import {0}; {0}.show()'.format(__name__)
    closed_command = 'import {0}; {0}.unregister()'.format(__name__)

    @property
    def update_config(self):
        return mcfg.switcher_update_box

    @property
    def key_config(self):
        return mcfg.switcher_key_box

    @property
    def match_config(self):
        return mcfg.switcher_match_box

    @property
    def translate_config(self):
        return mcfg.switcher_translate_box

    @property
    def rotate_config(self):
        return mcfg.switcher_rotate_box

    @property
    def orient_config(self):
        return mcfg.switcher_orient_box

    @property
    def scale_config(self):
        return mcfg.switcher_scale_box

    def __init__(self, dcc_store=None, *args, **kwargs):
        super(MayaSwitcher, self).__init__(dcc_store=dcc_store, *args, **kwargs)
        manager.register(self, self.create_command)
        self.setObjectName(self.__class__.ui_name)
        self.controller = None
        self.callback = om2.MEventMessage.addEventCallback('SelectionChanged', self.onSelectionChanged)
        self.selected = None
        self.inners = []
        self.pivots = []
        self.rests = []

        self.onSelectionChanged()  # called to load/update switcher on startup

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

    def restorePrevious(self):
        """
        Restores the previous settings the window had when it was closed.
        """
        # all controls state
        rigs = pm.ls(type='piperRig')
        states = [attr.get() for r in rigs for attr in r.listAttr(v=True, k=True, st='*' + mcfg.visibility_suffix)]
        state = not all(states)
        self.all_controls_button.setChecked(state)

        # all bendy controls state
        bendy_controls = control.getAllBendy()
        state = not all([ctrl.visibility.get() for ctrl in bendy_controls])
        self.bendy_button.setChecked(state)

        # joints state
        state = not all([joint.visibility.get() for joint in pm.ls(type='joint') if joint not in bendy_controls])
        self.joints_button.setChecked(state)

        # hide/play state
        controls = control.getAll()
        state = all([ctrl.hideOnPlayback.get() for ctrl in controls]) if controls else False
        self.hide_play_button.setChecked(state)

        # inner controls state
        controls = control.getAllInner()
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
        spaces = python.OrderedSet(['local'])
        switchers = set()
        self.pivots = python.OrderedSet()
        self.rests = python.OrderedSet()
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

                if child_name.endswith(mcfg.dynamic_pivot_suffix + mcfg.control_suffix):
                    self.pivots.add(child_name)
                    self.rests.add(child.attr(mcfg.dynamic_pivot_rest).get())

                # adding inner controls for visibility toggle
                if mcfg.inner_suffix in child_name and child != node:
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
        [attr.set(state) for r in rigs for attr in r.listAttr(ud=True, v=True, k=True, st='*' + mcfg.visibility_suffix)]
        pm.undoInfo(closeChunk=True)

    def onInnerControlsPressed(self):
        """
        Toggles between showing/hiding all inner controls.
        """
        controls = control.getAllInner()
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

    def onBendyPressed(self):
        """
        Toggles between showing/hiding all bendy controls.
        """
        controls = control.getAllBendy()
        state = not self.bendy_button.isChecked()
        pm.undoInfo(openChunk=True)
        [ctrl.visibility.set(state) for ctrl in controls]
        pm.undoInfo(closeChunk=True)

    def onJointsPressed(self):
        """
        Toggles between showing/hiding all joints in scene.
        """
        joints = pm.ls(type='joint')
        bendy_controls = control.getAllBendy()
        joints = filter(lambda i: i not in bendy_controls, joints)
        state = not self.joints_button.isChecked()
        pm.undoInfo(openChunk=True)
        for joint in joints:
            joint.visibility.set(state)
            joint.hiddenInOutliner.set(not state)
        pm.undoInfo(closeChunk=True)

        # refreshes any opened outliner editors in order to hide joints
        editors = pm.lsUI(editors=True)
        [pm.outlinerEditor(ed, e=True, refresh=True) for ed in editors if pm.outlinerEditor(ed, exists=True)]

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
        rigs = selection.get('piperRig')
        pm.select(rigs)

    def close(self, *_, **__):
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
        (MayaSwitcher): Widget created.
    """
    if MayaSwitcher.instance is None:
        MayaSwitcher.instance = MayaSwitcher(dcc_store=maya_store)

    return MayaSwitcher.instance


def unregister():
    """
    Unregisters widget from the widget manager.
    """
    if MayaSwitcher.instance is None:
        return

    MayaSwitcher.instance.onClosedPressed()
    om2.MMessage.removeCallback(MayaSwitcher.instance.callback)
    manager.unregister(MayaSwitcher.instance)
    QtCompat.delete(MayaSwitcher.instance)
    MayaSwitcher.instance = None
    

def show():
    """
    Convenience method for showing MayaSwitcher.

    Returns:
        (MayaSwitcher): QtWidget being shown.
    """
    instance = get()
    instance.showInMaya()
    return instance
