#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import json

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import pymel.core as pm

from piper.ui.widget import manager
from piper.ui.clipper import Clipper


class MayaClipper(MayaQWidgetDockableMixin, Clipper):

    def __init__(self, *args, **kwargs):
        super(MayaClipper, self).__init__(*args, **kwargs)
        manager.register(self)

    def getAnimations(self):
        """
        Gets all the animations nodes in scene with their corresponding clip data.

        Returns:
            (dictionary): Data from each animation node's clipData attribute encoded as dictionary.
        """
        clip_data = {}
        animations = pm.ls(type='piperAnimation')

        for animation in animations:
            data = animation.clipData.get()

            if data:
                data = json.loads(data)

            clip_data[animation.name()] = data

        return clip_data

    def onSavePressed(self):
        """
        Writes data found in the AnimClip widgets into the associated nodes clipData attribute as parsed dictionaries.
        """
        for widget in self.anim_widgets:
            data = widget.getData()

            for animation_name, clip_data in data.items():
                piper_animation = pm.PyNode(animation_name)
                parsed_data = json.dumps(clip_data)
                piper_animation.clipData.set(parsed_data)

    def dockCloseEventTriggered(self):
        """
        Happens when clipper window closes, useful to unregister clipper for widget window manager.
        """
        manager.unregister(self)
        super(MayaClipper, self).dockCloseEventTriggered()


def show():
    """
    Convenience method for showing the MayaClipper widget

    Returns:
        (MayaClipper): Widget created.
    """
    gui = MayaClipper()
    gui.show(dockable=True)
    return gui
