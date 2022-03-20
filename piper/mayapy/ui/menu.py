#  Copyright (c) Christian Corsica. All Rights Reserved.

import os

from Qt import QtWidgets

import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.util as myu
import piper.mayapy.rig as rig
import piper.mayapy.rig.bone as bone
import piper.mayapy.rig.skin as skin
import piper.mayapy.rig.xform as xform
import piper.mayapy.rig.curve as curve
import piper.mayapy.rig.space as space
import piper.mayapy.rig.control as control
import piper.mayapy.graphics as graphics
import piper.mayapy.settings as settings
import piper.mayapy.ui.clipper as myclipper
import piper.mayapy.ui.switcher as myswitcher
import piper.mayapy.ui.vert_selector as myvert_selector
import piper.mayapy.ui.widget as mywidget
import piper.mayapy.ui.window as mywindow
import piper.mayapy.pipe.export as export
import piper.mayapy.pipe.paths as paths
import piper.mayapy.pipernode as pipernode
import piper.mayapy.attribute as attribute
import piper.mayapy.animation as animation
import piper.mayapy.animation.key as key
import piper.mayapy.animation.resolution as resolution

from piper.mayapy.pipe.store import store
from piper.ui.menu import PiperMenu, PiperSceneMenu, PiperExportMenu, getPiperMainMenu


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

    def openSceneInOS(self):
        """
        Opens the current scene in a OS window.
        """
        pcu.openWithOS(os.path.dirname(pm.sceneName()))

    def openArtDirectoryInOS(self):
        """
        Opens the art directory in a OS window.
        """
        pcu.openWithOS(store.get(pcfg.art_directory))

    def openGameDirectoryInOS(self):
        """
        Opens the game directory in a OS window.
        """
        pcu.openWithOS(store.get(pcfg.game_directory))

    def copyCurrentSceneToClipboard(self):
        """
        Copies the current scene to the clipboard.
        """
        scene_path = pm.sceneName()

        if not scene_path:
            pm.error('Scene is not saved!')

        pcu.copyToClipboard(scene_path)

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


class MayaExportMenu(PiperExportMenu):

    def exportToGame(self):
        export.piperNodesToGameAsFBX()

    def exportToCurrentDirectory(self):
        export.piperNodesToSelfAsFBX()

    def exportMeshesToCurrentAsObj(self):
        export.piperMeshToSelfAsOBJ()

    def setArtDirectory(self):
        dialog = QtWidgets.QFileDialog()
        starting_directory = pm.workspace(q=True, dir=True)
        directory = dialog.getExistingDirectory(self, 'Choose directory to export from', starting_directory)

        if not directory:
            return

        settings.setProject(directory)
        store.set(pcfg.art_directory, directory)

    def setGameDirectory(self):
        dialog = QtWidgets.QFileDialog()
        starting_directory = store.get(pcfg.game_directory)
        directory = dialog.getExistingDirectory(self, 'Choose directory to export to', starting_directory)

        if not directory:
            return

        store.set(pcfg.game_directory, directory)


