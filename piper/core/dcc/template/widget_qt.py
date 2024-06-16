#  Copyright (c) Christian Corsica. All Rights Reserved.

from Qt import QtWidgets

import piper.config as pcfg
from piper.core.store import piper_store
from piper.core.dcc.template.widget import WidgetDCC


class WidgetQTDCC(WidgetDCC):

    def setArtDirectory(self, parent, project=None):
        """
        Opens up a dialog window for the user to select the art directory they would like the current project to have.

        Args:
            parent (QtWidget): Widget to parent dialog window to.

            project (string): Name of project to set art directory in.

        Returns:
            (string): Path to directory user has selected.
        """
        if not project:
            project = self.dcc_paths.getCurrentProject()

        if not project:
            self.dcc_paths.warn('Please create a project before setting the art directory!')
            return

        dialog = QtWidgets.QFileDialog(parent)
        projects = piper_store.get(pcfg.projects)
        starting_directory = projects[project][pcfg.art_directory] if projects else ''
        directory = dialog.getExistingDirectory(parent, 'Choose directory to export from', starting_directory)

        if not directory:
            return

        projects[project][pcfg.art_directory] = directory
        piper_store.set(pcfg.projects, projects)
        return directory

    def setGameDirectory(self, parent, project=None):
        """
        Opens up a dialog window for the user to select the game directory they would like the current project to have.

        Args:
            parent (QtWidget): Widget to parent dialog window to.

            project (string): Name of project to set game directory in.

        Returns:
            (string): Path to directory user has selected.
        """
        if not project:
            project = self.dcc_paths.getCurrentProject()

        if not project:
            self.dcc_paths.warn('Please create a project before setting the game directory!')
            return

        dialog = QtWidgets.QFileDialog(parent)
        projects = piper_store.get(pcfg.projects)
        starting_directory = projects[project][pcfg.game_directory] if projects else ''
        directory = dialog.getExistingDirectory(parent, 'Choose directory to export to', starting_directory)

        if not directory:
            return

        projects[project][pcfg.game_directory] = directory
        piper_store.set(pcfg.projects, projects)
        return directory


dcc_widget = WidgetQTDCC()
