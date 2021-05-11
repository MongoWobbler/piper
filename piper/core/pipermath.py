#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.
#
#  Some functions come from:
#  https://stackoverflow.com/questions/17915475/how-may-i-project-vectors-onto-a-plane-defined-by-its-orthogonal-vector-in-pytho

import math


def dotProduct(x, y):
    """
    Gets the dot product between the two given vectors.

    Args:
        x (list): First vector.

        y (list): Second vector.

    Returns:
        (float): Dot product result, scalar.
    """
    return sum([x[i] * y[i] for i in range(len(x))])


def magnitude(x):
    """
    Gets the length/norm/magnitude of the given vector

    Args:
        x (list): Vector to get magnitude of.

    Returns:
        (float): Magnitude of given vector
    """
    return math.sqrt(dotProduct(x, x))


def normalize(x):
    """
    Normalizes the given vector to turn it into a unit vector.

    Args:
        x (list): Vector to normalize.

    Returns:
        (list): Vector normalized.
    """
    return [x[i] / magnitude(x) for i in range(len(x))]


def projectOntoPlane(x, n):
    """
    Projects the given x vector onto the given n plane which is defined by its orthogonal vector.

    Args:
        x (list): Vector to to project onto n.

        n (list): Vector that represents its orthogonal plane.

    Returns:
        (list): Vector x projected onto plane n.
    """
    d = dotProduct(x, n) / magnitude(n)
    p = [d * normalize(n)[i] for i in range(len(n))]
    return [x[i] - p[i] for i in range(len(x))]
