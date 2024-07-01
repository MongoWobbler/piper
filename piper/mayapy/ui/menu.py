#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm

from Qt import QtWidgets

import piper.config as pcfg
import piper.config.maya as mcfg

import piper.core.filer as filer
import piper.core.pather as pather

import piper.mayapy.rig as rig
import piper.mayapy.rig.bone as bone
import piper.mayapy.rig.skin as skin
import piper.mayapy.rig.xform as xform
import piper.mayapy.rig.curve as curve
import piper.mayapy.rig.space as space
import piper.mayapy.rig.control as control
import piper.mayapy.graphics as graphics
import piper.mayapy.settings as settings
import piper.mayapy.ui.browser as mybrowser
import piper.mayapy.ui.clipper as myclipper
import piper.mayapy.ui.projects as myprojects
import piper.mayapy.ui.switcher as myswitcher
import piper.mayapy.ui.vert_selector as myvert_selector
import piper.mayapy.ui.widget as mywidget
import piper.mayapy.ui.window as mywindow
import piper.mayapy.pipe.perforce as perforce
import piper.mayapy.mesh as mesh
import piper.mayapy.modifier as modifier
import piper.mayapy.plugin as plugin
import piper.mayapy.pipernode as pipernode
import piper.mayapy.attribute as attribute
import piper.mayapy.animation as animation
import piper.mayapy.animation.key as key
import piper.mayapy.animation.resolution as resolution

from piper.core.store import piper_store
from piper.mayapy.pipe.paths import maya_paths
from piper.mayapy.pipe.export import maya_export
from piper.mayapy.pipe.store import maya_store
from piper.ui.menu import PiperMenu, PiperSceneMenu, PiperPerforceMenu, PiperExportMenu, getPiperMainMenu


class MayaPiperMenu(PiperMenu):
    """
    Implements undo chunks so that a whole piper function call is undone instead of only parts of it at a time.
    """
    def onBeforePressed(self):
        pm.undoInfo(openChunk=True)

    def onAfterPressed(self, method):
        pm.undoInfo(closeChunk=True)

        # repeat last command
        module = method.__module__
        full_method = module + '.' + method.__name__
        pm.repeatLast(ac='python("import {}; {}()")'.format(module, full_method), acl=full_method)


class MayaSceneMenu(PiperSceneMenu):

    def build(self):
        self.dcc_paths = maya_paths
        self.add(mybrowser.show, 'Browser')
        self.addSeparator()
        super(MayaSceneMenu, self).build()

    def reloadCurrentScene(self):
        """
        Reopens the current scene. Prompts the user to save if there are unsaved changes.
        """
        scene_path = pm.sceneName()
        if not scene_path:
            return

        if not mywindow.save():
            return

        pm.openFile(scene_path, force=True)

    def openSelectedReference(self, node=None):
        """
        Opens the last selected object's reference file.

        Args:
            node (PyNode): Node to get reference file of.
        """
        if not node:
            node = pm.selected()[-1]

        if not node:
            pm.warning('Nothing Selected!')
            return

        if not node.isFromReferencedFile():
            pm.warning(node.nodeName() + ' is not from a referenced file!')
            return

        if not mywindow.save():
            return

        path = node.referenceFile().path
        pm.openFile(path, force=True)


class MayaPerforceMenu(PiperPerforceMenu):

    def afterAdded(self):
        state = maya_store.get(mcfg.use_perforce)
        self.menuAction().setVisible(state)

    def addScene(self):
        perforce.makeAvailable()

    def addSceneAfterSaving(self):
        """
        App dependent.

        Returns:
            (boolean): Setting stored in store.
        """
        return maya_store.get(mcfg.p4_add_after_save)

    def onAddSceneAfterSavingPressed(self, state):
        maya_store.set(mcfg.p4_add_after_save, state)


class MayaExportMenu(PiperExportMenu):

    def build(self):
        self.dcc_paths = maya_paths
        self.dcc_export = maya_export
        super(MayaExportMenu, self).build()

