#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm

import piper_config as pcfg
import piper.core.util as pcu
import piper.mayapy.rig.bone as bone
import piper.mayapy.rig.skin as skin
import piper.mayapy.rig.xform as xform
import piper.mayapy.rig.curve as curve
import piper.mayapy.graphics as graphics
import piper.mayapy.settings as settings
import piper.mayapy.ui.util as myui
import piper.mayapy.ui.window as mywindow
import piper.mayapy.pipe.export as export
import piper.mayapy.pipernode as pipernode
import piper.mayapy.attribute as attribute

from PySide2 import QtWidgets
from piper.mayapy.pipe.store import store
from piper.ui.menu import PiperMenu, PiperSceneMenu, PiperExportMenu, getPiperMainMenu


class MayaPiperMenu(PiperMenu):
    """
    Implements undo chunks so that a whole piper function call is undone instead of only parts of it at a time.
    """
    def onBeforePressed(self):
        pm.undoInfo(openChunk=True)

    def onAfterPressed(self):
        pm.undoInfo(closeChunk=True)


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


class MayaNodesMenu(MayaPiperMenu):

    def __init__(self, title='Nodes', parent=None):
        super(MayaNodesMenu, self).__init__(title, parent=parent)
        self.build()

    def build(self):
        self.add('Create Mesh', pipernode.createMesh)
        self.add('Create Skinned Mesh', pipernode.createSkinnedMesh)


class MayaBonesMenu(MayaPiperMenu):

    def __init__(self, title='Bones', parent=None):
        super(MayaBonesMenu, self).__init__(title, parent=parent)
        self.binder = skin.Binder()
        self.build()

    def build(self):
        self.add('Create at Pivot', bone.createAtPivot)
        self.add('Parent', xform.parent)
        self.add('Mirror Translate', xform.mirrorTranslate)
        self.add('Mirror Rotate', xform.mirrorRotate)
        self.add('Assign Labels', bone.assignLabels)
        self.add('Add Delete Attribute', attribute.addDelete)
        self.addSeparator()
        self.add('Unbind', self.binder.unbind)
        self.add('Rebind', self.binder.rebind)
        self.addSeparator()
        self.add('Health Check', bone.health)


class MayaGraphicsMenu(MayaPiperMenu):

    def __init__(self, title='Graphics', parent=None):
        super(MayaGraphicsMenu, self).__init__(title, parent=parent)
        self.build()

    def build(self):
        self.add('Create Initial Material', graphics.createInitialMaterial)
        self.add('Update Materials', graphics.updateMaterials)


class MayaCurvesMenu(MayaPiperMenu):

    def __init__(self, title='Curves', parent=None):
        super(MayaCurvesMenu, self).__init__(title, parent=parent)
        self.build()

    def build(self):
        [self.add(pcu.toSentenceCase(curve_method.__name__), curve_method) for curve_method in curve.methods]
        self.addSeparator()
        self.add('Create Curve(s) From Cross Section', curve.crossSection)
        self.add('Create Cross Section Curve at Origin', curve.originCrossSection)
        self.addSeparator()
        self.add('Layout All Curves', curve.layoutAll)


class MayaSettingsMenu(MayaPiperMenu):

    def __init__(self, title='Settings', parent=None):
        super(MayaSettingsMenu, self).__init__(title, parent=parent)
        self.build()

    def build(self):
        self.addCheckbox('Use Piper Units', store.get(pcfg.use_piper_units), self.onUseUnitsPressed)
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
    piper_menu.scene_menu = MayaSceneMenu()
    piper_menu.nodes_menu = MayaNodesMenu()
    piper_menu.export_menu = MayaExportMenu()
    piper_menu.curves_menu = MayaCurvesMenu()
    piper_menu.bones_menu = MayaBonesMenu()
    piper_menu.graphics_menu = MayaGraphicsMenu()
    piper_menu.settings_menu = MayaSettingsMenu()
    piper_menu.build()

    main_menu = myui.getMainMenuBar()
    main_menu.addMenu(piper_menu)
