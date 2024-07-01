#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
from functools import partial
from pathlib import Path

from Qt import QtWidgets, QtCore, QtGui, QtCompat

import piper.config as pcfg
import piper.core
import piper.core.dcc as dcc
import piper.core.filer as filer
import piper.core.pythoner as python
from piper.core.events import dispatcher
from piper.core.perforce import Perforce, makeAvailable
from piper.core.dcc.template.paths import dcc_paths, FileType
from piper.core.dcc.template.export import dcc_export
from piper.ui.widget import setTips


class ModifierAwareMenu(QtWidgets.QMenu):

    def __init__(self, *args, **kwargs):
        """
        Menu which captures any modifier keys (shift, alt, control) in order to alter functions if any are held
        """
        super(ModifierAwareMenu, self).__init__(*args, **kwargs)
        self.setToolTipsVisible(True)
        self.is_shift_held = False
        self.is_ctrl_held = False
        self.is_alt_held = False

    def keyPressEvent(self, event):
        """
        Overriding key pressed event to know when any modifier key is pressed.

        Args:
            event (QKeyEvent): Event that holds what happened.
        """
        self.is_shift_held = event.key() == QtCore.Qt.Key_Shift
        self.is_ctrl_held = event.key() == QtCore.Qt.Key_Control
        self.is_alt_held = event.key() == QtCore.Qt.Key_Alt
        super(ModifierAwareMenu, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """
        Overriding key released event to know when any modifier keys are released.

        Args:
            event (QKeyEvent): Event that holds what happened.
        """
        self.is_shift_held = not event.key() == QtCore.Qt.Key_Shift
        self.is_ctrl_held = not event.key() == QtCore.Qt.Key_Control
        self.is_alt_held = not event.key() == QtCore.Qt.Key_Alt
        super(ModifierAwareMenu, self).keyReleaseEvent(event)


class FilterButton(QtWidgets.QPushButton):

    def __init__(self, file_type=FileType.none, *args, **kwargs):
        """
        Filter button that draws a line at the bottom of the button to represent the file type it filters.
        """
        super(FilterButton, self).__init__(*args, **kwargs)
        self.file_type = file_type
        self.type_color = pcfg.file_type_colors[file_type]

    def paintEvent(self, event):
        """
        Overriding paint event to paint lines that represent the type and whether type is exportable or not.

        Args:
            event (QtGui.QPaintEvent): Event that is calling this paint function.
        """
        super(FilterButton, self).paintEvent(event)

        if not self.isChecked():
            return

        box_height = self.height()
        line_height = int(box_height * 0.1)
        width = self.width()
        painter = QtGui.QPainter(self)

        painter.setPen(QtGui.QPen(QtGui.QBrush(self.type_color), 1))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.type_color)))

        # if the first two values are 0, 0, that means top left corner, but it doesn't include the frame
        # so adding more width to include the frame
        # draw type line horizontally
        painter.drawEllipse(-width, box_height - line_height, width * 4, line_height)


class BrowserItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, *args, **kwargs):
        """
        QTreeWidgetItem that stores paths and whether path is a directory or not.
        """
        super(BrowserItem, self).__init__(*args, **kwargs)
        self.path = None
        self.is_directory = False


class DirectoryItem(BrowserItem):

    def __init__(self, *args, **kwargs):
        """
        BrowserItem which represents a directory and stores information about its children, and whether to hide, etc.
        """
        super(DirectoryItem, self).__init__(*args, **kwargs)
        self.is_directory = True
        self.children_directories = []
        self.child_file_count = 0
        self.current_hidden_count = 0
        self.is_top_item = False
        self.setForeground(0, QtGui.QBrush(QtGui.QColor('#e3c674')))

    def setExpandOnParents(self, expand_state):
        """
        Expands the item and all the parent directory items too.

        Args:
            expand_state (boolean): Expand state to give to directory item and all its parents.
        """
        self.setExpanded(True)
        parent_item = self.parent()

        while not parent_item.is_top_item:
            parent_item.setExpanded(expand_state)
            parent_item = parent_item.parent()


