#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import json

import pymel.core as pm

import piper_config as pcfg
import piper.mayapy.rig as rig
import piper.mayapy.rig.skin as skin
import piper.mayapy.attribute as attribute


def createHigh(rigs=None):
    """
    References in the high poly version of the mesh. Naming convention is important! See piper configs "high_poly"
    to correctly suffix high poly file and high poly geometry.

    Args:
        rigs (list): Rigs to create high-poly version of mesh.

    Returns:
         (list): Absolute path of references made.
    """
    warnings = []
    piper_rigs = []
    references = {}
    high_references = []
    skeleton_meshes = rig.getSkeletonMeshes(rigs=rigs)

    # get all the data more organized based on what file reference each mesh belongs to
    for mesh, data in skeleton_meshes.items():
        reference = pm.FileReference(namespace=mesh.namespace())

        # no need to operate on meshes that are already high poly
        if reference.namespace.startswith(pcfg.high_poly_namespace):
            continue

        if reference in references:
            references[reference].update({mesh: data})
        else:
            references[reference] = {mesh: data}

    for reference, meshes in references.items():

        deformers = []
        skinned_mesh = None
        should_continue = False
        path, extension = os.path.splitext(reference.path)
        high_absolute = path + pcfg.high_poly_file_suffix + extension
        high_references.append(high_absolute)

        # cannot reference in path that does not exist
        if not os.path.exists(high_absolute):
            text = 'High poly path does not exist! ' + high_absolute
            warnings.append(text)
            pm.warning(text)
            continue

        for i, mesh in enumerate(meshes):

            if i == 0:
                # all meshes in reference should share same skinned mesh
                skinned_mesh = meshes[mesh]['skinned_mesh']
                should_continue = skinned_mesh.wraps.get()  # if there is data in wraps attribute, then high_poly exists

                if should_continue:
                    text = skinned_mesh.name() + ' already has high poly!'
                    warnings.append(text)
                    pm.warning(text)
                    break

                # getting relative path
                root_path = reference.path.split(reference.unresolvedPath())[0]
                high_relative = high_absolute.split(root_path)[-1]

                # reference in high poly, filter by transform, create group, group deformers, and parent group
                nodes = pm.createReference(high_relative, namespace=pcfg.high_poly_namespace, returnNewNodes=True)
                nodes = pm.ls(nodes, type='transform')
                group_name = os.path.basename(path) + pcfg.high_poly_file_suffix + pcfg.group_suffix
                group = pm.PyNode(group_name) if pm.objExists(group_name) else pm.group(name=group_name, em=True)
                deformers.append(group.name())  # deformers will be serialized with json so using group name
                pm.parent(nodes, group)
                pm.parent(group, skinned_mesh)
                attribute.lockAndHideCompound(group)

            # finding the accompanying high poly mesh with a suffix swap
            high_name = pcfg.high_poly_namespace + ':'
            high_name += mesh.name(stripNamespace=True).replace(pcfg.low_poly_suffix, pcfg.high_poly_suffix)

            if not pm.objExists(high_name):
                text = mesh.name() + ' has no high poly equivalent! ' + high_name
                warnings.append(text)
                pm.warning(text)
                continue

            # create proximity wrap
            piper_rig = meshes[mesh]['rig']
            piper_rigs.append(piper_rig)
            high_poly = pm.PyNode(high_name)
            deformer = skin.createProximityWrap(mesh, high_poly)
            deformers.append(deformer)

            piper_rig.highPolyVisibility >> high_poly.visibility

        if should_continue:
            continue

        # write the deformers and group onto the skinned mesh wraps attribute
        deformers_data = json.dumps(deformers)
        skinned_mesh.wraps.set(deformers_data)

    pm.select(piper_rigs)

    # finished referencing high poly, display warnings if any found
    warning_length = len(warnings)
    if warning_length == 0:
        pm.displayInfo('Finished referencing and proximity wrapping high-poly geometry')
    elif warning_length == 1:
        pm.warning('Finished with ONE warning: ' + warnings[0])
    else:
        pm.warning('Finished with MULTIPLE warnings. Please see Script Editor for details.')

    return high_references


def removeHigh(rigs=None, warn=True):
    """
    Removes the high-poly references.

    Args:
        rigs (list): Rigs to remove high-poly from. If None given will use selected or find rigs in scene.

        warn (boolean): If True, will warn user if no high-poly references of given rigs found.

    Returns:
        (list): File references removed.
    """
    references = set()
    skinned_meshes = set()
    skeleton_meshes = rig.getSkeletonMeshes(rigs=rigs)

    for mesh, data in skeleton_meshes.items():
        reference = pm.FileReference(namespace=mesh.namespace())

        if not reference.namespace.startswith(pcfg.high_poly_namespace):
            continue

        references.add(reference)
        pm.parent(mesh, world=True)
        shapes = mesh.getShapes()  # deformed shape is made when creating deformer, must delete
        shapes = [shape for shape in shapes if not shape.isReferenced()]
        pm.delete(shapes)
        skinned_meshes.add(data['skinned_mesh'])

    for skinned_mesh in skinned_meshes:
        to_delete = skinned_mesh.wraps.get()
        to_delete = json.loads(to_delete)
        pm.delete(to_delete[0])  # index 0 is group, rest are proximity deformers that were deleted with deformer shapes
        skinned_mesh.wraps.set('')

    # remove references
    [reference.remove() for reference in references]

    # final display
    if references:
        pm.displayInfo('Removed ' + str(len(references)) + ' high-poly references')
    elif warn:
        pm.warning('No high-poly references found!')

    return references
