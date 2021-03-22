#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import math
import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.convert as convert


def zeroOut(transform):
    """
    Zeroes out the given transform to zero translate, rotate, and one to scale.

    Args:
        transform (pm.nodetypes.Transform): Transform to zero out.
    """
    pm.xform(transform, absolute=True, t=[0, 0, 0], ro=[0, 0, 0], s=[1, 1, 1])


def getDistance(start, end):
    """
    Gets the distance between given start and end.

    Args:
        start (Any): Start point to get distance to end.

        end (Any): End point to get distance from end.

    Returns:
        (float): Distance from start point to end point.
    """
    start_location = convert.toVector(start)
    end_location = convert.toVector(end)

    return (end_location - start_location).length()


def getDirection(start, end):
    """
    Gets the vector direction aiming between the given start and end.

    Args:
        start (Any): Transform or vector where direction should start from.

        end (Any): Transform or vector where direction should end/aim at.

    Returns:
        (pm.dt.Vector): Direction aiming from start to end normalized.
    """
    start_location = convert.toVector(start)
    end_location = convert.toVector(end)
    aim_direction = (end_location - start_location).normal()
    return aim_direction


def getMatrixFromVector(forward, up=None, forward_axis='z', location=None):
    """
    Creates a rotation from given forward direction and up direction. Which is then used to calculate a matrix.

    Args:
        forward (Any): Vector that faces forward.

        up (Any): Vector that faces up. If none given will use scene up axis.

        forward_axis (string): What local vector will face forward in the matrix.

        location (Any): Where the matrix should be in world space. If none given, will be at origin.

    Returns:
        (pm.nodetypes.Matrix): Matrix calculated from given forward vector.
    """
    if isinstance(up, (list, tuple)):
        up = pm.dt.Vector(up)
    elif isinstance(up, str):
        up = pm.dt.Vector(convert.axisToVector(up))
    elif isinstance(up, pm.dt.Vector):
        pass
    else:
        up = pm.upAxis(axis=True, q=True)
        up = pm.dt.Vector(convert.axisToVector(up))

    right = forward.cross(up).normal()
    up = right.cross(forward).normal()
    coordinates = []

    if forward_axis == 'x':
        coordinates = [forward.get(), up.get(), right.get()]
    elif forward_axis == 'y':
        coordinates = [up.get(), forward.get(), right.get()]
    elif forward_axis == 'z':
        coordinates = [(right * -1).get(), up.get(), forward.get()]

    location = convert.toVector(location, invalid_zero=True)
    coordinates.append(location)
    return pm.dt.Matrix(*coordinates)


def getAimRotation(start, end):
    """
    Gets the rotation values to aim given start vector to given end vector.

    Args:
        start (Any): Point that needs to aim to end.

        end (Any): Point that start needs to aim at.

    Returns:
        (list): Rotation values to aim start towards end.
    """
    forward = getDirection(start, end)
    matrix = getMatrixFromVector(forward, up=None)
    euler_rotation = matrix.rotate.asEulerRotation()

    if isinstance(start, pm.nodetypes.Transform) and start.hasAttr('rotateOrder'):
        euler_rotation = euler_rotation.reorderIt(start.rotateOrder.get())

    rotation = [math.degrees(angle) for angle in (euler_rotation.x, euler_rotation.y, euler_rotation.z)]
    return rotation


def getOrientAxis(start, target):
    """
    Gets the closest axis object is using to pointing to target.
    Thanks to Charles Wardlaw for helping script it.

    Args:
        start (PyNode): transform object to find axis of.

        target (string or PyNode): transform object that axis is pointing to.

    Returns:
        (tuple): Closest axis
    """
    closest_axis = None
    closest_dot_result = 0.0

    aim_direction = getDirection(start, target)
    world_matrix = start.worldMatrix.get()

    for axis in pcfg.axes:
        axis_vector = pm.dt.Vector(axis)  # the world axis
        axis_vector = axis_vector * world_matrix  # turning the world axis to local start object axis
        dot = axis_vector.dot(aim_direction)  # dot product tells us how aligned the axis is with the aim direction
        if dot > closest_dot_result:
            closest_dot_result = dot
            closest_axis = axis

    return closest_axis
