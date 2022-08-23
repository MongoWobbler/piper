#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import unreal as ue

import piper.core.pather as pather
import piper.core.pythoner as python


class Dependencies(object):
    """
    Gets all the dependencies recursively.

    Holds registry, and utility library, options, class names, and found package names to avoid having to recall them
    on every recursive function call.
    """
    def __init__(self):
        self.found = set()
        self.registry = ue.AssetRegistryHelpers.get_asset_registry()
        self.utilities = ue.EditorUtilityLibrary()

        self.options = ue.AssetRegistryDependencyOptions()
        self.options.include_soft_package_references = True
        self.options.include_hard_package_references = True

        self.sequence_name = 'AnimSequence'
        self.abp_name = 'AnimBlueprint'
        self.montage_name = 'AnimMontage'
        self.blendspace1_name = 'BlendSpace1D'
        self.blendspace_name = 'BlendSpace'
        self.offset1_name = 'AimOffsetBlendSpace1D'
        self.offset_name = 'AimOffsetBlendSpace'

        # main animation blueprints to get animations and other anim blueprints from
        self.main_blueprints = []

        # if True, will print each animation to unreal's output log
        self.log = False

        # if given and path is valid, will write each animation to the given path
        self.write_to_file = None

    def writeToFile(self):
        """
        Writes the found names to the write_to_file path given.
        """
        directory = os.path.dirname(self.write_to_file)
        pather.validateDirectory(directory)

        with open(self.write_to_file, 'w') as open_file:
            [open_file.write("{}\n".format(name)) for name in self.found]

        ue.log(f'Finished writing {str(len(self.found))} animations to {self.write_to_file}')

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
                cls = data.asset_class
                if cls == self.sequence_name:
                    self.found.add(data.package_name)
                elif (cls == self.abp_name or
                      cls == self.montage_name or
                      cls == self.blendspace1_name or
                      cls == self.blendspace_name or
                      cls == self.offset1_name or
                      cls == self.offset_name):
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
            [ue.log(path) for path in self.found]

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
