#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue
import piper.core


def isHeadless():
    """
    Gets whether unreal is running headless or not by checking if we can find the main menu in the level editor.

    Returns:
        (bool): True if unreal is running headless.
    """
    tool = ue.ToolMenus.get()
    return not bool(tool.find_menu(ue.Name('LevelEditor.MainMenu')))


def welcome():
    """
    Displays the welcome message.
    """
    message = piper.core.getWelcomeMessage()
    ue.log(message)
