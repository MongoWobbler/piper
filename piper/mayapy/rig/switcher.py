#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.attribute as attribute

from . import curve
from . import control


def get(transform, error=True, name=False):
    """
    Gets the switcher if the given transform has an fk_ik attribute.

    Args:
        transform (pm.nodetypes.Transform): Transform to get switcher control of.

        error (boolean): If True, will raise error if given transform is not connected to a switcher.

        name (boolean): If True, will return name of switcher.

    Returns:
        (pm.nodetypes.Transform or String): Switcher control that holds real fk_ik attribute.
    """
    if transform.hasAttr(pcfg.proxy_fk_ik):
        real_switcher = transform.attr(pcfg.proxy_fk_ik).connections()

        if not real_switcher:
            pm.error(transform.nodeName() + ' has proxy attribute but is not connected!')

        return real_switcher[0].name() if name else real_switcher[0]

    elif transform.hasAttr(pcfg.fk_ik_attribute):
        return transform.name() if name else transform

    elif error:
        pm.error(transform.nodeName() + ' is not connected to a switcher!')

    else:
        return None


def create(driver, name=''):
    """
    Creates the switcher control in charge of switching between FK and IK chains.

    Args:
        driver (pm.nodetypes.Transform): Transform where switcher will be created and will drive switcher's transform.

        name (string): Prefix name for switcher control.

    Returns:
        (pm.nodetypes.Transform): Switcher control created.
    """
    name = name + pcfg.switcher_suffix
    switcher_control = control.create(driver, name=name, shape=curve.cube, scale=0.5)
    attribute.addSeparator(switcher_control)
    attribute.nonKeyableCompound(switcher_control)
    switcher_control.addAttr(pcfg.fk_ik_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)
    switcher_control.addAttr(pcfg.switcher_transforms, dt='string', k=False, h=True, s=True)
    switcher_control.addAttr(pcfg.switcher_fk, dt='string', k=False, h=True, s=True)
    switcher_control.addAttr(pcfg.switcher_ik, dt='string', k=False, h=True, s=True)
    switcher_control.addAttr(pcfg.switcher_reverses, dt='string', k=False, h=True, s=True)
    driver.worldMatrix >> switcher_control.offsetParentMatrix

    return switcher_control


def getData(switcher_attribute, cast=False):
    """
    Gets the data stored in the given attribute.

    Args:
        switcher_attribute (pm.general.Attribute): The name of the attribute to get the data from.

        cast (boolean): If True, will cast each value of the attribute found into a PyNode.

    Returns:
        (list): All nodes held in the attribute string.
    """
    data = switcher_attribute.get()

    if not data:
        return []

    data = data.split(', ')
    namespace = switcher_attribute.namespace()
    return [pm.PyNode(namespace + node) for node in data] if cast else data


def getAllData(transform):
    """
    Check whether given node has all needed attributes to perform a switch, raise error if it does not.

    Args:
        transform (pm.nodetypes.Transform): Switcher control with attributes that hold all the FK IK information.

    Returns:
        (list): Switcher, Transforms, FK controls, IK controls, reverses and fk_ik attribute value.
        Transforms and controls are in order.
    """
    switcher = get(transform)
    attribute.exists(switcher, pcfg.switcher_attributes, error=True)
    fk_ik_value = switcher.attr(pcfg.fk_ik_attribute).get()
    attributes = [getData(switcher.attr(attr), cast=True) for attr in pcfg.switcher_attributes[:-1]]
    attributes.insert(0, switcher)
    attributes.append(fk_ik_value)

    return attributes


def addData(switcher_attribute, addition, names=False):
    """
    Adds string data to the given switcher_attribute.

    Args:
        switcher_attribute (pm.general.Attribute): Attribute to store data in.

        addition (list): Data to add.

        names (boolean): If True, will convert given addition to strings.
    """
    if names:
        addition = [node.name() for node in addition]

    data = getData(switcher_attribute)
    data = data + addition
    switcher_attribute.set(', '.join(data))
