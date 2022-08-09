#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue
import piper.core.util as pcu


def welcome():
    """
    Displays the welcome message.
    """
    message = pcu.getWelcomeMessage()
    ue.log(message)
