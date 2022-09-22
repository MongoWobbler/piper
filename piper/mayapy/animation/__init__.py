#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import copy

import pymel.core as pm

import piper.config.maya as mcfg
import piper.mayapy.pipe.paths as paths
import piper.mayapy.rig.xform as xform
import piper.mayapy.rig.control as control
import piper.mayapy.selection as selection

from . import key
from . import resolution


def referenceRig(path):
    """
    Creates a reference to the given rig path.
    If rig or rig component selected, will replace the rig's skinned mesh with the given rig path's skinned mesh.

    Args:
        path (string): Rig path to reference.

    Returns:
        (pm.nodetypes.FileReference or list): Reference(s) created.
    """
    # looks for rigs we might have selected
    rigs = selection.get('piperRig', search=False)

    if not rigs:
        return pm.createReference(path, namespace=mcfg.rig_namespace)  # create a new reference

    references = []
    high_poly = resolution.removeHigh(rigs=rigs, warn=False)
    new_character = os.path.basename(os.path.abspath(path + '/../..'))

    # swap out references with the skinned mesh file in the given path
    for rig in rigs:
        rig_namespace = rig.namespace()
        skins_grp = rig_namespace + mcfg.skinned_mesh_grp
        skins_grp = pm.PyNode(skins_grp) if pm.objExists(skins_grp) else pm.group(n=skins_grp, em=True, p=rig)

        for skinned_mesh in rig.getChildren(ad=True, type='piperSkinnedMesh'):
            skinned_mesh_namespace = skinned_mesh.namespace()
            old_reference = pm.FileReference(namespace=skinned_mesh_namespace).parent()
            old_character = os.path.basename(os.path.abspath(old_reference.path + '/../..'))
            new_path = old_reference.path.replace(old_character, new_character)

            if not os.path.exists(new_path):
                pm.warning(new_path + ' does not exist! Skipping reference swapping')
                continue

            references.append(new_path)
            new_relative_path = paths.getRelativeArt(new_path)
            nodes = old_reference.replaceWith(new_relative_path, returnNewNodes=True)  # this is where the swap happens
            new_skinned_meshes = pm.ls(nodes, type='piperSkinnedMesh')

            try:
                # catch a bad parent, usually happens when re-referencing original rig skinned mesh reference
                # Warning: Referenced objects parented to referenced objects may not be reparented
                pm.parent(new_skinned_meshes, skins_grp)
            except RuntimeError:
                pass

            if mcfg.bind_namespace in skinned_mesh_namespace:
                [new_skinned_mesh.visibility.set(False) for new_skinned_mesh in new_skinned_meshes]

    if high_poly:
        resolution.createHigh(rigs=rigs)

    return references


def _validateScale(transform, keyframe, failed, display=pm.warning):
    """
    Validates the scale of the given transform on the given key and adds it to a dictionary with "scale" as key, and
    a set as its value.

    Args:
        transform (pm.nodetypes.Transform): Transform to validate uniform scale.

        keyframe (float or int): Keyframe to check for uniform scale.

        failed (dictionary): Must have a "scale" key with a set as its value to add possible transform to.

        display (method): How to display a transform that is not uniformly scaled.

    Returns:
        (boolean): True if transform is uniformly scaled.
    """
    if xform.isUniformlyScaled(transform):
        return True

    failed['scale'].add(transform)
    text = '{0} has non-uniform scale on frame {1}'
    display(text.format(transform.name(), str(keyframe)))
    return False


def isUniformlyScaled(transform, start=None, end=None, resume=True):
    """
    Gets whether the given transform is uniformly scaled or not across all keyframes.

    Args:
        transform (pm.nodetypes.Transform): Transform to check for uniform scale.

        start (int): Frame to start checking for uniform scale.

        end (int): Frame  to end check for uniform scale.

        resume(boolean): If True, will resume the refreshing the dependency graph when finished with checking scale.

    Returns:
        (boolean): True if uniformly scaled across all keyframes.
    """
    pm.refresh(suspend=True)
    is_uniformly_scaled = True
    current_time = pm.currentTime()

    if start is None:
        start = int(pm.playbackOptions(q=True, min=True))

    if end is None:
        end = int(pm.playbackOptions(q=True, max=True))

    for keyframe in range(start, end):
        pm.currentTime(keyframe)

        if not xform.isUniformlyScaled(transform):
            is_uniformly_scaled = False
            break

    pm.currentTime(current_time)
    pm.refresh(suspend=not resume)
    return is_uniformly_scaled


def health(namespaces=None, resume=True, scale_display=pm.warning):
    """
    Performs a health check on the controls to catch anything that might cause errors further down the pipe.

    Args:
        namespaces (Iterable): Namespaces to get controls from.

        resume(boolean): If True, will resume the refreshing the dependency graph when finished with health check.

        scale_display (method): How to display any non-uniform scale.

    Returns:
        (dictionary): Error causing nodes.
    """
    failed_default = {'scale': set()}
    failed = copy.deepcopy(failed_default)
    pm.refresh(suspend=True)

    current_time = pm.currentTime()
    controls = control.getAll(namespaces)
    keys = key.getAll(controls, 's')
    keys[0.0] = controls

    for keyframe, scaled_controls in keys.items():
        pm.currentTime(keyframe)
        [_validateScale(ctrl, keyframe, failed, scale_display) for ctrl in scaled_controls]

    pm.currentTime(current_time)
    pm.refresh(suspend=not resume)

    errors = {} if failed == failed_default else failed
    pm.warning('Errors found in animation! Open Script Editor') if errors else pm.displayInfo('Animation is happy')
    return errors
