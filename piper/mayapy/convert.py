#  Copyright (c) Christian Corsica. All Rights Reserved.

import math

import pymel.core as pm
import piper.config.maya as mcfg


COLORS_INDEX = {0: 'default',
                1: 'black',
                2: 'dark grey',
                3: 'light grey',
                4: 'dark red',
                5: 'dark blue',
                6: 'blue',
                7: 'bright green',
                8: 'dark purple',
                9: 'pink',
                10: 'dark orange',
                11: 'brown',
                12: 'burnt orange',
                13: 'red',
                14: 'green',
                15: 'sky blue',
                16: 'white',
                17: 'yellow',
                18: 'light blue',
                19: 'light green',
                20: 'pink',
                21: 'salmon',
                22: 'light yellow',
                23: 'green',
                24: 'light brown',
                25: 'mustard',
                26: 'grass green',
                27: 'tree green',
                28: 'cyan',
                29: 'baby blue',
                30: 'purple',
                31: 'magenta'}

COLORS_RGB = {'cyan': [0, 1, 1],
              'pink': [1, 0, 1],
              'dark red': [.7, 0, 0],
              'dark green': [0, .7, 0],
              'burnt orange': [.85, .6, 0],
              'green': [0, 1, 0],
              'yellow': [1, 1, 0],
              'blue': [0, 0, 1],
              'red': [1, 0, 0],
              'pastel green': [.3, .5, .3],
              'pastel red': [.66, .37, .37],
              'pastel blue': [.28, .28, .64],
              'pastel yellow': [.7, .7, .33],
              'muddy red': [.5, .3, .3]}

AXES = {'x': (1, 0, 0),
        'y': (0, 1, 0),
        'z': (0, 0, 1),
        'nx': (-1, 0, 0),
        'ny': (0, -1, 0),
        'nz': (0, 0, -1)}

INDEXED_AXES = {'x': 0,
                'y': 1,
                'z': 2}

TRIAXES = {'x': ['x', 'y', 'z'],
           'y': ['y', 'x', 'z'],
           'z': ['z', 'x', 'y'],
           'nx': ['x', 'y', 'z'],
           'ny': ['y', 'x', 'z'],
           'nz': ['z', 'x', 'y'],
           (1, 0, 0): ['x', 'y', 'z'],
           (0, 1, 0): ['y', 'x', 'z'],
           (0, 0, 1): ['z', 'x', 'y'],
           (-1, 0, 0): ['x', 'y', 'z'],
           (0, -1, 0): ['y', 'x', 'z'],
           (0, 0, -1): ['z', 'x', 'y']}

JOINT_LABELS = {None: 0,
                'root': 1,
                'thigh': 2,
                'calf': 3,
                'foot': 4,
                'ball': 5,
                'spine': 6,
                'neck': 7,
                'head': 8,
                'clavicle': 9,
                'upperarm': 10,
                'lowerarm': 11,
                'hand': 12,
                'other': 18}


def reverse(dictionary):
    """
    Convenience method for reversing key/values in dictionary.

    Args:
        dictionary (dict): Dictionary to reverse key/value pairs.

    Returns:
        (dictionary): Reversed dict.
    """
    return {b: a for a, b in dictionary.items()}


def jointNameToLabel(name):
    """
    Get the label int associated with the given joint name.

    Args:
        name (string): Name of joint.

    Returns:
        (int)
    """
    return JOINT_LABELS.get(name, 0)


def colorToInt(color):
    """
    Converts given color string to Maya's color index.

    Args:
        color (string): Name of color.

    Returns:
        (int): Index of color.
    """
    color_table = reverse(COLORS_INDEX)
    return color_table.get(color, 0)


def IntToColor(number):
    """
    Converts a Maya index to a color string.

    Args:
        number (int): Index to convert to color name.

    Returns:
        (string): Name of color associated with given index.
    """
    return COLORS_INDEX.get(number, 'default')


def colorToRGB(color):
    """
    Converts given color name to an RGB value.

    Args:
        color (string): Name of color.

    Returns:
        (list): RGB value on respective indices.
    """
    return COLORS_RGB.get(color, None)


def rgbToColor(rgb):
    """
    Converts given RGB value to a color name.

    Args:
        rgb (list): RGB value on respective list indices.

    Returns:
        (string): Name of given RGB value.
    """
    color_table = reverse(COLORS_RGB)
    return color_table.get(rgb, None)


def axisToString(vector, absolute=False):
    """
    Converts given vector list to the associated letter direction.

    Args:
        vector (tuple): Unit vector pointing in an axis.

        absolute (boolean): If True, will return positive axis only.

    Returns:
        (string): Name of axis of given vector. If negative, vector will start with "n".
    """
    axis_table = reverse(AXES)
    axis = axis_table[vector]
    return axis.lstrip('n') if absolute else axis


