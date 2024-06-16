#  Copyright (c) Christian Corsica. All Rights Reserved.

from Qt import QtWidgets, QtCore, QtGui

import piper.core
import piper.config as pcfg
import piper.ui.widget as widget
from piper.core.store import piper_store
from piper.core.dcc.template.paths import dcc_paths
from piper.core.dcc.template.widget_qt import dcc_widget
from piper.core.dcc.template.export import dcc_export


class DirectoryLine(QtWidgets.QWidget):
    """
    Widget that holds the animation clip information.
    """
    def __init__(self, icon_name, set_pressed, export_pressed, *args, **kwargs):
        super(DirectoryLine, self).__init__(*args, **kwargs)
        self.icon_name = icon_name
        self.set_pressed = set_pressed
        self.export_pressed = export_pressed

        self.set_button = None
        self.export_button = None
        self.text_line = None

        self.dcc_paths = dcc_paths
        self.dcc_widget = dcc_widget
        self.dcc_export = dcc_export

        self.build()

    def build(self):
        icons_directory = piper.core.getIconsDirectory()
        layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(layout)

        # line edit
        self.text_line = QtWidgets.QTextEdit()
        self.text_line.setReadOnly(True)
        self.text_line.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
        layout.addWidget(self.text_line)

        # set button
        self.set_button = QtWidgets.QToolButton()
        self.set_button.setToolTip(self.set_pressed.__doc__)
        self.set_button.setStatusTip(self.set_pressed.__doc__)
        set_icon = QtGui.QIcon(f'{icons_directory}/{self.icon_name}.png')
        self.set_button.setIcon(set_icon)
        self.set_button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Ignored)
        self.set_button.clicked.connect(self.set_pressed)
        layout.addWidget(self.set_button)

        # export button
        self.export_button = QtWidgets.QToolButton()
        self.export_button.setToolTip(self.export_pressed.__doc__)
        self.export_button.setStatusTip(self.export_pressed.__doc__)
        export_icon = QtGui.QIcon(icons_directory + '/piper_export.png')
        self.export_button.setIcon(export_icon)
        self.export_button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Ignored)
        self.export_button.clicked.connect(self.export_pressed)
        layout.addWidget(self.export_button)

    def updateLine(self, text, full_text_method, color):
        """
        Updates the text line with the given colored text. If no text is given, will set text line to empty string.

        Args:
            text (string): Text to update text line with.

            full_text_method (Callable): Method which gets the full text to update line with.

            color (string): Name or hex code of color to set colored text to.
        """
        if not text:
            self.text_line.setText('')
            return

        export_path = full_text_method()
        split_text = export_path.split(text)

        # if the split was successful (len > 1), that means the export path is part of the directory and all is good!
        if len(split_text) > 1:
            text_length = len(text)
            colored = widget.colorTextEnd(export_path[:text_length], export_path[text_length:], color=color)
            self.text_line.setText(colored)
            return

        colored = widget.colorTextStart(export_path)
        self.text_line.setText(colored)


