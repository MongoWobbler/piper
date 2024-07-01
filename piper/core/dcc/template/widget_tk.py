#  Copyright (c) Christian Corsica. All Rights Reserved.

import piper.config as pcfg
import piper.core.pather as pather
from piper.core.events import dispatcher
from piper.core.store import piper_store
from piper.core.dcc.template.widget import WidgetDCC


class WidgetTKDCC(WidgetDCC):

    def setArtDirectory(self, project=None):
        """
        Sets the art source directory in the global piper settings

        Args:
            (string): Name of project to set art directory to.

        Returns:
            (string): Art directory that was set.
        """
        if not project:
            project = self.dcc_paths.getCurrentProject()

        if not project:
            raise NameError('Please create a project before setting the art directory!')

        projects = piper_store.get(pcfg.projects)
        starting_directory = projects[project][pcfg.art_directory]
        directory = pather.getDirectoryDialog(starting_directory, 'Choose directory to export from', error=False)

        if not directory:
            return

        dispatcher.call(pcfg.before_art_directory_change_event)
        projects[project][pcfg.art_directory] = directory
        piper_store.set(pcfg.projects, projects)
        dispatcher.call(pcfg.after_art_directory_change_event)
        return directory

    def setGameDirectory(self, project=None):
        """
        Sets the game export directory in the global piper settings

        Args:
            (string): Name of project to set game directory to.

        Returns:
            (string): Game directory that was set.
        """
        if not project:
            project = self.dcc_paths.getCurrentProject()

        if not project:
            raise NameError('Please create a project before setting the art directory!')

        projects = piper_store.get(pcfg.projects)
        starting_directory = projects[project][pcfg.game_directory]
        directory = pather.getDirectoryDialog(starting_directory, 'Choose directory to export to', error=False)

        if not directory:
            return

        projects[project][pcfg.game_directory] = directory
        piper_store.set(pcfg.projects, projects)
        return directory


dcc_widget = WidgetTKDCC()