class MayaCurvesMenu(MayaPiperMenu):

    def __init__(self, title='Curves', *args, **kwargs):
        super(MayaCurvesMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        [self.add(pcu.toSentenceCase(curve_method.__name__), curve_method) for curve_method in curve.methods]
        self.addSeparator()
        self.add('Create Curve(s) From Cross Section', curve.crossSection)
        self.add('Create Cross Section Curve at Origin', curve.originCrossSection)
        self.addSeparator()
        self.add('Layout All Curves', curve.layoutAll)
        self.add('Layout All Colors', curve.layoutColors)


class MayaNodesMenu(MayaPiperMenu):

    def __init__(self, title='Nodes', *args, **kwargs):
        super(MayaNodesMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add('Create Mesh', pipernode.createMesh)
        self.add('Create Skinned Mesh', pipernode.createSkinnedMesh)
        self.add('Create Animation', pipernode.createAnimation)


class MayaBonesMenu(MayaPiperMenu):

    def __init__(self, title='Bones', *args, **kwargs):
        super(MayaBonesMenu, self).__init__(title, *args, **kwargs)
        self.binder = skin.Binder()
        self.build()

    def build(self):
        self.add('Create at Pivot', bone.createAtPivot)
        self.add('Parent', xform.parent)
        self.add('Mirror Translate', xform.mirrorTranslate)
        self.add('Mirror Rotate', xform.mirrorRotate)
        self.add('Assign Labels', bone.assignLabels)
        self.add('Assign Bind Attributes', bone.assignBindAttributes)
        self.add('Add Delete Attribute', attribute.addDelete)
        self.add('Turn Off Segment Scale Compensate', bone.setSegmentScaleCompensateOff)
        self.add('Return to Bind Pose', skin.returnToBindPose)
        self.addSeparator()
        self.add('Select Fractionally Weighted Verts', skin.selectWeightedVerts)
        self.add('Select Weighted Verts', myvert_selector.show)
        self.addSeparator()
        self.add('Unbind', self.binder.unbind)
        self.add('Rebind', self.binder.rebind)
        self.addSeparator()
        self.add('Health Check', bone.health)


class MayaRigMenu(MayaPiperMenu):

    def __init__(self, title='Rig', *args, **kwargs):
        super(MayaRigMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add('Add Space(s)', space.create)
        self.addSeparator()
        self.add('Lock Mesh(es)', rig.lockMeshes)
        self.add('Unlock Mesh(es)', rig.unlockMeshes)

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
        return control.replaceShapes(path) if myu.isCtrlHeld() else animation.referenceRig(path)

    def build(self):
        # cannot build menu without art directory
        art_directory = store.get(pcfg.art_directory)
        if not art_directory:
            return

        rigs = pcu.getAllFilesEndingWithWord(pcfg.maya_rig_suffixes, art_directory)
        for rig in rigs:
            name = os.path.basename(os.path.abspath(rig + '/../..'))
            rig = paths.getRelativeArt(rig)
            self.add(name, self.referenceRig, rig)


class MayaAnimationMenu(MayaPiperMenu):

    def __init__(self, title='Animation', *args, **kwargs):
        super(MayaAnimationMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add('Clipper', myclipper.show)
        self.add('Space Switcher', myswitcher.show)
        self.addSeparator()
        self.add('Reference High-Poly', resolution.createHigh)
        self.add('Remove High-Poly', resolution.removeHigh)
        self.addSeparator()
        self.add('Toggle Auto/Stepped Tangents', key.toggleStepped)
        self.add('Round Keyframes', key.roundAll)
        self.add('Delete Decimal Keyframes On Curves', key.deleteDecimals)
        self.addSeparator()
        self.add('Health Check', animation.health)


class MayaGraphicsMenu(MayaPiperMenu):

    def __init__(self, title='Graphics', *args, **kwargs):
        super(MayaGraphicsMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.add('Create Initial Material', graphics.createInitialMaterial)
        self.add('Update Materials', graphics.updateMaterials)


class MayaSettingsMenu(MayaPiperMenu):

    def __init__(self, title='Settings', *args, **kwargs):
        super(MayaSettingsMenu, self).__init__(title, *args, **kwargs)
        self.build()

    def build(self):
        self.addCheckbox('Use Piper Units', store.get(pcfg.use_piper_units), self.onUseUnitsPressed)
        self.addCheckbox('Use Piper Render', store.get(pcfg.use_piper_render), self.onUseRenderPressed)
        self.addCheckbox('Export In Ascii', store.get(pcfg.export_ascii), self.onExportInAsciiPressed)
        self.addCheckbox('Unload Unwanted Plug-ins', store.get(pcfg.unload_unwanted), self.onUnloadUnwantedPressed)
        self.add('Set HDR Image', self.onSetHdrImagePressed)
        self.addSeparator()
        self.add('Assign Hotkeys', settings.hotkeys)

        self.addSeparator()
        self.add('Uninstall Piper', self.uninstall)

    @staticmethod
    def onUseUnitsPressed(state):
        store.set(pcfg.use_piper_units, state)

    @staticmethod
    def onUseRenderPressed(state):
        store.set(pcfg.use_piper_render, state)

    @staticmethod
    def onExportInAsciiPressed(state):
        store.set(pcfg.export_ascii, state)

    @staticmethod
    def onUnloadUnwantedPressed(state):
        store.set(pcfg.unload_unwanted, state)

    def onSetHdrImagePressed(self):
        dialog = QtWidgets.QFileDialog()
        starting_directory = store.get(pcfg.art_directory)
        file_path = dialog.getOpenFileName(self, 'Choose HDR Image', starting_directory)

        if not file_path:
            return

        store.set(pcfg.hdr_image_path, file_path[0])

    @staticmethod
    def uninstall():
        pm.warning('Uninstall currently not implemented')


def create():
    """
    Creates the menu set for Piper and adds it to maya's main Menu Bar.
    """
    piper_menu = getPiperMainMenu()
    piper_menu.on_before_reload = settings.removeCallbacks
    piper_menu.scene_menu = MayaSceneMenu()
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