class Projects(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(Projects, self).__init__(*args, **kwargs)
        self.setWindowTitle('Projects')

        self.project_box = None
        self.art_line = None
        self.game_line = None
        self.export_color = '#69CFCC'  # cyan type of color

        self.dcc_paths = dcc_paths
        self.dcc_export = dcc_export
        self.dcc_widget = dcc_widget

        self.last_successfully_set_project = None
        self.is_blocking_combobox_callback = False
        self.build()

    def build(self):
        # layouts
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(10, 0, 10, 0)  # makes combo box look OK, otherwise it becomes a fat choch
        projects_layout = QtWidgets.QVBoxLayout()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # art line
        self.art_line = DirectoryLine('piper_art', self.onSetArtPressed, self.dcc_export.exportToCurrentDirectory)
        art_placeholder = 'Use the palette icon button to the right to set the art source path.'
        self.art_line.text_line.setPlaceholderText(art_placeholder)

        # game line
        self.game_line = DirectoryLine('piper_game', self.onSetGamePressed, self.dcc_export.exportToGame)
        game_placeholder = 'Use the gamepad icon button to the right to set the game export path.'
        self.game_line.text_line.setPlaceholderText(game_placeholder)

        # projects combo box
        self.project_box = QtWidgets.QComboBox()
        self.project_box.addItems(['', pcfg.create_project, pcfg.delete_project])
        projects = piper_store.get(pcfg.projects)
        if projects:
            self.project_box.insertItems(0, projects)
            current_project = self.dcc_paths.getCurrentProject()
            self.setProject(current_project)
            index = self.project_box.findText(current_project, QtCore.Qt.MatchFixedString)
            self.project_box.setCurrentIndex(index)

        self.project_box.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
        self.project_box.currentTextChanged.connect(self.onProjectBoxChanged)

        # have to do this fun workaround just to get a widget behaving ok with splitter
        projects_widget = QtWidgets.QWidget()
        projects_widget.setLayout(projects_layout)
        projects_layout.addWidget(self.project_box)
        splitter.addWidget(projects_widget)
        splitter.addWidget(self.art_line)
        splitter.addWidget(self.game_line)
        main_layout.addWidget(splitter)

    def onProjectBoxChanged(self, text):
        """
        Called when project combo box has changed. Handles creating, deleting and setting projects.

        Args:
            text (string): Name of text that was selected.
        """
        if self.is_blocking_combobox_callback:
            return

        if text == pcfg.create_project:
            if not self.onCreateProjectPressed():
                self.resetProject()

        elif text == pcfg.delete_project:
            if not self.onDeleteProjectPressed():
                self.resetProject()

        else:
            self.setProject(text)

    def resetProject(self):
        """
        Resets the project back to the previously successfully set project.
        """
        index = self.project_box.findText(self.last_successfully_set_project, QtCore.Qt.MatchFixedString)
        if index < 0:
            self.dcc_paths.warn(f'Could not find {self.last_successfully_set_project} project! Something went wrong.')
            return

        self.is_blocking_combobox_callback = True
        self.project_box.setCurrentIndex(index)
        self.is_blocking_combobox_callback = False

    def onCreateProjectPressed(self):
        """
        Creates a new project.

        Returns:
            (boolean): True if project was successfully created. False if it failed to create.
        """
        name = widget.getUserInput('Project Name', 'What should be the name of this new project?', self)

        # user cancelled operation
        if not name:
            return False

        # validate name from empty spaces
        name.strip()  # trim leading and trailing whitespaces
        if not name:
            self.dcc_paths.warn('Empty space is not a valid project name! Please input a valid name')
            return False

        # validate name from guarded names
        if name == pcfg.create_project or name == pcfg.delete_project:
            self.dcc_paths.warn(f'{pcfg.create_project} and {pcfg.delete_project} are not valid names!')
            return False

        # validate name from existing names
        projects = piper_store.get(pcfg.projects)
        if name in projects:
            self.dcc_paths.warn(f'{name} already exists! Please input a new name')
            return False

        # add project to combo box
        self.is_blocking_combobox_callback = True
        self.project_box.insertItem(0, name)
        self.project_box.setCurrentIndex(0)
        self.is_blocking_combobox_callback = False

        # add project to store and set project as current project
        projects[name] = pcfg.project_default
        piper_store.set(pcfg.projects, projects)
        self.setProject(name)
        self.dcc_paths.display(f'Created {name} project.')
        return True

    def onDeleteProjectPressed(self):
        """
        Deletes the last selected project.

        Returns:
            (boolean): True if project was successfully delete, else False.
        """
        current_project = self.dcc_paths.getCurrentProject()

        if not current_project:
            self.dcc_paths.warn('No project was selected! Please create or select a project before deleting.')
            return False

        message = f'Are you sure you would like to delete the {current_project} project?'
        confirmation = QtWidgets.QMessageBox.question(self, 'Confirm Deletion', message)

        if confirmation != QtWidgets.QMessageBox.Yes:
            return False

        return self.deleteProject(current_project)

    def setProject(self, name):
        """
        Sets the current project to the given name.

        This must be overridden to set the current project in the DCC store.

        Args:
            name (string or None): Name of project to be used as the current project.
        """
        self.dcc_paths.setCurrentProject(project=name if name else None, force=True)

        # should be setting current project in DCC store here.
        self.last_successfully_set_project = name
        if not name:
            self.art_line.text_line.setText('')
            self.game_line.text_line.setText('')
            return

        self.updateDirectoryLines()

    def deleteProject(self, name):
        """
        Deletes the project off the piper store and sets the project on the DCC store back to None.

        Args:
            name (string): Name of project to delete.

        Returns:
            (boolean): True if project was successfully delete, else False.
        """
        empty_index = self.project_box.findText('', QtCore.Qt.MatchFixedString)
        if empty_index < 0:
            self.dcc_paths.warn('Could not find empty project! Something has gone wrong.')
            return False

        project_index = self.project_box.findText(name, QtCore.Qt.MatchFixedString)
        if project_index < 0:
            self.dcc_paths.warn(f'Could not find {name} index in QtWidget.QComboBox! Something has gone wrong.')
            return False

        self.is_blocking_combobox_callback = True
        self.project_box.removeItem(project_index)
        empty_index = self.project_box.findText('', QtCore.Qt.MatchFixedString)  # have to find again after removing
        self.is_blocking_combobox_callback = False
        self.project_box.setCurrentIndex(empty_index)
        projects = piper_store.get(pcfg.projects)
        projects.pop(name)
        piper_store.set(pcfg.projects, projects)
        self.dcc_paths.display(f'Successfully deleted {name}')
        return True

    def onSetArtPressed(self):
        """
        Sets the art directory to use for the current project.
        """
        directory = self.dcc_widget.setArtDirectory(self)
        if not directory:
            return

        self.updateDirectoryLines()

    def onSetGamePressed(self):
        """
        Sets the export path to use for the current project.
        """
        directory = self.dcc_widget.setGameDirectory(self)
        if not directory:
            return

        self.updateDirectoryLines()

    def updateDirectoryLines(self, *_, **__):
        """
        Updates the directory lines with the currently set project directories and colors them in based on the
        directory and current scene to signify the export path the scene would take.
        """
        art_directory = self.dcc_paths.getArtDirectory()
        self.art_line.updateLine(art_directory, self.dcc_paths.getSelfExport, color=self.export_color)

        game_directory = self.dcc_paths.getGameDirectory()
        self.game_line.updateLine(game_directory, self.dcc_paths.getGameExport, color=self.export_color)
