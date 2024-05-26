#  Copyright (c) Christian Corsica. All Rights Reserved.

import os

from Qt import QtWidgets, QtCore

import piper.config as pcfg
import piper.core
import piper.core.install
import piper.core.pather as pather

from piper.ui.widget import TreeWidget, TreeNodeItem, separator, addMenuItem
import piper.core.dcc as dcc
import piper.core.install.unreal_install as ue_install


class DCC(QtWidgets.QWidget):

    def __init__(self, name=''):
        super(DCC, self).__init__()

        # initial
        self.setWhatsThis('Right click to add or remove paths for Piper to install to the DCC')
        self.headers = ['Install', 'Version', 'Path']
        self.allow_context = False

        self.tree = None
        self.layout = None
        self.name = name
        self.defaults = {}

        self.build()

    def build(self):
        # layouts
        self.layout = QtWidgets.QGridLayout(self)
        label_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(label_layout, 0, 0)

        # DCC name label
        label = QtWidgets.QLabel(self.name)
        label_layout.addWidget(label, 0)

        # tree widget
        self.tree = TreeWidget()
        self.tree.setColumnCount(len(self.headers))
        self.tree.setHeaderLabels(self.headers)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tree.setSelectionBehavior(QtWidgets.QTreeView.SelectRows)
        self.tree.itemSelectionChanged.connect(self.onSelectionChanged)
        self.tree.header().setSectionsClickable(True)
        self.tree.header().sectionClicked.connect(self.onSectionClicked)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.showContextMenu)
        self.tree.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.layout.addWidget(self.tree, 1, 0)

    def onAddLinePressed(self, *args, **__):
        """
        Called to add a row to the tree widget.

        Args:
            *args (string): Text to add to columns.

        Returns:
            (TreeNodeItem): Item created and added to tree.
        """
        item = TreeNodeItem(self.tree)
        item.setCheckState(0, QtCore.Qt.Checked)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        [item.setText(i + 1, arg) for i, arg in enumerate(args)]
        item.setToolTip(2, pcfg.dcc_tooltips.get(self.name))
        return item

    def onRemoveLinePressed(self):
        """
        Removes the selected row line(s).
        """
        root = self.tree.invisibleRootItem()
        [(item.parent() or root).removeChild(item) for item in self.tree.selectedItems()]

    def onSelectionChanged(self, *_, **__):
        """
        Happens when selection is changed in order to maintain selection after checkbox is pressed.
        """
        # makes sure we keep the same items selected that we previously had when pressing checkbox
        if self.tree.is_updating:
            self.tree.is_updating = False
            [item.setSelected(True) for item in self.tree.items_to_select]
            self.tree.items_to_select = []

    def onSectionClicked(self, i):
        """
        Convenience method for toggling all the checkboxes of the section clicked.
        """
        # only the first column should have checkboxes
        if i != 0:
            return

        root = self.tree.invisibleRootItem()
        items_length = root.childCount()

        state = all([root.child(n).checkState(i) == QtCore.Qt.Checked for n in range(items_length)])
        new_state = QtCore.Qt.Unchecked if state else QtCore.Qt.Checked
        [root.child(n).setCheckState(i, new_state) for n in range(items_length)]

    def showContextMenu(self, position):
        """
        Builds and shows menu when right click is pressed on given position
        """
        if not self.allow_context:
            return

        menu = QtWidgets.QMenu(self.tree)

        add_action = QtWidgets.QAction(f'Add {self.name} path')
        add_action.triggered.connect(self.onAddLinePressed)
        menu.addAction(add_action)

        remove_action = QtWidgets.QAction('Remove Selected path(s)')
        remove_action.triggered.connect(self.onRemoveLinePressed)
        menu.addAction(remove_action)

        menu.addSeparator()

        reset_action = QtWidgets.QAction('Reset back to defaults')
        reset_action.triggered.connect(self.resetToDefaults)
        menu.addAction(reset_action)

        menu.exec_(self.tree.mapToGlobal(position))

    def addDefaults(self):
        """
        Adds the defaults DCC version(s) to the tree widget as an item for each one
        """
        [self.onAddLinePressed(version, path) for path, version in self.defaults.items()]

    def resetToDefaults(self):
        """
        Removes all the items from the tree widget and adds the default DCC version(s) stored.
        """
        self.tree.clear()
        self.addDefaults()

    @staticmethod
    def onItemDoubleClicked(item, column):
        """
        Don't allow the first column (checkbox) to be editable as text.

        Args:
            item (QtWidgets.QTreeWidgetItem): Item to get and set flags from to allow/lock edits.

            column (int): Column that was double-clicked.
        """
        flags = item.flags()

        if column == 0:
            item.setFlags(flags ^ QtCore.Qt.ItemIsEditable)
        elif flags & QtCore.Qt.ItemIsEditable:
            item.setFlags(flags | QtCore.Qt.ItemIsEditable)

    def getSelectedRows(self):
        """
        Gets the selected rows.

        Returns:
            (list): A bunch of integers representing the selected row number(s).
        """
        return list(set(index.row() for index in self.tree.selectedIndexes()))

    def getPaths(self):
        """
        Gets all the valid paths that are checked on to install as keys, and the accompanying version(s) as values.

        Returns:
            (dictionary): Valid paths checked to install as keys, version as value
        """
        paths = {}
        root = self.tree.invisibleRootItem()
        items_length = root.childCount()

        for i in range(items_length):
            item = root.child(i)
            version = item.text(1)
            path = item.text(2)

            # if install checkbox is not checked, ignore this dcc
            if item.checkState(0) != QtCore.Qt.Checked:
                continue

            if not os.path.exists(path):
                print(f'{path} does not exist! Skipping.')
                continue

            paths[path] = {'version': version}

        return paths


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Piper Installer')
        self.headers = ['Digital Content Creation (DCC)', 'Install']

        self.actions = []  # actions must be stored so they are not garbage collected
        self.widget_dccs = {}
        self.dcc_symlink_methods = {pcfg.unreal_name: ue_install.symlink}

        self.build()

    def build(self):
        # layouts
        dialog = QtWidgets.QDialog()
        self.setCentralWidget(dialog)
        main_layout = QtWidgets.QVBoxLayout(dialog)

        # menu bar
        menu = self.menuBar()
        file_menu = menu.addMenu('&Help')

        # add documentation and print info to menu bar
        addMenuItem(menu=file_menu, on_pressed=dcc.printInfo, actions=self.actions)
        addMenuItem(menu=file_menu, on_pressed=piper.core.openDocumentation, actions=self.actions)

        # fill out DCC information with what the user has installed
        installed = dcc.getInstalled()
        for dcc_name in pcfg.valid_dccs:
            installed_dcc = installed.get(dcc_name, {})
            dcc_widget = DCC(name=dcc_name)
            dcc_widget.defaults = installed_dcc
            dcc_widget.addDefaults()
            self.widget_dccs[dcc_name] = dcc_widget
            main_layout.addWidget(dcc_widget)

            # allow context to add/remove paths in unreal install
            if dcc_name == pcfg.unreal_name:
                headers = dcc_widget.headers
                headers[2] = 'Path to .uproject or Plugins'
                dcc_widget.tree.setColumnCount(len(headers))
                dcc_widget.tree.setHeaderLabels(headers)
                dcc_widget.allow_context = True

        # install button
        separator(main_layout)
        install_button = QtWidgets.QPushButton('Install Piper to Selected DCC\'s')
        install_button.clicked.connect(self.onInstallPressed)
        main_layout.addWidget(install_button)

    def onInstallPressed(self):
        """
        Runs the installers/installer methods for each DCC checked on the widget tree.
        """
        install_directory = piper.core.getPiperDirectory()
        pather.deleteCompiledScripts(install_directory)

        for dcc_name, dcc_widget in self.widget_dccs.items():
            installer = dcc.mapping.get(dcc_name)
            symlink_method = self.dcc_symlink_methods.get(dcc_name)
            paths = dcc_widget.getPaths()

            if not paths:
                continue

            print('=' * 50)
            print(dcc_name)

            if installer:
                versions = [row.get('version') for row in paths.values()]
                install_script = piper.core.install.getScriptPath(dcc_name)
                installer().runInstaller(install_script, install_directory, versions)
            elif symlink_method:
                [symlink_method(install_directory, path) for path in paths]
            else:
                print(f'{dcc_name} DCC has no associated installer!')

        print('\nFinished Piper Install. You may close this window or run other installers.')
