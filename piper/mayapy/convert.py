#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import math
import pymel.core as pm

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
              'burnt orange': [.85, .6, 0]}

AXES = {'x': (1, 0, 0),
        'y': (0, 1, 0),
        'z': (0, 0, 1),
        'nx': (-1, 0, 0),
        'ny': (0, -1, 0),
        'nz': (0, 0, -1)}

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
    label = JOINT_LABELS.get(name)
    return label if label else JOINT_LABELS[None]


def colorToInt(color):
    """
    Converts given color string to Maya's color index.

    Args:
        color (string): Name of color.

    Returns:
        (int): Index of color.
    """
    color_table = reverse(COLORS_INDEX)
    color_number = color_table.get(color)
    return color_number if color_number else 0


def IntToColor(number):
    """
    Converts a Maya index to a color string.

    Args:
        number (int): Index to convert to color name.

    Returns:
        (string): Name of color associated with given index.
    """
    color = COLORS_INDEX.get(number)
    return color if color else 'default'


def colorToRGB(color):
    """
    Converts given color name to an RGB value.

    Args:
        color (string): Name of color.

    Returns:
        (list): RGB value on respective indices.
    """
    rgb = COLORS_RGB.get(color)
    return rgb if rgb else None


def rgbToColor(rgb):
    """
    Converts given RGB value to a color name.

    Args:
        rgb (list): RGB value on respective list indices.

    Returns:
        (string): Name of given RGB value.
    """
    color_table = reverse(COLORS_RGB)
    color = color_table.get(rgb)
    return color if color else None


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


def axisToTriAxis(axis):
    """
    Converts given axis to a tri axis string list ('x', 'y', 'z').

    Args:
        axis (string or tuple): Axis to convert to tri axis.

    Returns:
        (list): Three strings of 'x', 'y', and 'z' in order depending on given axis.
    """
    return TRIAXES[axis]


def toVector(transform, invalid_zero=False, error=False):
    """
    Converts given transform to a PyMel Vector.

    Args:
        transform (Any): Node or list to convert to Vector.

        invalid_zero (boolean): If True and given transform is not a valid type, will return a zero Vector.

        error (boolean): If given transform is not a valid type and given invalid_zero is False, will return error.

    Returns:
        (pm.dt.Vector): Vector of given transform.
    """
    if isinstance(transform, (pm.nodetypes.Transform, str)):
        location = pm.dt.Vector(pm.xform(transform, q=True, ws=True, rp=True))
    elif isinstance(transform, (list, tuple)):
        location = pm.dt.Vector(transform)
    elif isinstance(transform, pm.dt.Vector):
        location = transform
    else:  # if we cant convert, return zero or error or pass and return given location
        if invalid_zero:
            location = pm.dt.Vector((0, 0, 0))
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