class FileItem(BrowserItem):

    def __init__(self, *args, **kwargs):
        """
        BrowserItem which represent a file path along with type of file and visibility options.
        """
        super(FileItem, self).__init__(*args, **kwargs)
        self.file_type = FileType.none
        self.type_visibility = False
        self.search_visibility = False
        self.addChildFileCount()

    def addChildFileCount(self):
        """
        Adds child file count to all the parent directories of the item.
        """
        parent_item = self.parent()
        while not parent_item.is_top_item:
            parent_item.child_file_count += 1
            parent_item = parent_item.parent()

    def setInitialHidden(self, is_hidden):
        """
        Sets the initial hidden state on creation of item. Only adds to hidden count if item should be hidden.

        Args:
            is_hidden (boolean): If True, hides the item. Else shows the item
        """
        if not is_hidden:
            return

        self.type_visibility = True
        self.updateHiddenParentCount(update_count=1)
        self.setHidden(is_hidden)

    def updateVisibility(self, is_hidden):
        """
        Forces update of item visibility, this should not be called directly.
        Try calling setTypeVisibility and setSearchVisibility instead based on what is hiding the item.

        Args:
            is_hidden (boolean): Will hide the item if True, else will show them item.
        """
        update_count = 1 if is_hidden else -1
        self.updateHiddenParentCount(update_count=update_count)
        self.setHidden(is_hidden)

    def setTypeHidden(self, is_hidden):
        """
        Call this function instead of QtWidgets.QTreeWidgetItem.setHidden! This handles updating parent counts.

        Args:
            is_hidden (boolean): If True, hides the item.
        """
        # only update if changed
        if self.type_visibility == is_hidden:
            return

        self.type_visibility = is_hidden

        # search visibility is set to True, which means item must remain hidden
        if self.search_visibility:
            return

        self.updateVisibility(is_hidden)

    def setSearchHidden(self, is_hidden):
        """
        Call this function instead of QtWidgets.QTreeWidgetItem.setHidden! This handles updating parent counts.

        Args:
            is_hidden (boolean): If True, hides the item.
        """
        if self.search_visibility == is_hidden:
            return

        self.search_visibility = is_hidden

        # type visibility is set to True, which means item must remain hidden
        if self.type_visibility:
            return

        self.updateVisibility(is_hidden)

    def updateHiddenParentCount(self, update_count=1):
        """
        Adds the given update_count to all the item's parents' current hidden count in order to keep track
        of how many items the directory is hiding.

        Args:
            update_count (int): How much to add or subtract of current hidden count. Usually 1 or -1.
        """
        parent_item = self.parent()
        while not parent_item.is_top_item:
            parent_item.current_hidden_count += update_count
            parent_item = parent_item.parent()


