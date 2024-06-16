#  Copyright (c) Christian Corsica. All Rights Reserved.

from piper.core.dcc.template.widget_tk import WidgetTKDCC
import piper.unrealpy.paths as paths


class UnrealWidget(WidgetTKDCC):

    def __init__(self):
        super(UnrealWidget, self).__init__()
        self.dcc_paths = paths.get()


unreal_widget = UnrealWidget()


def get():
    """
    Convenience method for getting the unreal_widget. Useful in menu creation.

    Returns:
        (UnrealPaths): WidgetTKDCC class for Unreal.
    """
    return unreal_widget
