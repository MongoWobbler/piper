#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import pymel.core as pm

import piper.config.maya as mcfg
from piper.core.dcc.template.paths import FileType, PathDCC
from piper.mayapy.pipe.store import maya_store


class MayaFileType(FileType):
    """
    Defines the export types that are allowed in Maya's piper.
    """

    @staticmethod
    def isMesh(directory):
        """
        Determines what is a mesh file type.

        Args:
            directory (string): Used to determine if it is a mesh file type

        Returns:
            (boolean): True is given directory proves that the File Type should be of mesh.
        """
        return os.path.basename(directory) == mcfg.meshes_directory

    @staticmethod
    def isSkeletal(file_name):
        """
        Determines what is a Skeletal Mesh file type.

        Args:
            file_name (string): Used to determine if it is a mesh file type.

        Returns:
            (boolean): True is given file_name proves that the File Type should be of skeletal mesh.
        """
        return file_name.startswith(mcfg.skinned_mesh_prefix)

    @staticmethod
    def isRig(file_name):
        """
        Determines what is a Rig file type.

        Args:
            file_name (string): Used to determine if it is a Rig file type.

        Returns:
            (boolean): True is given file_name proves that the File Type should be of type Rig.
        """
        return os.path.splitext(file_name)[0] == mcfg.rig_name

    @staticmethod
    def isAnimation(directory):
        """
        Determines what is an animation file type.

        Args:
            directory (string): Used to determine if it is a animation file type

        Returns:
            (boolean): True is given directory proves that the File Type should be of animation.
        """
        return os.path.basename(directory) == mcfg.animation_directory


class MayaPaths(PathDCC):

    @property
    def is_exportable(self):
        """
        Dictionary of each file type as key, and bool of whether the file type is exportable or not as value.
        """
        return {FileType.none: False,
                FileType.static_mesh: True,
                FileType.skeletal_mesh: True,
                FileType.rig: False,
                FileType.animation: True}

    def display(self, text):
        """
        Way of DCC of displaying text in a friendly, visible manner.

        Args:
            text (string): Text to display.
        """
        pm.displayInfo(text)

    def warn(self, text):
        """
        Way of DCC to warn user of with message.

        Args:
            text (string): Text to warn user with.
        """
        pm.warning(text)

    def getCurrentScene(self):
        """
        Meant to be overridden by DCC that can get the full path to the currently opened scene in the DCC.

        Returns:
            (string): Full path to the current scene.
        """
        return pm.sceneName()

    def getCurrentProject(self):
        """
        Uses the DCC store to get the current project selected.

        Returns:
            (string): Name of current project selected.
        """
        return maya_store.get(mcfg.current_project)

    def setCurrentProject(self, project=None, force=False):
        """
        Sets the given project on the Maya store.

        Args:
            project (string): If given, will set the current project to the given project.

            force (boolean): If True, will force to set the project to None if None is given.

        Returns:
            (boolean): True if project was set, False if it was not set.
        """
        if project or force:
            maya_store.set(mcfg.current_project, project)
            return True

        return False

    def open(self, path):
        """
        Opens the given path in Maya.

        Args:
            path (string): Full path to file to open in Maya.
        """
        pm.openFile(path, force=True)

    @staticmethod
    def getFileType(directory, file_name):
        """
        Gets what kind of file type the given directory and given file_name is.

        Args:
            directory (string): Directory the given file_name is located in.

            file_name (string): The name of the file (not including its directory).

        Returns:
            (FileType): The file type that the given file is based on its directory and file name.
        """
        if MayaFileType.isSkeletal(file_name):
            return FileType.skeletal_mesh

        elif MayaFileType.isRig(file_name):
            return FileType.rig

        elif MayaFileType.isMesh(directory):
            return FileType.static_mesh

        elif MayaFileType.isAnimation(directory):
            return FileType.animation

        return FileType.none


maya_paths = MayaPaths()