class Browser(QtWidgets.QDialog):

    @property
    def mesh_config(self):
        raise NotImplementedError

    @property
    def skeleton_config(self):
        raise NotImplementedError

    @property
    def rig_config(self):
        raise NotImplementedError

    @property
    def animation_config(self):
        raise NotImplementedError

    @property
    def other_config(self):
        raise NotImplementedError

    @property
    def expanded_directories_config(self):
        raise NotImplementedError

    def __init__(self, app=None, *args, **kwargs):
        """
        Window to handle batching operations of files.
        """
        super(Browser, self).__init__(*args, **kwargs)
        self.setWindowTitle(pcfg.browser_name)
        self.app = app
        self.tree = None
        self.top_item = None
        self.icons_directory = piper.core.getIconsDirectory()

        # widgets
        self.search_button = None
        self.search_bar = None
        self.completer = None
        self.completer_model = None
        self.selected_label = None
        self.total_label = None
        self.buttons_layout = None
        self.context_menu = None

        # useful data
        self.names = []
        self.directories = []
        self.expanded_directories = set()
        self.types = self.defineTypes()
        self.search_icon = QtGui.QIcon(f'{self.icons_directory}/piper_search.png')
        self.x_icon = QtGui.QIcon(f'{self.icons_directory}/piper_x.png')

        # update data
        self.is_shift_held = False
        self.is_updating_items = False
        self.is_batching = False
        self.is_changing_projects = False
        self.searched = False

        if not self.app:
            self.app = dcc.get(error=False)

        if not self.app:
            self.app = 'DCC'

        # overridable attributes
        self.extensions = pcfg.dcc_extensions.get(self.app)
        self.store = None
        self.dcc_paths = dcc_paths
        self.dcc_export = dcc_export

        # build / binding events
        self.build()
        dispatcher.listen(pcfg.before_project_change_event, self.onBeforeProjectChange)
        dispatcher.listen(pcfg.after_project_change_event, self.onAfterProjectChange)
        dispatcher.listen(pcfg.before_art_directory_change_event, self.onBeforeArtDirectoryChange)
        dispatcher.listen(pcfg.after_art_directory_change_event, self.onAfterArtDirectoryChange)

    def keyPressEvent(self, event):
        """
        Overriding key pressed event to know when shift key is pressed.

        Args:
            event (QKeyEvent): Event that holds what happened.
        """
        self.is_shift_held = event.key() == QtCore.Qt.Key_Shift
        super(Browser, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """
        Overriding key released event to know when shift key is released.

        Args:
            event (QKeyEvent): Event that holds what happened.
        """
        self.is_shift_held = not event.key() == QtCore.Qt.Key_Shift
        super(Browser, self).keyReleaseEvent(event)

    def createFilterButton(self, file_type):
        """
        Convenience method for creating checkable button.

        Args:
            file_type (FileType): Type of file this button represents to filter.

        Returns:
            (FilterButton): Button widget that was created
        """
        button = FilterButton(file_type, self.types[file_type]['name'])
        method = partial(self.onFilterPressed, file_type)
        method.__doc__ = self.onFilterPressed.__doc__
        method.__name__ = self.onFilterPressed.__name__
        self.types[file_type]['method'] = method
        self.types[file_type]['button'] = button
        button.setCheckable(True)
        button.setChecked(True)
        setTips(method, button, module=self.onFilterPressed.__module__)
        button.clicked.connect(method)
        button.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        self.buttons_layout.addWidget(button)

        if not self.store:
            return button

        stored_state = self.store.get(self.types[file_type]['config'])
        button.setChecked(stored_state)
        self.types[file_type]['hidden'] = not stored_state
        return button

    def createIconButton(self, icon_name, method):
        """
        Convenience method for creating an icon button.

        Args:
            icon_name (string): Name of icon to find in icons directory.

            method (Callable): Function to call when button is pressed.

        Returns:
            (QtWidgets.QToolButton): Button widget that was created.
        """
        button = QtWidgets.QToolButton()
        select_icon = QtGui.QIcon(f'{self.icons_directory}/{icon_name}.png')
        button.setIcon(select_icon)
        button.setFocusPolicy(QtCore.Qt.NoFocus)
        button.setAutoRaise(True)
        setTips(method, button)
        button.clicked.connect(method)
        self.buttons_layout.addWidget(button)
        return button

    def defineTypes(self):
        """
        Gets what filter buttons this browser will have. This can be overridden as long as it return a proper
        dictionary.

        Returns:
            (dictionary): File type as key, dictionary as value with the following as string keys:
             name, config, method, button, hidden, and files..
        """
        mesh_icon = QtGui.QIcon(f'{self.icons_directory}/piper_mesh_vertical_line.png')
        skeleton_icon = QtGui.QIcon(f'{self.icons_directory}/piper_skinned_mesh_vertical_line.png')
        rig_icon = QtGui.QIcon(f'{self.icons_directory}/piper_rig_vertical_line.png')
        animation_icon = QtGui.QIcon(f'{self.icons_directory}/piper_animation_vertical_line.png')
        none_icon = QtGui.QIcon(f'{self.icons_directory}/piper_null_vertical_line.png')

        types = {FileType.static_mesh:   {'name': 'Mesh',
                                          'config': self.mesh_config,
                                          'icon': mesh_icon},
                 FileType.skeletal_mesh: {'name': 'Skeleton',
                                          'config': self.skeleton_config,
                                          'icon': skeleton_icon},
                 FileType.rig:           {'name': 'Rig',
                                          'config': self.rig_config,
                                          'icon': rig_icon},
                 FileType.animation:     {'name': 'Animation',
                                          'config': self.animation_config,
                                          'icon': animation_icon},
                 FileType.none:          {'name': 'Other',
                                          'config': self.other_config,
                                          'icon': none_icon}}

        for file_type in types:
            types[file_type]['method'] = None
            types[file_type]['button'] = None
            types[file_type]['hidden'] = False
            types[file_type]['items'] = []

        return types

    def build(self):
        """
        Creates all the widgets
        """
        # layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        search_layout = QtWidgets.QHBoxLayout()
        label_layout = QtWidgets.QHBoxLayout()

        # filter buttons
        [self.createFilterButton(file_type) for file_type in self.types]

        # icon buttons
        self.createIconButton('piper_select', self.selectScene)
        self.createIconButton('piper_reload', self.onReloadButtonPressed)

        # search button
        self.search_button = QtWidgets.QToolButton()
        self.search_button.setIcon(self.search_icon)
        self.search_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.search_button.setAutoRaise(True)
        setTips(self.onSearchButtonPressed, self.search_button)
        self.search_button.clicked.connect(self.onSearchButtonPressed)
        search_layout.addWidget(self.search_button)

        # search bar
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText('Search...')
        self.search_bar.textChanged.connect(self.onSearchTextChanged)
        self.search_bar.returnPressed.connect(self.onSearch)
        search_layout.addWidget(self.search_bar)

        # search bar model / auto-complete
        self.completer_model = QtCore.QStringListModel(self)
        self.completer = QtWidgets.QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.search_bar.setCompleter(self.completer)

        # tree with all directories/paths
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionBehavior(QtWidgets.QTreeView.SelectRows)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.tree.itemExpanded.connect(self.onItemExpanded)
        self.tree.itemCollapsed.connect(self.onItemCollapsed)
        self.tree.itemSelectionChanged.connect(self.updateSelectedLabel)
        self.tree.customContextMenuRequested.connect(self.showContextMenu)

        # selected label
        self.selected_label = QtWidgets.QLabel('0 path(s) | 0 folder(s) | 0 selected')
        self.selected_label.setFrameStyle(QtWidgets.QFrame.WinPanel | QtWidgets.QFrame.Sunken)
        self.selected_label.setLineWidth(1)
        label_layout.addWidget(self.selected_label)

        # spacer to separate labels
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        label_layout.addItem(spacer)

        # total items label
        self.total_label = QtWidgets.QLabel('files: 0')
        self.total_label.setFrameStyle(QtWidgets.QFrame.WinPanel | QtWidgets.QFrame.Sunken)
        self.total_label.setLineWidth(1)
        label_layout.addWidget(self.total_label)

        # must call reload after all widgets have been created
        self.reload(select_current=True, save_expanded_directories=False)

        # adding widgets / layouts to main layout
        main_layout.addLayout(self.buttons_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.tree)
        main_layout.addLayout(label_layout)

    def loadTree(self, starting_directory=None):
        """
        Starts the directory read for the Tree Widget.
        """
        if not starting_directory:
            starting_directory = self.dcc_paths.getArtDirectory(error=True)

        self.top_item = DirectoryItem(self.tree, [os.path.basename(starting_directory), '', '', ''])
        self.top_item.path = Path(starting_directory)
        self.top_item.is_top_item = True
        self.top_item.is_directory = True
        self.top_item.setExpanded(True)
        self.readDirectory(self.top_item.path, self.top_item)

    def readDirectory(self, path, parent_item):
        """
        Recursive read of directory that populates tree widget.

        Args:
            path (pathlib.Path): Full path to file or directory. If directory, will call this function again.

            parent_item (BrowserItem): Item to parent new item to.
        """
        directory = os.listdir(path)

        for file_name in directory:
            file_path = path / file_name

            if file_name.endswith(self.extensions):
                item = FileItem(parent_item, [file_path.stem, '', '', ''])
                item.path = file_path
                item.file_type = self.dcc_paths.getFileType(path, file_name)
                item.setIcon(0, self.types[item.file_type]['icon'])
                item.setToolTip(0, file_path.as_posix())
                item.setInitialHidden(self.types[item.file_type]['hidden'])
                self.types[item.file_type]['items'].append(item)
                self.names.append(file_path.stem)

            elif os.path.isdir(file_path):
                item = DirectoryItem(parent_item, [file_name, '', '', ''])
                item.path = file_path
                item.setToolTip(0, file_path.as_posix())
                parent_item.children_directories.append(item)
                item.setExpanded(item.path in self.expanded_directories)
                self.directories.append(item)
                self.readDirectory(file_path, item)

    def updateSelectedLabel(self):
        """
        Updates the selected items label with how many items are currently selected and their type.
        """
        selected_items = self.tree.selectedItems()
        total_selected = len(selected_items)
        directories_selected = 0

        for item in selected_items:
            if item.is_directory:
                directories_selected += 1

        paths = total_selected - directories_selected
        self.selected_label.setText(f'{paths} path(s) | {directories_selected} folder(s) | {total_selected} selected')

    def updateTotalLabel(self):
        """
        Updates the total files label with the current visible path items' count.
        """
        total_items = sum([d.child_file_count - d.current_hidden_count for d in self.top_item.children_directories])
        self.total_label.setText(f'files: {total_items}')

    def onItemsHiddenUpdate(self):
        """
        Updates the directories visibility after items have been shown/hidden.
        """
        [item.setHidden(item.current_hidden_count >= item.child_file_count) for item in self.directories]
        self.updateTotalLabel()

    def removeItems(self):
        """
        Removes all the items from the QWidgetTree.
        """
        if not self.top_item:
            return

        QtCompat.delete(self.top_item)

        for file_type in self.types:
            self.types[file_type]['items'].clear()
            self.types[file_type]['items'] = []

        self.directories.clear()
        self.directories = []
        self.names.clear()
        self.names = []
        self.search_bar.setText("")
        # self.setSearchState(False)
        self.top_item = None

    def removeEmptyDirectories(self):
        """
        Removes all empty directories from the item tree widget.
        """
        to_keep = []
        for item in reversed(self.directories):
            if item.childCount():
                to_keep.append(item)
            else:
                item.parent().children_directories.remove(item)
                QtCompat.delete(item)

        self.directories = to_keep

    def saveExpandedDirectories(self):
        """
        Saves/stores the expanded directories in the DCC's store.

        Returns:
            (boolean): True if save was successful.
        """
        # if there is no current project set, then there are no directories to save
        current_project = self.dcc_paths.getCurrentProject()
        if not current_project:
            return False

        expanded_directories = [item.path.as_posix() for item in self.directories if item.isExpanded()]
        stored_directories = self.store.get(self.expanded_directories_config)
        stored_directories[current_project] = expanded_directories
        self.store.set(self.expanded_directories_config, stored_directories, write=True)
        return True

    def loadExpandedDirectories(self):
        """
        Loads the previously expanded directories into the expanded_directories variable of the Browser class.

        Returns:
            (boolean): True if load was successful.
        """
        self.expanded_directories = set()
        current_project = self.dcc_paths.getCurrentProject()
        if not current_project:
            return False

        project_expanded_directories = self.store.get(self.expanded_directories_config)
        previously_expanded_directories = project_expanded_directories.setdefault(current_project, [])
        self.expanded_directories = {Path(path) for path in previously_expanded_directories}
        return True

    def reload(self, select_current=True, save_expanded_directories=False):
        """
        Reloads the tree widget by removing all the items and reading all the directories recursively.
        Useful for when new files are saved or added in directories.

        Args:
            select_current (boolean): If True, will select the item that is associated with the current scene.

            save_expanded_directories (boolean): If True, will remember which directories were expanded after reloading.
        """
        if save_expanded_directories:
            self.saveExpandedDirectories()

        self.loadExpandedDirectories()
        self.removeItems()

        art_directory = self.dcc_paths.getArtDirectory()
        if not art_directory:
            self.dcc_paths.warn('Art Directory is not set! '
                                'Please set art directory in Projects before opening Browser window.')
            return

        self.loadTree()
        self.removeEmptyDirectories()
        self.completer_model.setStringList(self.names)
        self.onItemsHiddenUpdate()

        if select_current:
            self.selectScene(display_not_found=False)

    def selectScene(self, scene=None, display_not_found=True):
        """
        Selects the item associated with the given scene in the widget tree if found.

        Args:
            scene (string): Full path to scene that matches an item path in the widget tree.

            display_not_found (boolean): If True, will display that scene was not found.

        Returns:
            (boolean): True if scene was found and selected.
        """
        if not scene:
            scene = self.dcc_paths.getCurrentScene()

        if not scene:

            if display_not_found:
                self.dcc_paths.display("Can't find a scene that is not saved/doesn't exist!")

            return False

        path = Path(scene)
        file_type = self.dcc_paths.getFileType(str(path.parent), path.name)
        for item in self.types[file_type]['items']:

            if item.path == path:
                button = self.types[item.file_type]['button']

                # setting button to checked if it is not in order to select item since it could be hidden
                if not button.isChecked():
                    button.setChecked(True)
                    self.types[item.file_type]['method']()

                item.parent().setExpandOnParents(True)
                self.tree.setCurrentItem(item)
                return True

        if display_not_found:
            self.dcc_paths.display(f'{path} is not in {self.top_item.path}!')

        return False

    def onClosePressed(self):
        """
        This method should be called when window closes. Stores window's settings and removes callback(s).
        """
        dispatcher.unlisten(pcfg.before_project_change_event, self.onBeforeProjectChange)
        dispatcher.unlisten(pcfg.after_project_change_event, self.onAfterProjectChange)
        dispatcher.unlisten(pcfg.before_art_directory_change_event, self.onBeforeArtDirectoryChange)
        dispatcher.unlisten(pcfg.after_art_directory_change_event, self.onAfterArtDirectoryChange)

        if not self.store:
            return

        [self.store.set(self.types[t]['config'], self.types[t]['button'].isChecked(), write=False) for t in self.types]

        # if save of store didn't happen in expanded directories function, then we must manually call write settings
        if not self.saveExpandedDirectories():
            self.store.writeSettings()

    def onFilterPressed(self, file_type, *_):
        """
        Sets the visibility of the item if it is of the button type based on the button toggle state.
        """
        state = not self.types[file_type]['button'].isChecked()
        self.types[file_type]['hidden'] = state
        text = self.search_bar.text().lower()

        if text:
            self.setSearchState(True)
            for item in self.types[file_type]['items']:
                item.setTypeHidden(state)
                item.setSearchHidden(text not in item.path.stem.lower())

        else:
            [item.setTypeHidden(state) for item in self.types[file_type]['items']]

        self.onItemsHiddenUpdate()

    def onReloadButtonPressed(self):
        """
        Reloads the tree widget by removing all the items and reading all the directories recursively.
        Useful for when new files are saved or added in directories.
        """
        self.reload(select_current=False, save_expanded_directories=True)

    def setSearchState(self, state):
        """
        Sets the current state of the search. Changes icon according to the search state.

        Args:
            state (boolean): If True, a search has occurred and items are filtered. False no items are filtered.
        """
        self.searched = state
        icon = self.x_icon if state else self.search_icon
        self.search_button.setIcon(icon)

    def onSearchTextChanged(self):
        """
        Shows all the items that are not hidden by the filter type if there is nothing in the search bar.
        """
        if not self.searched or self.search_bar.text():
            return

        [i.setSearchHidden(False) for t in self.types if not self.types[t]['hidden'] for i in self.types[t]['items']]
        self.onItemsHiddenUpdate()
        self.setSearchState(False)

    def onSearch(self):
        """
        Filters the items in the QTreeWidget by hiding any items that don't match the search bar text.
        Only runs through items not already hidden by filter.
        """
        text = self.search_bar.text().lower()
        if not text:
            return

        self.setSearchState(True)
        for file_type in self.types:
            if self.types[file_type]['hidden']:
                continue

            for item in self.types[file_type]['items']:
                item.setSearchHidden(text not in item.path.stem.lower())

        self.onItemsHiddenUpdate()

    def onSearchButtonPressed(self):
        """
        Triggers a search if there's text and there is no current search, else clears the search.
        """
        if self.searched:
            self.search_bar.setText("")
            self.search_bar.setFocus()
            return

        self.onSearch()
        self.search_bar.setFocus()

    def onBeforeProjectChange(self):
        """
        Called right before project changes to save which directories were expanded.
        """
        self.saveExpandedDirectories()
        self.is_changing_projects = True

    def onAfterProjectChange(self):
        """
        Called right after project finishes changing to reload directories.
        """
        self.reload(select_current=True, save_expanded_directories=False)
        self.is_changing_projects = False

    def onBeforeArtDirectoryChange(self):
        """
        Called right before art directory changes to save which directories were expanded if we're not in the middle
        of changing projects.
        """
        if self.is_changing_projects:
            return

        self.saveExpandedDirectories()

    def onAfterArtDirectoryChange(self):
        """
        Called right after art directory finishes changing to reload directories if we're not in the middle
        of changing projects.
        """
        if self.is_changing_projects:
            return

        self.reload(select_current=True, save_expanded_directories=False)

    @staticmethod
    def getItemsPaths(items):
        """
        Gets the paths of the selected file items in the tree.

        Args:
            items (list): FileItem items to get names from.

        Returns:
            (list): Path for each item.
        """
        return [str(item.path.as_posix()) for item in items]

    @staticmethod
    def getFilesNames(items):
        """
        Gets the name of the selected file items without the extension.

        Args:
            items (list): FileItem items to get names from.

        Returns:
            (list): Name for each item.
        """
        return [item.path.stem for item in items]

    def copyFilesPaths(self, items):
        """
        Filters items for files only and copies their path to the clipboard.
        - If SHIFT is held, will copy P4 depot paths instead.
        - if CTRL is held, will copy each path enclosed by quotation marks, and separated by a comma plus space.

        Args:
            items (list): Items whose path will be copied to the clipboard if they are files.
        """
        paths = self.getItemsPaths(items=items)
        if not self.context_menu.is_shift_held:

            if not self.context_menu.is_ctrl_held:
                filer.copyToClipboard('\n'.join(paths))
                return

            formatted_paths = python.listToStrings(paths)
            filer.copyToClipboard(formatted_paths)

        p4 = Perforce()
        with p4.connect():
            info = p4.getInfo(path=paths)

        if not info:
            self.dcc_paths.warn('Could not get depot info from selected items!')
            return

        paths = [data['depotFile'] for data in info]
        if not self.context_menu.is_ctrl_held:
            filer.copyToClipboard('\n'.join(paths))
            return

        formatted_paths = python.listToStrings(paths)
        filer.copyToClipboard(formatted_paths)

    def copyFilesNames(self, items):
        """
        Filters items for files only and copies their name to the clipboard without extensions.
        - if CTRL is held, will copy each name enclosed by quotation marks, and separated by a comma plus space.

        Args:
            items (list): Items whose name will be copied to the clipboard if they are files.
        """
        names = self.getFilesNames(items=items)
        formatted_names = python.listToStrings(names) if self.context_menu.is_ctrl_held else '\n'.join(names)
        filer.copyToClipboard(formatted_names)

    def copyFoldersPaths(self, items):
        """
        Filters items for directories only and copies their path to the clipboard.
        - if CTRL is held, will copy each name enclosed by quotation marks, and separated by a comma plus space.

        Args:
            items (list): Items whose path will be copied to the clipboard if they are directories.
        """
        paths = self.getItemsPaths(items=items)
        formatted_paths = python.listToStrings(paths) if self.context_menu.is_ctrl_held else '\n'.join(paths)
        filer.copyToClipboard(formatted_paths)

    def onItemDoubleClicked(self, item, *_):
        """
        Opens the scene in the DCC when the given item is double-clicked in the tree widget.

        Args:
            item (BrowserItem): Item that was double-clicked.
        """
        self.dcc_paths.open(item.path)

    def setExpandOnChildren(self, item, expand_state):
        """
        Recursively set to expand state on all the given item's children directories.

        Args:
            item (BrowserItem): Item to recursively set all to expand state.

            expand_state (boolean): State the expand should have.
        """
        for child_item in item.children_directories:
            child_item.setExpanded(expand_state)
            self.setExpandOnChildren(child_item, expand_state)

    def onItemExpanded(self, item):
        """
        Called when item is expanded to be able to expand all its children if shift held.

        Args:
            item (BrowserItem): Item that was expanded.
        """
        if self.is_updating_items:
            return

        if not self.is_shift_held:
            return

        self.is_updating_items = True
        self.setExpandOnChildren(item, True)
        self.is_updating_items = False

    def onItemCollapsed(self, item):
        """
        Called when item is collapsed to be able to collapse all its children if shift held.

        Args:
            item (BrowserItem): Item that was collapsed.
        """
        if self.is_updating_items:
            return

        if not self.is_shift_held:
            return

        self.is_updating_items = True
        self.setExpandOnChildren(item, False)
        self.is_updating_items = False

    def menuItemsAction(self, name, enabled, method, *args):
        """
        Convenience method for creating an items action used in menus which takes it several
        arguments to the given method.

        Args:
            name (string): Name of action.

            enabled (boolean): If True, action will be enabled and usable, else will be greyed out.

            method (Callable): Function to call when action is pressed.

        Returns:
            (QtWidgets.QAction): Action created.
        """
        action = QtWidgets.QAction(name)
        action.triggered.connect(partial(method, *args))
        setTips(method, action)
        action.setEnabled(enabled)
        self.context_menu.addAction(action)
        return action

    def makeItemsAvailable(self, items):
        """
        Makes the given items available in P4 by checking out or adding any of the given items to a changelist

        Args:
            items (list): Items to make available to the user in P4.
        """
        paths = self.getItemsPaths(items)
        makeAvailable(path=paths)

    @staticmethod
    def unavailableTip(widget, insert_text):
        """
        Convenience method for inserting given insert_text at the start of the tooltip of a widget.

        Args:
            widget (QtWidgets.QWidget): Widget to insert tooltip to.

            insert_text (string): Text to add at start of widget tooltip.
        """
        tip = widget.toolTip()
        tip = f'Action UNAVAILABLE because {insert_text}\n{tip}'
        widget.setToolTip(tip)

    def showContextMenu(self, position):
        """
        Shows the context menu (right click).
        """
        items = self.tree.selectedItems()

        if not items:
            return

        self.context_menu = ModifierAwareMenu(self.tree)

        # data
        item = items[0].path
        file_items, folder_items, exportable_items = self.getFilteredItemsData(items)
        is_files = bool(file_items)
        is_folders = bool(folder_items)
        is_exportable = bool(exportable_items)
        is_single_item = len(items) == 1
        is_single_file_item = len(file_items) == 1

        # must assign action to a variable so that python doesn't garbage collected before menu appears
        name_action = self.menuItemsAction('Copy File Name(s)', is_files, self.copyFilesNames, file_items)
        file_action = self.menuItemsAction('Copy File Path(s)', is_files, self.copyFilesPaths, file_items)
        folder_action = self.menuItemsAction('Copy Folder Path(s)', is_folders, self.copyFoldersPaths, folder_items)
        self.context_menu.addSeparator()

        # the following actions only work if we have exportable items selected
        export_game_action = QtWidgets.QAction('Export to Game')
        export_game_method = partial(self.export, self.dcc_export.exportToGame, file_items)
        export_game_action.triggered.connect(export_game_method)
        export_game_action.setEnabled(is_exportable)
        setTips(dcc_export.exportToGame, export_game_action)
        self.context_menu.addAction(export_game_action)

        export_art_action = QtWidgets.QAction('Export to Current Directory')
        export_art_method = partial(self.export, self.dcc_export.exportToCurrentDirectory, file_items)
        export_art_action.triggered.connect(export_art_method)
        export_art_action.setEnabled(is_exportable)
        setTips(dcc_export.exportToCurrentDirectory, export_art_action)
        self.context_menu.addAction(export_art_action)
        self.context_menu.addSeparator()

        # the following actions only work if only one item is selected
        open_os_action = self.menuItemsAction('Open In Browser', is_single_item, filer.openWithOS, item)

        # only works if item is not directory
        open_dcc_action = self.menuItemsAction(f'Open in {self.app}', is_single_file_item, self.dcc_paths.open, item)

        self.context_menu.addSeparator()
        p4_available_action = self.menuItemsAction('P4 Make Available', is_files, self.makeItemsAvailable, file_items)

        if not is_files:
            self.unavailableTip(name_action, 'no file items are selected!')
            self.unavailableTip(file_action, 'no file items are selected!')
            self.unavailableTip(p4_available_action, 'no file items are selected!')

        if not is_exportable:
            self.unavailableTip(export_game_action, 'no exportable file types are selected!')
            self.unavailableTip(export_art_action, 'no exportable file types are selected!')

        if not is_folders:
            self.unavailableTip(folder_action, 'no directory items are selected!')

        if not is_single_item:
            self.unavailableTip(open_os_action, 'multiple files are selected!')

            if not is_single_file_item:
                self.unavailableTip(open_dcc_action, 'multiple files are selected or selected item is directory!')

        self.context_menu.exec_(self.tree.mapToGlobal(position))

    def getFilteredItemsData(self, items=None):
        """
        Splits the given items (if none given, will use selected) into recursively found shown file items, and currently
        selected directory items.

        Args:
            items (list): Browser Items to separate into file, directory, and exportable

        Returns:
            (list): File items set as first index, directory items as second index, and exportable as third index.
        """
        if not items:
            items = self.tree.selectedItems()

        file_items = []
        directory_items = []
        exportable_items = set()

        for item in items:

            if item.is_directory:
                self._getDirectoryFilteredFiles(item, exportable_items)
                directory_items.append(item)
            else:
                file_items.append(item)

                if self.dcc_paths.is_exportable[item.file_type]:
                    exportable_items.add(item)

        return file_items, directory_items, exportable_items

    def getDirectoryFilteredFileItems(self, items=None):
        """
        Gets all the given directory's child items that are files, are not hidden, and are exportable.

        Args:
            items (list): Items to get file items from.

        Returns:
            (set): File items that are exportable and not hidden.
        """
        if not items:
            items = self.tree.selectedItems()

        files = set()
        for item in items:

            if item.is_directory:
                self._getDirectoryFilteredFiles(item, files)
            elif self.dcc_paths.is_exportable[item.file_type]:
                files.add(item)

        return files

    def _getDirectoryFilteredFiles(self, directory, filtered_set):
        """
        Recursively gets all the given directory's child items that are files, are not hidden, adn are exportable.

        Args:
            directory (DirectoryItem): Directory to recursively get child items which are FileItems and not hidden.

            filtered_set (set): Set to add file items to.
        """
        for i in range(directory.childCount()):
            child_item = directory.child(i)

            # don't take child item that is hidden into consideration
            if child_item.isHidden():
                continue

            if child_item.is_directory:
                self._getDirectoryFilteredFiles(child_item, filtered_set)
            elif self.dcc_paths.is_exportable[child_item.file_type]:
                filtered_set.add(child_item)

    def export(self, export_method, file_items=None):
        """
        Exports the given items with the given export_method.

        Args:
            export_method (Callable): Function used to export from item's paths.

            file_items (list): Items with paths to export.
        """
        if not file_items:
            file_items = self.getDirectoryFilteredFileItems()

        # adding try/finally to make sure to turn off batching state even if batch export fails.
        try:
            self.is_batching = True
            for item in file_items:
                self.dcc_paths.open(item.path.as_posix())
                export_method()
        finally:
            self.is_batching = False

        self.selectScene(display_not_found=False)
