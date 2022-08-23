#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm


def evaluateGraph():
    """
    Forces the Maya's graph to evaluate by refreshing the UI and changing the current time. Useful for when scripts
    run differently when you run them piece by piece, and when you run them all at once since some nodes may need
    to be evaluated before other nodes can be created and plugged in.
    """
    pm.refresh(force=True)
    current_time = pm.currentTime()
    pm.currentTime(current_time, update=True)


def getIncrementalNodes(name, i='01', namespace=''):
    """
    Gets all the nodes with incrementing given i as part of their name. Must have "{}" to format given i.

    Args:
        name (string): Name of node with "{}" to replace for given i and to search for existence.

        i (string): Digit format to incremental nodes to find with given i as the starting digit.

        namespace (string): Namespace to append to name we are searching for.

    Returns:
        (list): Nodes found with given format.
    """
    nodes = []
    node_to_validate = namespace + name.format(i)

    while pm.objExists(node_to_validate):
        nodes.append(node_to_validate)
        i = '{:0>{}}'.format(str(int(i) + 1), len(i))
        node_to_validate = namespace + name.format(i)

    return nodes


def getConstrainedTargets(driver, constraint_type='parentConstraint'):
    """
    Gets all the transforms the given driver is driving through the giving constraint type.

    Args:
        driver (PyNode): The transform that is driving the other transform(s) through a constraint.

        constraint_type (string): The type of constraint to look for.
        Normally "parentConstraint", "pointConstraint", "orientConstraint", or "scaleConstraint".

    Returns:
        (set): Transform(s) being driven by given driver through given constraint type.
    """
    # Using sets to remove duplicates from list connections because Maya
    constraints = set(driver.listConnections(type=constraint_type))
    targets = set()
    for constraint in constraints:
        targets.update(set(constraint.connections(source=False, destination=True, et=True, type='transform')))

    return targets
