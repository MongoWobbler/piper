#  Copyright (c) Christian Corsica. All Rights Reserved.

import os

import piper.config as pcfg
import piper.core.filer as filer
from piper.core.store import piper_store


class FileType:
    """
    Defines the export types that are allowed in piper. This is essentially just an enum with inheritance.
    """
    none = pcfg.none_type
    static_mesh = pcfg.static_mesh_type
    skeletal_mesh = pcfg.skeletal_mesh_type
    rig = pcfg.rig_type
    animation = pcfg.animation_type

    @staticmethod
    def isMesh(directory):
        """
        Determines what is a mesh file type.

        Args:
            directory (string): Used to determine if it is a mesh file type

        Returns:
            (boolean): True is given directory proves that the File Type should be of mesh.
        """
        raise NotImplementedError

    @staticmethod
    def isSkeletal(file_name):
        """
        Determines what is a Skeletal Mesh file type.

        Args:
            file_name (string): Used to determine if it is a mesh file type.

        Returns:
            (boolean): True is given file_name proves that the File Type should be of skeletal mesh.
        """
        raise NotImplementedError

    @staticmethod
    def isRig(file_name):
        """
        Determines what is a Rig file type.

        Args:
            file_name (string): Used to determine if it is a Rig file type.

        Returns:
            (boolean): True is given file_name proves that the File Type should be of type Rig.
        """
        raise NotImplementedError

    @staticmethod
    def isAnimation(directory):
        """
        Determines what is an animation file type.

        Args:
            directory (string): Used to determine if it is a animation file type

        Returns:
            (boolean): True is given directory proves that the File Type should be of animation.
        """
        raise NotImplementedError


