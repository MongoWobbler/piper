#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper_config as pcfg
import piper.mayapy.rig.core as rig


def _connect(transform, target, space):
    """
    Convenience method for connecting the use transforms attributes from the piper space to matrix blend target.

    Args:
        transform (pm.nodetypes.Transform): Transform connect use transform from onto target.

        target (pm.Attribute): Attribute with use transform attributes.

        space (pm.Attribute): Space attribute that will drive the target weight.
    """
    space >> target.weight
    transform.attr(pcfg.space_use_translate) >> target.useTranslate
    transform.attr(pcfg.space_use_rotate) >> target.useRotate
    transform.attr(pcfg.space_use_scale) >> target.useScale


def getAll(transform):
    """
    Gets all the piper made spaces. Uses names stored in a string attribute to get these spaces.
    Will return empty list if no spaces attributes found.

    Args:
        transform (pm.nodetypes.Transform): Transform to get spaces from.

    Returns:
        (list): All space attributes given transform has, if any.
    """
    attributes = None

    if transform.hasAttr(pcfg.spaces_name):
        attributes = transform.attr(pcfg.spaces_name).get()

    return attributes.split(':') if attributes else []


def create(spaces, transform):
    """
    Creates the given spaces on the given transform.

    Args:
        spaces (list): A bunch of pm.nodetypes.Transform(s) that will drive the given transform.

        transform (pm.nodetypes.Transform): Transform to have ability to switch between given spaces.

    Returns:
          (list): Name of space attribute(s) made.
    """
    space_attributes = []
    parent = transform.getParent()
    transform_name = transform.nodeName()
    matrix_blend = transform.offsetParentMatrix.listConnections()
    has_spaces = matrix_blend and transform.hasAttr(pcfg.space_world_name)

    if has_spaces:
        # define matrix blend from the matrix plug
        matrix_blend = matrix_blend[0]

        if matrix_blend.nodeType() != 'blendMatrix':
            pm.error(transform.nodeName() + ' has wrong type: ' + matrix_blend.nodeName() + ' in offsetParentMatrix')
    else:
        # create and hook up matrix blend
        matrix_blend = pm.createNode('blendMatrix', n=transform_name + pcfg.space_blend_matrix_suffix)
        target = matrix_blend.attr('target[0]')
        offset_matrix = transform.offsetParentMatrix.get()
        matrix_blend.inputMatrix.set(offset_matrix)
        matrix_blend.outputMatrix >> transform.offsetParentMatrix

        # counter drive parent to create a world space
        if parent:
            parent.inverseMatrix >> target.targetMatrix

        # create attributes on transform and add world space by default
        rig.addSeparator(transform)
        transform.addAttr(pcfg.space_use_translate, at='bool', dv=1, k=True)
        transform.addAttr(pcfg.space_use_rotate, at='bool', dv=1, k=True)
        transform.addAttr(pcfg.space_use_scale, at='bool', dv=1, k=True)
        transform.addAttr(pcfg.spaces_name, dt='string', k=False, h=True, s=True)
        transform.addAttr(pcfg.space_world_name, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)
        _connect(transform, target, transform.attr(pcfg.space_world_name))
        space_attributes.append(pcfg.space_world_name)

    for space in spaces:
        space_name = space.nodeName()
        space_attribute = space_name + pcfg.space_suffix
        transform.addAttr(space_attribute, k=True, dv=0, hsx=True, hsn=True, smn=0, smx=1)
        target = rig.getNextAvailableTarget(matrix_blend, 1)

        # make multiply matrix node and hook it up
        offset = transform.parentMatrix.get() * space.worldInverseMatrix.get()
        multiply = pm.createNode('multMatrix', n='space_{}_To_{}_multMatrix'.format(transform_name, space_name))
        multiply.matrixIn[0].set(offset)
        space.worldMatrix >> multiply.matrixIn[1]

        # counter drive parent
        if parent:
            parent.worldInverseMatrix >> multiply.matrixIn[2]

        multiply.matrixSum >> target.targetMatrix
        _connect(transform, target, transform.attr(space_attribute))
        space_attributes.append(space_attribute)

    # update the spaces attribute
    old_spaces = getAll(transform)
    updated_spaces = old_spaces + space_attributes
    transform.attr(pcfg.spaces_name).set(':'.join(updated_spaces))
    return space_attributes


def switch(transform, new_space, t=True, r=True, s=True):
    """
    Switches the given transform to the given new_space while maintaining the world transform of the given transform.
    Choose to switch driving translate, rotate, or scale attributes on or off too.

    Args:
        transform (pm.nodetypes.Transform):

        new_space (string): Name of space attribute to switch to.

        t (boolean): If True, space will affect translate values.

        r (boolean): If True, space will affect rotate values.

        s (boolean): If True, space will affect scale values.
    """
    position = transform.worldMatrix.get()
    transform.useTranslate.set(t)
    transform.useRotate.set(r)
    transform.useScale.set(s)
    spaces = getAll(transform)
    [transform.attr(space_attribute).set(0) for space_attribute in spaces]
    transform.attr(new_space).set(1)
    pm.xform(transform, ws=True, m=position)