class MayaCurvesMenu(MayaPiperMenu):

    def __init__(self, title='Curves', *args, **kwargs):
        super(MayaCurvesMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        [self.add(curve_method) for curve_method in curve.methods]
        self.addSeparator()
        self.add(curve.crossSection, 'Create Curve(s) From Cross Section')
        self.add(curve.originCrossSection, 'Create Cross Section Curve at Origin')
        self.addSeparator()
        self.add(curve.layoutAll, 'Layout All Curves')
        self.add(curve.layoutColors, 'Layout All Colors')


class MayaNodesMenu(MayaPiperMenu):

    def __init__(self, title='Nodes', *args, **kwargs):
        super(MayaNodesMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add(pipernode.createMesh)
        self.add(pipernode.createSkinnedMesh)
        self.add(pipernode.createAnimation)
        self.addSeparator()
        self.add(mesh.assignCollisions)


class MayaBonesMenu(MayaPiperMenu):

    def __init__(self, title='Bones', *args, **kwargs):
        super(MayaBonesMenu, self).__init__(title, *args, **kwargs)
        self.binder = skin.Binder()
        self.build()

    def build(self):
        self.add(bone.createAtPivot)
        self.add(xform.parent)
        self.add(xform.mirrorTranslate)
        self.add(xform.mirrorRotate)
        self.add(bone.assignLabels)
        self.add(bone.assignBindAttributes)
        self.add(attribute.addDelete, 'Add Delete Attribute')
        self.add(bone.setSegmentScaleCompensateOff, 'Turn Off Segment Scale Compensate')
        self.add(skin.returnToBindPose)
        self.addSeparator()
        self.add(bone.rotationToJointOrient)
        self.add(bone.jointOrientToRotation)
        self.addSeparator()
        self.add(skin.selectWeightedVerts, 'Select Fractionally Weighted Verts')
        self.add(myvert_selector.show, 'Select Weighted Verts')
        self.addSeparator()
        self.add(self.binder.unbind)
        self.add(self.binder.rebind)
        self.addSeparator()
        self.add(bone.health, 'Health Check')


class MayaRigMenu(MayaPiperMenu):

    def __init__(self, title='Rig', *args, **kwargs):
        super(MayaRigMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add(space.create, 'Add Space(s)')
        self.addSeparator()
        self.add(rig.lockMeshes, 'Lock Mesh(es)')
        self.add(rig.unlockMeshes, 'Unlock Mesh(es)')

class MayaReferenceMenu(MayaPiperMenu):

    def __init__(self, title='Reference', *args, **kwargs):
        super(MayaReferenceMenu, self).__init__(title, *args, **kwargs)
        self.build()

    @staticmethod
    def referenceRig(path):
        """
        Convenience method for referecing a rig to replace control curves if ctrl held, else reference into scene.

        Args:
            path (string): Path to Maya file to reference.

        Returns:
            (pm.nodetypes.FileReference or list): Reference(s) created.
        """
        return control.replaceShapes(path) if modifier.isCtrlHeld() else animation.referenceRig(path)

    def build(self):
        # cannot build menu without art directory
        art_directory = maya_paths.getArtDirectory()
        if not art_directory:
            return

        rigs = pather.getAllFilesEndingWithWord(mcfg.maya_rig_suffixes, art_directory)
        for rig in rigs:
            name = os.path.basename(os.path.abspath(rig + '/../..'))
            rig = maya_paths.getRelativeArt(rig)
            self.add(self.referenceRig, name, rig)


class MayaAnimationMenu(MayaPiperMenu):

    def __init__(self, title='Animation', *args, **kwargs):
        super(MayaAnimationMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add(myclipper.show, 'Clipper')
        self.add(myswitcher.show, 'Space Switcher')
        self.addSeparator()
        self.add(resolution.createHigh, 'Reference High-Poly')
        self.add(resolution.removeHigh, 'Remove High-Poly')
        self.addSeparator()
        self.add(key.toggleStepped, 'Toggle Auto/Stepped Tangents')
        self.add(key.roundAll, 'Round Keyframes')
        self.add(key.deleteDecimals, 'Delete Decimal Keyframes On Curves')
        self.addSeparator()
        self.add(animation.health, 'Health Check')


class MayaGraphicsMenu(MayaPiperMenu):

    def __init__(self, title='Graphics', *args, **kwargs):
        super(MayaGraphicsMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add(graphics.createInitialMaterial)
        self.add(graphics.updateMaterials)


class MayaSettingsMenu(MayaPiperMenu):

    def __init__(self, title='Settings', *args, **kwargs):
        super(MayaSettingsMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add(myprojects.show, 'Projects')
        self.addSeparator()
        self.addCheckbox(maya_store.get(mcfg.use_perforce), self.onUsePerforcePressed, 'Use Perforce')
        self.addCheckbox(maya_store.get(mcfg.use_piper_units), self.onUseUnitsPressed, 'Use Piper Units')
        self.addCheckbox(maya_store.get(mcfg.use_piper_render), self.onUseRenderPressed, 'Use Piper Render')
        self.addCheckbox(maya_store.get(mcfg.export_ascii), self.onExportInAsciiPressed, 'Export In Ascii')
        self.addCheckbox(maya_store.get(mcfg.unload_unwanted), self.onUnloadUnwantedPressed, 'Unload Unwanted Plug-ins')
        self.addCheckbox(maya_store.get(mcfg.open_port), self.onPortPressed, 'Open Port')
        self.add(self.onSetHdrImagePressed, 'Set HDR Image')
        self.addSeparator()
        self.add(settings.hotkeys, 'Assign Hotkeys')

        self.addSeparator()
        self.add(self.uninstall, 'Uninstall Piper')

    def onUsePerforcePressed(self, state):
        """
        Sets whether perforce should be used before saving scene and shows/hides the Perforce menu set

        Args:
            state (boolean): Whether to use perforce or not.
        """
        maya_store.set(mcfg.use_perforce, state)
        self.parent_menu.perforce_menu.menuAction().setVisible(state)

    @staticmethod
    def onUseUnitsPressed(state):
        """
        Changes time range, frame speed, units, and grid size to what's defined in Piper.

        Args:
            state (boolean): If True, will change some Maya defaults on Maya open.
        """
        maya_store.set(mcfg.use_piper_units, state)
        if state:
            settings.loadDefaults()

    @staticmethod
    def onUseRenderPressed(state):
        """
        Sets the viewport's render engine to DirectX11 and the tone map to use the tonemapping set in Maya config.

        Args:
            state (boolean): If True, will switch render engine and tonemapping.
        """
        maya_store.set(mcfg.use_piper_render, state)
        if state:
            settings.loadRender()

    @staticmethod
    def onExportInAsciiPressed(state):
        """
        Sets FBX export method.

        Args:
            state (boolean): If True, FBX will export in ASCII, useful to read what is part of the file. Else FBX
            will export in Binary format. Binary is a smaller, faster file, but harder to debug.
        """
        maya_store.set(mcfg.export_ascii, state)

    @staticmethod
    def onUnloadUnwantedPressed(state):
        """
        Unloads all the unwanted Maya plugins defined in piper's Maya config if given state is True.

        Args:
            state (boolean): If True, unloads unwanted Maya plugins as defined in piper's Maya config
        """
        maya_store.set(mcfg.unload_unwanted, state)
        if state:
            plugin.unloadUnwanted()

    @staticmethod
    def onPortPressed(state):
        """
        Opens/Closes a port based on the given state. Useful for commands that may come from another DCC.

        Args:
            state (boolean): If True, will open port, else will close it.
        """
        maya_store.set(mcfg.open_port, state)
        settings.openPort() if state else settings.closePort()

    def onSetHdrImagePressed(self):
        """
        Opens a file dialog for user to pick HDR image to use as the default image for shader backgrounds
        """
        dialog = QtWidgets.QFileDialog()
        starting_directory = maya_paths.getArtDirectory()
        file_path = dialog.getOpenFileName(self, 'Choose HDR Image', starting_directory)

        if not file_path:
            return

        maya_store.set(mcfg.hdr_image_path, file_path[0])

    @staticmethod
    def uninstall():
        """
        Removes the module file from the user's Documents/Maya directory. Must restart Maya for effect to take place.
        """
        pm.warning('Uninstall currently not implemented')


def create():
    """
    Creates the menu set for Piper and adds it to maya's main Menu Bar.
    """
    piper_menu = getPiperMainMenu()
    piper_menu.on_before_reload = settings.removeCallbacks
    piper_menu.scene_menu = MayaSceneMenu()
    piper_menu.perforce_menu = MayaPerforceMenu()
    piper_menu.nodes_menu = MayaNodesMenu()
    piper_menu.export_menu = MayaExportMenu()
    piper_menu.curves_menu = MayaCurvesMenu()
    piper_menu.bones_menu = MayaBonesMenu()
    piper_menu.rig_menu = MayaRigMenu()
    piper_menu.animation_menu = MayaAnimationMenu()
    piper_menu.reference_menu = MayaReferenceMenu()
    piper_menu.graphics_menu = MayaGraphicsMenu()
    piper_menu.settings_menu = MayaSettingsMenu()
    piper_menu.build()

    main_menu = mywidget.getMainMenuBar()
    main_menu.addMenu(piper_menu)