class PathDCC(object):
    """
    Used partly as template of common functionality across different DCCs, along with common functions that can be
    deduced with this common functionality.
    """

    @property
    def is_exportable(self):
        """
        Dictionary of each file type as key, and bool of whether the file type is exportable or not as value.
        """
        raise NotImplementedError

    def display(self, text):
        """
        Way of DCC of displaying text in a friendly, visible manner.

        Args:
            text (string): Text to display.
        """
        raise NotImplementedError

    def warn(self, text):
        """
        Way of DCC to warn user of with message.

        Args:
            text (string): Text to warn user with.
        """
        raise NotImplementedError

    def getCurrentScene(self):
        """
        Meant to be overridden by DCC that can get the full path to the currently opened scene in the DCC.

        Returns:
            (string): Full path to the current scene.
        """
        raise NotImplementedError

    def getCurrentProject(self):
        """
        Uses the DCC store to get the current project selected.

        Returns:
            (string): Name of current project selected.
        """
        raise NotImplementedError

    def setCurrentProject(self, project=None, force=False):
        """
        Sets the given project on the DCC store.

        Args:
            project (string): If given, will set the current project to the given project.

            force (boolean): If True, will force to set the project to None if None is given.

        Returns:
            (boolean): True if project was set, False if it was not set.
        """
        raise NotImplementedError

    def open(self, path):
        """
        Opens the given path in the DCC.

        Args:
            path (string): Full path to file to open in dcc.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def validateDirectory(self, directory_key, directory_name, project=None, error=False):
        """
        Runs a validation check to make sure projects exist in piper store and there is a current project set if no
        project is given. If given error is True, raises error, else return None.

        Args:
            directory_key (string): Key to look up directory in projects dictionary.

            directory_name (string): Name of directory type we're searching for to use in error message if raised.

            project (string): Name of project to check and make sure is part of projects

            error (boolean): If True, will raise error if validation fails. Else will return None.

        Returns:
            (string or None): Full path to directory found with directory key.
        """
        projects = piper_store.get(pcfg.projects)
        if not projects:
            if error:
                raise KeyError('No projects have been made. Please make a project using Piper->Settings->Projects')
            else:
                return None

        if not project:
            project = self.getCurrentProject()

        if not project:
            if error:
                raise KeyError('No project is currently set! Please set a project.')
            else:
                return None

        if project not in projects:
            if error:
                raise KeyError(f'{project} project is not part of the piper projects! Something has gone wrong.')
            else:
                return None

        directory = projects[project][directory_key]
        if directory:
            return directory  # woo! validation successful
        elif error:
            raise KeyError(f'{directory_name} directory is not currently set on the {project} project. '
                           f'Please set the {directory_name} directory')

        return None

    def getArtDirectory(self, project=None, error=False):
        """
        Gets the art/source directory set to be used for the current project.

        Args:
            project (string): If given, will use project to search art directory of, else will use current project.

            error (boolean): If True, will raise error if no projects found, no project set, or art directory is not set

        Returns:
            (string or None): Full path to art directory.
        """
        return self.validateDirectory(pcfg.art_directory, 'Art', project=project, error=error)

    def getGameDirectory(self, project=None, error=False):
        """
        Gets the game/export directory set to be used for the current project.

        Args:
            project (string): If given, will use project to search game directory of, else will use current project.

            error (boolean): If True, will raise error if no projects found, no project set, or no game directory set.

        Returns:
            (string or None): Full path to game directory.
        """
        return self.validateDirectory(pcfg.game_directory, 'Game', project=project, error=error)

    def getRelativeArt(self, path='', name=''):
        """
        Gets the relative art path of given path. If path not given will use current scene path.

        Args:
            path (string): Path to get relative art directory of.

            name (string): If given, will change the name of the file to the given name.

        Returns:
            (string): Path relative to art directory set through settings.
        """
        if not path:
            path = self.getCurrentScene()

        if not path:
            raise ValueError('Scene is not saved! ')

        path = path.replace('\\', '/')
        art_directory = self.getArtDirectory()
        if not path.startswith(art_directory):
            raise ValueError(path + ' is not in the art directory: ' + art_directory)

        if name:
            directory = os.path.dirname(path)
            old_name, extension = os.path.splitext(os.path.basename(path))
            path = os.path.join(directory, name + extension)

        relative_art = os.path.relpath(path, art_directory)
        return relative_art.replace('\\', '/')

    def getSelfExport(self, name='', error=True):
        """
        Gets the current scene's directory if scene is saved, else uses the art directory.

        Args:
            name (string): Name of file to return.

            error (bool): If True and art directory is not found, will raise error. Else will return None.

        Returns:
            (string): Full path with given name.
        """
        scene_path = self.getCurrentScene()
        if scene_path:
            export_directory = os.path.dirname(scene_path)
        else:
            art_directory = self.getArtDirectory(error=error)

            # validate art directory exists
            if not art_directory:
                return None

            export_directory = art_directory

        export_path = os.path.join(export_directory, name).replace('\\', '/')
        return export_path

    def getGameExport(self, name='', error=True):
        """
        Gets the game path for the given scene. If no scene open, will use game root directory.

        Args:
            name (string): Name of file to return.

            error (bool): If True and game directory is not found, will raise error. Else will return None.

        Returns:
            (string): Full path with given name.
        """
        scene_path = self.getCurrentScene()
        game_directory = self.getGameDirectory(error=error)
        relative_directory = ''

        # validate game directory exists
        if not game_directory:
            return None

        if scene_path:
            source_directory = os.path.dirname(scene_path)
            art_directory = self.getArtDirectory()

            # gets the relative path using the art directory
            if scene_path.startswith(art_directory):
                relative_directory = os.path.relpath(source_directory, art_directory)
            else:
                self.warn(scene_path + ' is not in art directory! Returning game directory root.')

        export_path = os.path.join(game_directory, relative_directory, name).replace('\\', '/')
        return export_path

    def getGameTextureExport(self, texture):
        """
        Gets the path to export the given texture to.

        Args:
            texture (string): Full art directory path of texture file.

        Returns:
            (string): Full game directory path of where given texture would export to.
        """
        relative_directory = ''
        art_directory = self.getArtDirectory()
        game_directory = self.getGameDirectory()

        if texture.startswith(art_directory):
            relative_directory = os.path.relpath(texture, art_directory)
        else:
            self.warn(texture + ' is not in art directory! Returning game directory root.')

        export_path = os.path.join(game_directory, relative_directory).replace('\\', '/')
        export_path = export_path.replace(pcfg.art_textures_directory_name,
                                          pcfg.game_textures_directory_name)
        return export_path

    def openSceneInOS(self):
        """
        Opens the current scene in an OS window.
        """
        current_scene = self.getCurrentScene()

        if not current_scene:
            self.warn('Scene is not saved!')
            return

        filer.openWithOS(os.path.dirname(current_scene))

    def copyCurrentSceneToClipboard(self):
        """
        Copies the current scene to the clipboard.
        """
        current_scene = self.getCurrentScene()

        if not current_scene:
            self.warn('Scene is not saved!')
            return

        filer.copyToClipboard(current_scene)

    def openArtDirectoryInOS(self, project=None):
        """
        Opens the art directory in OS window.

        Args:
            project (string): Name of project to open art directory of in OS window.
        """
        art_directory = self.getArtDirectory(project=project, error=True)
        filer.openWithOS(art_directory)

    def openGameDirectoryInOS(self, project=None):
        """
        Opens the game directory in OS window.

        Args:
            project (string): Name of project to open game directory of in OS window.
        """
        game_directory = self.getGameDirectory(project=project, error=True)
        filer.openWithOS(game_directory)


dcc_paths = PathDCC()
