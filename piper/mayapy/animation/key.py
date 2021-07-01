#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.mayapy.rig.control as control


def getAll(controls=None, attr=None):
    """
    Gets all the keys that all the given controls have.

    Args:
        controls (Iterable): controls to check for keys.

        attr (string): If given, gets only the keys where the given attr is keyed.

    Returns:
        (dictionary): Keyframes as key, controls as values.
    """
    keys = {}

    if not controls:
        controls = control.getAll()

    for ctrl in controls:
        keys_to_get = ctrl.attr(attr) if attr else ctrl
        ctrl_keys = set(pm.keyframe(keys_to_get, q=True))
        for key in ctrl_keys:

            if key not in keys:
                keys[key] = set()

            keys[key].add(ctrl)

    return keys


def toggleStepped():
    """
    Convenience method for toggling between stepped and auto key tangents.
    """
    key_in = pm.keyTangent(q=True, g=True, itt=True)[0]
    key_out = pm.keyTangent(q=True, g=True, ott=True)[0]

    if key_in == 'auto' and key_out == 'auto':
        pm.keyTangent(g=True, itt='clamped')
        pm.keyTangent(g=True, ott='step')
        pm.displayInfo('In stepped key tangents')
    elif key_in == 'clamped' and key_out == 'step':
        pm.keyTangent(g=True, itt='auto')
        pm.keyTangent(g=True, ott='auto')
        pm.displayInfo('In auto key tangents')
    else:
        pm.error('Default in Tangents are not both auto or clamped/stepped')


def deleteDecimals():
    """
    Credit to Alex Tavener: www.alextavener.co.uk
    Deletes any keys that are not on a whole frame on selected curves.
    """
    curves = pm.keyframe(q=True, n=True, sl=1) or []
    for curve in curves:

        keys = pm.keyframe(curve, q=True, tc=1, vc=True) or []
        pm.selectKey(clear=1)

        time = [keys[i][0] for i in range(0, len(keys))]
        [pm.cutKey(time=(time[i], time[i])) for i in range(len(time)) if str(time[i])[-1] != '0']


def roundAll():
    """
    Rounds all keyframes not in whole number frames to their nearest whole frame number value.
    """
    # don't feel like converting this to python right now, so leaving as is.
    command = """// get all selected anim curves or anim curves attached to the selection
string $animCurves[] = `keyframe -q -name`;
for ($animCurve in $animCurves) // browse them
    {
    // get all selected keys at this curve
    float $thisKeys[] = `keyframe -q -sl $animCurve`;
    if (!size($thisKeys)) // if no keys selected get all keys
        $thisKeys = `keyframe -q $animCurve`;
    for ($keys in $thisKeys) // browse the keys
        {
        if (`fmod $keys 1` != 0) // if the keys have decimal places move them to the rounded keytime
            keyframe -e -t $keys -iub true -a -o over -timeChange (floor($keys)) $animCurve;
        }
        }"""
    pm.mel.eval(command)
