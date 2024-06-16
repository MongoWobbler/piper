#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import unreal as ue

import piper.core.pather as pather
import piper.core.pythoner as python
import piper.unrealpy.browser as browser


class Hierarchy(object):
    def __init__(self):

        self.found = set()
        self.no_found_message = "Didn't find anything!"
        self.registry = ue.AssetRegistryHelpers.get_asset_registry()
        self.utilities = ue.EditorUtilityLibrary()
        self.registry_helpers = ue.AssetRegistryHelpers()
        self.system_library = ue.SystemLibrary()

        self.options = ue.AssetRegistryDependencyOptions(True, True)

        self.sequence_name = 'AnimSequence'
        self.abp_name = 'AnimBlueprint'
        self.montage_name = 'AnimMontage'
        self.blendspace1_name = 'BlendSpace1D'
        self.blendspace_name = 'BlendSpace'
        self.offset1_name = 'AimOffsetBlendSpace1D'
        self.offset_name = 'AimOffsetBlendSpace'

        self.filter = ue.ARFilter(class_names=[self.sequence_name])

        # main animation blueprints to get animations and other anim blueprints from
        self.main_blueprints = []

        # if given and path is valid, will write each animation to the given path
        self.write_to_file = None

        # if True, will print each animation to unreal's output log
        self.log = False

    def writeToFile(self):
        """
        Writes the found names to the write_to_file path given.
        """
        found = list(self.found)
        found.sort()

        directory = os.path.dirname(self.write_to_file)
        pather.validateDirectory(directory)

        with open(self.write_to_file, 'w') as open_file:
            [open_file.write("{}\n".format(str(name))) for name in found]

        ue.log(f'Finished writing {str(len(found))} assets to {self.write_to_file}')

    def displayFound(self):
        """
        Logs all the paths found, if any.
        """
        found = list(self.found)
        found.sort()

        found_count = len(found)
        if not found_count:
            ue.log(self.no_found_message)
            return

        ue.log(f'Found {str(found_count)} assets.')
        [ue.log(path) for path in found]

    def get(self, assets):
        pass

    def _getRecursive(self, name):
        pass

    def getFromSelected(self):
        pass


class References(Hierarchy):
    def __init__(self):
        super(References, self).__init__()
        self.starting_directory = '/Game/'
        self.no_found_message = 'Found no references.'

    @python.measureTime
    def get(self, assets):
        """
        Get all the assets that are not being referenced a.k.a. not being used by anything.

        Args:
            assets (list): Consists of unreal.AssetData to get more references or packages from.
        """
        assets = self.registry.run_assets_through_filter(assets, self.filter)

        with ue.ScopedSlowTask(len(assets), 'Getting References') as task:
            task.make_dialog(True)

            for asset in assets:
                if task.should_cancel():
                    return

                task.enter_progress_frame(1)
                name = asset.package_name

                if not self.registry.get_referencers(name, self.options) and not asset.is_redirector():
                    self.found.add(name)

        if self.write_to_file:
            self.writeToFile()

        if self.log:
            self.displayFound()

    def getFromSelected(self):
        """
        Convenience method to get all references data from the selected assets.
        """
        assets = browser.getSelectedAssetData(recursive=True)
        self.get(assets)

    def getFromDirectory(self):
        """
        Convenience method to get all the animation sequences not being referenced in the specified directory.
        """
        assets = self.registry.get_assets_by_path(ue.Name(self.starting_directory), True)
        self.get(assets)


class Dependencies(Hierarchy):
    """
    Gets all the dependencies recursively.

    Holds registry, and utility library, options, class names, and found package names to avoid having to recall them
    on every recursive function call.
    """
    def __init__(self):
        super(Dependencies, self).__init__()
        self.no_found_message = 'Found no dependencies.'

    def _getRecursive(self, name):
        """
        Gets the given package name dependencies and adds them to the class' "found" variable if it's an anim sequence.

        Args:
            name (string or Name): Full path of the package.

        Returns:
            (string): Path to animation sequence.
        """
        dependencies = self.registry.get_dependencies(name, self.options)
        for dependency in dependencies:
            asset_data = self.registry.get_assets_by_package_name(dependency)
            for data in asset_data:
                asset_class = self.registry_helpers.get_class(data)
                class_name = self.system_library.get_class_display_name(asset_class)
                if class_name == self.sequence_name:
                    self.found.add(data.package_name)
                elif (class_name == self.abp_name or
                      class_name == self.montage_name or
                      class_name == self.blendspace1_name or
                      class_name == self.blendspace_name or
                      class_name == self.offset1_name or
                      class_name == self.offset_name):
                    self._getRecursive(data.package_name)

    @python.measureTime
    def get(self, asset_data):
        """
        Gets all the dependencies from the given asset data

        Args:
            asset_data (list): Consists of unreal.AssetData to get more dependencies or package name from.
        """
        with ue.ScopedSlowTask(len(asset_data), 'Getting Dependencies') as task:
            task.make_dialog(True)

            for data in asset_data:
                if task.should_cancel():
                    return

                task.enter_progress_frame(1)
                self._getRecursive(data.package_name)

        if self.write_to_file:
            self.writeToFile()

        if self.log:
            self.displayFound()

    def getFromSelected(self):
        """
        Convenience function to get the dependencies from the selected asset.
        """
        asset_data = self.utilities.get_selected_asset_data()
        self.get(asset_data)

    def getFromAnimBlueprints(self):
        """
        Convenience function to get the dependencies from the given animation blueprints.
        """
        asset_data = self.registry.get_assets_by_paths(self.main_blueprints)
        self.get(asset_data)


def printUnusedSequences():
    """
    Prints all the unused animation sequence assets in the game directory.
    """
    referencer = References()
    referencer.log = True
    referencer.getFromDirectory()


def printUnusedSelectedSequences():
    """
    Prints all the unused animation sequence assets that are selected.
    """
    referencer = References()
    referencer.log = True
    referencer.getFromSelected()