def axisToVector(axis, absolute=False):
    """
    Converts given axis string to a vector list.

    Args:
        axis (string): Name of vector to convert to a digit list.

        absolute (boolean): If True, will return positive axis only.

    Returns:
        (list): Unit vector in direction of given axis name.
    """
    axis = axis.lstrip('n') if absolute else axis
    return AXES[axis]


def axisToTriAxis(axis, absolute=False):
    """
    Converts given axis to a tri axis string list ('x', 'y', 'z').

    Args:
        axis (string or tuple): Axis to convert to tri axis.

        absolute (boolean): If True, will return positive axis only.

    Returns:
        (list): Three strings of 'x', 'y', and 'z' in order depending on given axis.
    """
    if absolute:
        axis = axis.lstrip('n')

    return TRIAXES[axis]


def axisToIndex(axis):
    """
    Converts the given axis to an index position.

    Args:
        axis (string): Axis to convert to int as index position.

    Returns:
        (int): Index of axis.
    """
    return INDEXED_AXES[axis]


def toVector(transform, invalid_default=None, error=False):
    """
    Converts given transform to a PyMel Vector.

    Args:
        transform (Any): Node or list to convert to Vector.

        invalid_default (any): If True and given transform is not a valid type, return a zero Vector or given vector.

        error (boolean): If given transform is not a valid type and given invalid_zero is False, will return error.

    Returns:
        (pm.dt.Vector): Vector of given transform.
    """
    if isinstance(transform, str):
        if transform in AXES:
            location = pm.dt.Vector(axisToVector(transform))
        else:
            location = pm.dt.Vector(pm.xform(transform, q=True, ws=True, rp=True))

    elif isinstance(transform, pm.nodetypes.Transform):
        location = pm.dt.Vector(pm.xform(transform, q=True, ws=True, rp=True))

    elif isinstance(transform, (list, tuple, pm.dt.Point)):
        location = pm.dt.Vector(transform)

    elif isinstance(transform, pm.dt.Vector):
        location = transform

    else:  # if we cant convert, return zero or error or pass and return given location
        if invalid_default:
            vector = (0, 0, 0) if invalid_default is True else invalid_default
            location = pm.dt.Vector(vector)
        elif error:
            location = None
            pm.error(str(type(transform)) + ' is not a valid type to convert to Vector!')
        else:
            location = transform

    return location


def toDegrees(transform):
    """
    Converts given transform to a rotation in degrees.

    Args:
        transform (pm.dt.Matrix, pm.dt.Quaternion, pm.dt.EulerRotation): Transform to convert to degrees.

    Returns:
        (list): Angle values of given transform.
    """
    if isinstance(transform, pm.dt.Matrix):
        rotation = transform.rotate.asEulerRotation()
    elif isinstance(transform, pm.dt.Quaternion):
        rotation = transform.asEulerRotation()
    elif isinstance(transform, pm.dt.EulerRotation):
        rotation = transform
    else:
        raise TypeError(str(type(transform)) + ' is not a valid type to convert to EulerRotation!')

    return [math.degrees(angle) for angle in rotation]


def toBind(node, fail_display=None, return_node=False):
    """
    Converts the given node to its bind namespace equivalent.

    Args:
        node (pm.nodetypes.DependNode):

        fail_display (method): How to display failure of finding bind node.

        return_node (boolean): If True, will return the given node if bind conversion fails.

    Returns:
        node (pm.nodetypes.DependNode): Node with bind namespace.
    """
    bind_name = node.name().replace(mcfg.skeleton_namespace + ':', mcfg.bind_namespace + ':')

    if bind_name.startswith(mcfg.fk_prefix):
        bind_name = bind_name.split(mcfg.fk_prefix)[-1]
    elif bind_name.startswith(mcfg.ik_prefix):
        bind_name = bind_name.split(mcfg.ik_prefix)[-1]

    if not bind_name.startswith(mcfg.bind_namespace):
        bind_name = mcfg.bind_namespace + ':' + bind_name

    if bind_name.endswith(mcfg.control_suffix):
        bind_name = bind_name.split(mcfg.control_suffix)[0]

    if not pm.objExists(bind_name) and fail_display:
        fail_display(bind_name + ' does not exist!')
        return node if return_node else None

    return pm.PyNode(bind_name)


def toPythonCommand(method):
    """
    Converts the given method to a python command string that maya's MEL can use.

    Args:
        method (method): Method to convert to a python command string.

    Returns:
        (string): MEL command calling given python method.
    """
    module = method.__module__
    full_method = module + '.' + method.__name__
    return 'python("import {module}; {full_method}()")'.format(module=module, full_method=full_method)
