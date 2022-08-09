#  Copyright (c) Christian Corsica. All Rights Reserved.


import pymel.core as pm

import piper.config as pcfg
import piper.core.util as pcu


def _validateMirrorArg(arg, success):
    """
    Gets the given arg as the mirror if a mirror exists.

    Args:
        arg (any): Can only mirror strings, PyNodes, and lists.

        success (list): List with a single bool in it to let calling function know if mirror was successful or not.

    Returns:
        (any): Given arg mirrored if possible, if not, then original arg.
    """
    if not isinstance(arg, (str, pm.PyNode, list)):
        return arg

    if isinstance(arg, list):
        new_arg = []
        for item in arg:
            new_arg.append(_validateMirrorArg(item, success))

        return new_arg

    if isinstance(arg, pm.PyNode):
        arg = arg.name()

    # swapping out full names
    if pcfg.left_name in arg or pcfg.right_name in arg:
        success[0] = True
        arg = pcu.swapText(arg, pcfg.left_name, pcfg.right_name)

    if arg.endswith((pcfg.left_suffix, pcfg.right_suffix)):
        success[0] = True
        return pcu.swapText(arg)

    if pcfg.left_suffix + '_' in arg or pcfg.right_suffix + '_' in arg:
        success[0] = True
        return pcu.swapText(arg, pcfg.left_suffix + '_', pcfg.right_suffix + '_')

    return arg


def mirror(method, *args, **kwargs):
    """
    Mirrors the given method by swapping the configured sides with each other from all the valid args and kwargs.

    Args:
        method (method): Method to execute AND execute mirrored IF sides are found.

    Returns:
        (any): Results of executing method.
    """
    results = method(*args, **kwargs)

    found_sides = []
    new_args = []
    new_kwargs = {}

    for arg in args:
        found_side = [False]  # found side bool passed within a list to be used as a reference (hack-ish)
        new_arg = _validateMirrorArg(arg, found_side)
        new_arg = new_arg if found_side[0] else arg
        new_args.append(new_arg)
        found_sides.append(found_side[0])

    for key, value in kwargs.items():
        found_side = [False]
        new_value = _validateMirrorArg(value, found_side)
        new_value = new_value if found_side[0] else value
        new_kwargs[key] = new_value
        found_sides.append(found_side[0])

    success = any(found_sides)  # if any sides are found, then mirror

    # run the method with mirrored args and kwargs
    if success:
        method(*new_args, **new_kwargs)

    return results


def _mirror(method):
    """
    Decorator for executing the given method with the mirrored sides suffix as args and kwargs.
    Method must be part of a class, and class must have a self.is_mirroring variable.

    Args:
        method (method): Will execute with sides flipped.
    """
    def wrapper(self, *args, **kwargs):

        if not self.is_mirroring:  # execute function normally if its not mirroring
            return method(self, *args, **kwargs)

        self.is_mirroring = False  # must turn off mirroring so that other functions inside method don't get mirrored.
        args = list(args)
        args.insert(0, self)  # inserting the class' instance into the first arg so decorator works

        results = mirror(method, *args, **kwargs)

        self.is_mirroring = True
        return results

    return wrapper


def _ignoreMirror(method):
    """
    Convenience decorator to mark a function as not mirror-able even is self.is_mirroring is True.
    """
    def wrapper(self, *args, **kwargs):
        is_mirroring = self.is_mirroring
        self.is_mirroring = False
        results = method(self, *args, **kwargs)
        self.is_mirroring = is_mirroring
        return results

    return wrapper
