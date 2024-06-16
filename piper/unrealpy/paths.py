#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue

import piper.config.unreal as ucfg
from piper.core.dcc.template.paths import PathDCC
from piper.unrealpy.store import unreal_store


class UnrealPaths(PathDCC):

    def display(self, text):
        """
        Way of Unreal of displaying text in a friendly, visible manner.

        Args:
            text (string): Text to display.
        """
        ue.log(text)

    def warn(self, text):
        """
        Way of Unreal to warn user of with message.

        Args:
            text (string): Text to warn user with.
        """
        ue.log_warning(text)

    def getCurrentScene(self):
        """
        Gets the full package name of the open level.
        """
        current_level = ue.get_editor_subsystem(ue.LevelEditorSubsystem).get_current_level()
        return ue.SystemLibrary.get_path_name(current_level).split(".")[0]

    def getCurrentProject(self):
        """
        Uses unreal store to get the current project selected.

        Returns:
            (string): Name of current project selected.
        """
        return unreal_store.get(ucfg.current_project)

    def setCurrentProject(self, project=None, force=False):
        """
        Sets the given project on the Unreal store.

        Args:
            project (string): If given, will set the current project to the given project.

            force (boolean): If True, will force to set the project to None if None is given.

        Returns:
            (boolean): True if project was set, False if it was not set.
        """
        if project or force:
            unreal_store.set(ucfg.current_project, project)
            return True

        return False


unreal_paths = UnrealPaths()


def get():
    """
    Convenience method for getting the unreal_paths. Useful in menu creation.

    Returns:
        (UnrealPaths): PathDCC class for Unreal.
    """
    return unreal_paths
