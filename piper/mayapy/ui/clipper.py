#  Copyright (c) Christian Corsica. All Rights Reserved.

import json

import maya.OpenMaya as om
import pymel.core as pm

from Qt import QtCompat
from piper.ui.widget import manager
from piper.ui.clipper import Clipper
from piper.mayapy.ui.widget import Controller


class MayaClipper(Clipper):

    label = 'Clipper'
    instance = None  # useful to be singleton while window is open
    ui_name = label.replace(' ', '')  # same as label, but without spaces
    create_command = 'import {0}; {0}.show()'.format(__name__)
    closed_command = 'import {0}; {0}.unregister()'.format(__name__)

    def __init__(self, *args, **kwargs):
        super(MayaClipper, self).__init__(*args, **kwargs)
        manager.register(self)
        self.callback = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, self.refresh)
        self.setObjectName(self.__class__.ui_name)
        self.controller = None

    def showInMaya(self):
        """
        Creates the controller to handle Maya integration with this class' widget. This replaces widget.show
        """
        self.controller = Controller(self.__class__.ui_name)

        if self.controller.exists():
            self.controller.restore(self)
        else:
            self.controller.create(self.label, self, ui_script=self.create_command, close_script=self.closed_command)

        self.controller.setVisible(True)

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
        clip_count = 0
        for widget in self.anim_widgets:
            data = widget.getData()

            for animation_name, clip_data in data.items():
                piper_animation = pm.PyNode(animation_name)
                parsed_data = json.dumps(clip_data)
                piper_animation.clipData.set(parsed_data)
                clip_count += len(clip_data)

        pm.displayInfo('Saved {} clips.'.format(str(clip_count)))
        
    def close(self, *args, **kwargs):
        """
        Overriding close method to use the controller class function instead.

        Returns:
            (string): Name of workspace control closed.
        """
        self.controller.close()


def get():
    """
    Gets the instance to the widget since it is meant to be a singleton.

    Returns:
        (MayaClipper): Widget created.
    """
    MayaClipper.instance = MayaClipper() if MayaClipper.instance is None else MayaClipper.instance
    return MayaClipper.instance


def unregister():
    """
    Unregisters widget from the widget manager.
    """
    if MayaClipper.instance is None:
        return

    om.MEventMessage.removeCallback(MayaClipper.instance.callback)
    manager.unregister(MayaClipper.instance)
    QtCompat.delete(MayaClipper.instance)
    MayaClipper.instance = None


def show():
    """
    Convenience method for showing the MayaClipper widget

    Returns:
        (MayaClipper): Widget created.
    """
    instance = get()
    instance.showInMaya()
    return instance
