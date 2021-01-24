#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.
# Thanks to Jennifer Conley for figuring out all the coordinates to create these shapes.

import pymel.core as pm
import piper.mayapy.convert as convert


def color(control, color_name):
    """
    Sets color of all the shapes that a given control has. See piper/mayapy/convert for all available colors.

    Args:
        control (pm.nodetypes.Transform): Transform that holds shapes as children.

        color_name (string): Name of color to change given control to.
    """
    shapes = control.getShapes()

    if not shapes:
        return

    for shape in shapes:
        shape.overrideEnabled.set(True)
        shape.overrideColor.set(convert.colorToInt(color_name))


def circle(*args, **kwargs):
    """
    Creates circle shape.

    Returns:
        (pm.nodetypes.Transform): Transform of circle shape created.
    """
    return pm.circle(nr=[0, 1, 0], *args, **kwargs)[0]


def triangle(*args, **kwargs):
    """
    Creates triangle shape.

    Returns:
        (pm.nodetypes.Transform): Transform of triangle shape created.
    """
    return pm.curve(d=1, p=[(-1, 0, 1), (1, 0, 1), (0, 0, -1), (-1, 0, 1)], k=[0, 1, 2, 3, ], *args, **kwargs)


def square(*args, **kwargs):
    """
    Creates square shape.

    Returns:
        (pm.nodetypes.Transform): Transform of square shape created.
    """
    return pm.curve(d=1, p=[(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1), (-1, 0, -1)],
                    k=[0, 1, 2, 3, 4], *args, **kwargs)


def moveAll(*args, **kwargs):
    """
    Creates a circle with arrows at each end.

    Returns:
        (pm.nodetypes.Transform): Transform of the move all shape created.
    """
    control = pm.circle(nr=[0, 1, 0], *args, **kwargs)[0]

    arrow_list = [pm.curve(d=1, p=[(1.75625, 0, 0.115973), (1.75625, 0, -0.170979), (2.114939, 0, -0.170979),
                                   (2.114939, 0, -0.314454), (2.473628, 0, -0.0275029), (2.114939, 0, 0.259448),
                                   (2.114939, 0, 0.115973), (1.75625, 0, 0.115973)], k=[0, 1, 2, 3, 4, 5, 6, 7]),
                  pm.curve(d=1, p=[(0.143476, 0, -1.783753), (0.143476, 0, -2.142442), (0.286951, 0, -2.142442),
                                   (0, 0, -2.501131), (-0.286951, 0, -2.142442), (-0.143476, 0, -2.142442),
                                   (-0.143476, 0, -1.783753), (0.143476, 0, -1.783753)],
                           k=[0, 1, 2, 3, 4, 5, 6, 7]),
                  pm.curve(d=1, p=[(-1.75625, 0, -0.170979), (-2.114939, 0, -0.170979), (-2.114939, 0, -0.314454),
                                   (-2.473628, 0, -0.0275029), (-2.114939, 0, 0.259448), (-2.114939, 0, 0.115973),
                                   (-1.75625, 0, 0.115973), (-1.75625, 0, -0.170979)], k=[0, 1, 2, 3, 4, 5, 6, 7]),
                  pm.curve(d=1, p=[(-0.143476, 0, 1.728747), (-0.143476, 0, 2.087436), (-0.286951, 0, 2.087436),
                                   (0, 0, 2.446125), (0.286951, 0, 2.087436), (0.143476, 0, 2.087436),
                                   (0.143476, 0, 1.728747), (-0.143476, 0, 1.728747)], k=[0, 1, 2, 3, 4, 5, 6, 7])]

    pm.select(arrow_list)
    pm.pickWalk(d='Down')
    pm.select(control, tgl=True)
    pm.parent(r=True, s=True)
    pm.delete(arrow_list)
    pm.xform(control, cp=True)
    return control


def sun(*args, **kwargs):
    """
    Creates sun-like shape, more like a soft gear shape.

    Returns:
        (pm.nodetypes.Transform): Transform of sun shape created.
    """
    control = pm.circle(s=16, nr=[0, 1, 0], *args, **kwargs)[0]
    pm.select((control + '.cv[1]'), (control + '.cv[3]'), (control + '.cv[5]'), (control + '.cv[7]'),
              (control + '.cv[9]'), (control + '.cv[11]'), (control + '.cv[13]'), (control + '.cv[15]'),
              (control + '.cv[17]'), (control + '.cv[19]'), r=True)
    pm.scale(0.3, 0.3, 0.3, p=[0, 0, 0], r=True)
    pm.makeIdentity(control, apply=True, t=1, r=1, s=1, n=0)
    pm.xform(control, cp=True)
    return control


def pick(*args, **kwargs):
    """
    Creates a shape that looks like a guitar pick. Pointy end at the origin

    Returns:
        (pm.nodetypes.Transform): Transform of pick shape created.
    """
    control = pm.circle(nr=[0, 1, 0], *args, **kwargs)[0]
    pm.move(control + '.cv[5]', (0, 0, -1.108194), r=True)
    pm.move(control + '.cv[1]', (0, 0, 1.108194), r=True)
    pm.move(control + '.cv[6]', (-0.783612, 0, -0.783612), r=True)
    pm.move(control + '.cv[0]', (-0.783612, 0, 0.783612), r=True)
    pm.move(control + '.cv[7]', (-1.108194, 0, 0), r=True)
    return pick


def frame(*args, **kwargs):
    """
    Creates a square within a square shape with lines at the corners.

    Returns:
        (pm.nodetypes.Transform): Transform of frame shape created.
    """
    return pm.curve(d=1, p=[(-1, 0, -1), (-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1), (-2, 0, -2), (2, 0, -2),
                            (1, 0, -1), (1, 0, 1), (2, 0, 2), (2, 0, -2), (2, 0, 2), (-2, 0, 2), (-1, 0, 1),
                            (-2, 0, 2), (-2, 0, -2)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    *args, **kwargs)


def plus(*args, **kwargs):
    """
    Creates plus sign (MEDIC!) shape.

    Returns:
        (pm.nodetypes.Transform): Transform of plus shape created.
    """
    control = pm.curve(d=1,
                       p=[(-1, 0, -3), (1, 0, -3), (1, 0, -1), (3, 0, -1), (3, 0, 1), (1, 0, 1), (1, 0, 3), (-1, 0, 3),
                          (-1, 0, 1), (-3, 0, 1), (-3, 0, -1), (-1, 0, -1), (-1, 0, -3)],
                       k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], *args, **kwargs)
    pm.scale(control, .33, .33, .33)
    pm.makeIdentity(control, apply=True, t=True, r=True, s=True)
    return control


def swirl(*args, **kwargs):
    """
    Creates a whirl like swirl shape.

    Returns:
        (pm.nodetypes.Transform): Transform of swirl shape created.
    """
    return pm.curve(d=3, p=[(0, 0, 0.0360697), (-0.746816, 0, 1), (-2, 0, -0.517827), (0, 0, -2), (2, 0, 0),
                            (0.536575, 0, 2.809361), (-3.191884, 0, 1.292017), (-2.772303, 0, -2.117866),
                            (-0.771699, 0, -3), (1.229059, 0, -3), (3, 0, -1.863394), (3.950518, 0, 0.314344),
                            (3, 0, 3.347373), (0, 0, 4.152682)],
                    k=[0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11, 11], *args, **kwargs)


def arrowSingleStraight(*args, **kwargs):
    """
    Creates an straight arrow with point at origin facing Z-forward shape.

    Returns:
        (pm.nodetypes.Transform): Transform of single straight arrow shape created.
    """
    control = pm.curve(d=1, p=[(0, 1.003235, 0), (0.668823, 0, 0), (0.334412, 0, 0), (0.334412, -0.167206, 0),
                               (0.334412, -0.501617, 0), (0.334412, -1.003235, 0), (-0.334412, -1.003235, 0),
                               (-0.334412, -0.501617, 0), (-0.334412, -0.167206, 0), (-0.334412, 0, 0),
                               (-0.668823, 0, 0), (0, 1.003235, 0)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                       *args, **kwargs)
    control.rx.set(90)
    control.tz.set(-1)
    pm.xform(piv=[0, 0, 0], a=True, ws=True)
    pm.makeIdentity(apply=True, t=True, r=True, s=True)
    return control


def arrowSingleCurved(*args, **kwargs):
    """
    Creates an curved arrow with pivot at origin facing Z-forward shape.

    Returns:
        (pm.nodetypes.Transform): Transform of single curved arrow shape created.
    """
    control = pm.curve(d=1, p=[(-0.251045, 0, 1.015808), (-0.761834, 0, 0.979696), (-0.486547, 0, 0.930468),
                               (-0.570736, 0, 0.886448), (-0.72786, 0, 0.774834), (-0.909301, 0, 0.550655),
                               (-1.023899, 0, 0.285854), (-1.063053, 0, 9.80765e-009), (-0.961797, 0, 8.87346e-009),
                               (-0.926399, 0, 0.258619), (-0.822676, 0, 0.498232), (-0.658578, 0, 0.701014),
                               (-0.516355, 0, 0.802034), (-0.440202, 0, 0.841857), (-0.498915, 0, 0.567734),
                               (-0.251045, 0, 1.015808), ], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                       *args, **kwargs)
    pm.xform(piv=[0, 0, 0], a=True, ws=True)
    return control


def arrowDoubleStraight(*args, **kwargs):
    """
    Creates two arrows joined with pivot at origin facing Z-forward shape.

    Returns:
        (pm.nodetypes.Transform): Transform of double straight arrow shape created.
    """
    control = pm.curve(d=1, p=[(0, 1, 0), (1, 1, 0), (2, 1, 0), (3, 1, 0), (3, 2, 0), (4, 1, 0), (5, 0, 0), (4, -1, 0),
                               (3, -2, 0), (3, -1, 0), (2, -1, 0), (1, -1, 0), (0, -1, 0), (-1, -1, 0), (-2, -1, 0),
                               (-3, -1, 0), (-3, -2, 0), (-4, -1, 0), (-5, 0, 0), (-4, 1, 0), (-3, 2, 0), (-3, 1, 0),
                               (-2, 1, 0), (-1, 1, 0), (0, 1, 0), ],
                       k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                       *args, **kwargs)
    pm.xform(cp=True)
    control.r.set((90, 90, 0))
    pm.scale(.2, .2, .2)
    pm.makeIdentity(apply=True, t=True, r=True, s=True)
    return control


def arrowDoubleCurved(*args, **kwargs):
    """
    Creates two arrows with pivot at origin facing Z-forward shape.

    Returns:
        (pm.nodetypes.Transform): Transform of double curved arrow shape created.
    """
    control = pm.curve(d=1, p=[(-0.251045, 0, -1.015808), (-0.761834, 0, -0.979696), (-0.486547, 0, -0.930468),
                               (-0.570736, 0, -0.886448), (-0.72786, 0, -0.774834), (-0.909301, 0, -0.550655),
                               (-1.023899, 0, -0.285854), (-1.063053, 0, 9.80765e-009), (-1.023899, 0, 0.285854),
                               (-0.909301, 0, 0.550655), (-0.72786, 0, 0.774834), (-0.570736, 0, 0.886448),
                               (-0.486547, 0, 0.930468), (-0.761834, 0, 0.979696), (-0.251045, 0, 1.015808),
                               (-0.498915, 0, 0.567734), (-0.440202, 0, 0.841857), (-0.516355, 0, 0.802034),
                               (-0.658578, 0, 0.701014), (-0.822676, 0, 0.498232), (-0.926399, 0, 0.258619),
                               (-0.961797, 0, 8.87346e-009), (-0.926399, 0, -0.258619), (-0.822676, 0, -0.498232),
                               (-0.658578, 0, -0.701014), (-0.516355, 0, -0.802034), (-0.440202, 0, -0.841857),
                               (-0.498915, 0, -0.567734), (-0.251045, 0, -1.015808)],
                       k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                          26, 27, 28], *args, **kwargs)
    pm.xform(piv=[0, 0, 0], a=True, ws=True)
    control.ry.set(-90)
    pm.makeIdentity(apply=True, t=True, r=True, s=True)
    return control


def arrowTriple(*args, **kwargs):
    """
    Creates three arrows joined with point at origin facing Z-forward shape. Two other arrows face +-X.

    Returns:
        (pm.nodetypes.Transform): Transform of triple straight arrow shape created.
    """
    control = pm.curve(d=1, p=[(-1, 1, 0), (-3, 1, 0), (-3, 2, 0), (-5, 0, 0), (-3, -2, 0), (-3, -1, 0), (-1, -1, 0),
                               (1, -1, 0), (3, -1, 0), (3, -2, 0), (5, 0, 0), (3, 2, 0), (3, 1, 0), (1, 1, 0),
                               (1, 3, 0), (2, 3, 0), (0, 5, 0), (-2, 3, 0), (-1, 3, 0), (-1, 1, 0), ],
                       k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], *args, **kwargs)
    control.rx.set(90)
    control.tz.set(-1)
    pm.scale(.2, .2, .2)
    pm.makeIdentity(apply=True, t=True, r=True, s=True)
    pm.xform(piv=[0, 0, 0], a=True, ws=True)
    return control


def arrowQuad(*args, **kwargs):
    """
    Creates an four arrows with pivot at origin pointing at +- X and Z.

    Returns:
        (pm.nodetypes.Transform): Transform of quad straight arrow shape created.
    """
    control = pm.curve(d=1,
                       p=[(1, 0, 1), (3, 0, 1), (3, 0, 2), (5, 0, 0), (3, 0, -2), (3, 0, -1), (1, 0, -1), (1, 0, -3),
                          (2, 0, -3), (0, 0, -5), (-2, 0, -3), (-1, 0, -3), (-1, 0, -1), (-3, 0, -1), (-3, 0, -2),
                          (-5, 0, 0), (-3, 0, 2), (-3, 0, 1), (-1, 0, 1), (-1, 0, 3), (-2, 0, 3), (0, 0, 5), (2, 0, 3),
                          (1, 0, 3), (1, 0, 1), ],
                       k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                       *args, **kwargs)
    pm.xform(cp=True)
    pm.scale(.2, .2, .2)
    pm.makeIdentity(apply=True, t=True, r=True, s=True)
    return control


def cube(*args, **kwargs):
    """
    Creates a cube shape.

    Returns:
        (pm.nodetypes.Transform): Transform of cube shape created.
    """
    return pm.curve(d=1, p=[(1, 1, 1), (1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1),
                            (1, 1, -1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1),
                            (-1, 1, 1), (-1, -1, 1), (1, -1, 1)],
                    k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], *args, **kwargs)


def diamond(*args, **kwargs):
    """
    Creates a two square pyramids joined facing +- Y axis shape.

    Returns:
        (pm.nodetypes.Transform): Transform of diamond shape created.
    """
    return pm.curve(d=1,
                    p=[(0, 1, 0), (-1, 0.00278996, 6.18172e-08), (0, 0, 1), (0, 1, 0), (1, 0.00278996, 0), (0, 0, 1),
                       (1, 0.00278996, 0), (0, 0, -1), (0, 1, 0), (0, 0, -1), (-1, 0.00278996, 6.18172e-08),
                       (0, -1, 0), (0, 0, -1), (1, 0.00278996, 0), (0, -1, 0), (0, 0, 1)],
                    k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], *args, **kwargs)


def ring(*args, **kwargs):
    """
    Creates an octagonal shape extruded in the Y axis shape.

    Returns:
        (pm.nodetypes.Transform): Transform of ring shape created.
    """
    return pm.curve(d=1, p=[(-0.707107, 0.0916408, 0.707107), (0, 0.0916408, 1), (0, -0.0916408, 1),
                            (-0.707107, -0.0916408, 0.707107), (-0.707107, 0.0916408, 0.707107), (-1, 0.0916408, 0),
                            (-1, -0.0916408, 0), (-0.707107, -0.0916408, 0.707107), (-1, -0.0916408, 0),
                            (-0.707107, -0.0916408, -0.707107), (-0.707107, 0.0916408, -0.707107),
                            (-1, 0.0916408, 0), (-0.707107, 0.0916408, -0.707107), (0, 0.0916408, -1),
                            (0, -0.0916408, -1), (-0.707107, -0.0916408, -0.707107),
                            (-0.707107, 0.0916408, -0.707107), (-0.707107, -0.0916408, -0.707107),
                            (0, -0.0916408, -1), (0.707107, -0.0916408, -0.707107), (0.707107, 0.0916408, -0.707107),
                            (0, 0.0916408, -1), (0.707107, 0.0916408, -0.707107), (1, 0.0916408, 0),
                            (1, -0.0916408, 0), (0.707107, -0.0916408, -0.707107), (1, -0.0916408, 0),
                            (0.707107, -0.0916408, 0.707107), (0.707107, 0.0916408, 0.707107), (1, 0.0916408, 0),
                            (0.707107, 0.0916408, 0.707107), (0, 0.0916408, 1), (0, -0.0916408, 1),
                            (0.707107, -0.0916408, 0.707107)],
                    k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                       26, 27, 28, 29, 30, 31, 32, 33], *args, **kwargs)


def cone(*args, **kwargs):
    """
    Creates a hexagonal pyramid shape with tip point at +1 Y.

    Returns:
        (pm.nodetypes.Transform): Transform of cone shape created.
    """
    return pm.curve(d=1, p=[(-0.5, -1, 0.866025), (0, 1, 0), (0.5, -1, 0.866025), (-0.5, -1, 0.866025),
                            (-1, -1, -1.5885e-07), (0, 1, 0), (-1, -1, -1.5885e-07), (-0.5, -1, -0.866026),
                            (0, 1, 0), (0.5, -1, -0.866025), (-0.5, -1, -0.866026), (0.5, -1, -0.866025), (0, 1, 0),
                            (1, -1, 0), (0.5, -1, -0.866025), (1, -1, 0), (0.5, -1, 0.866025)],
                    k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], *args, **kwargs)


def orb(*args, **kwargs):
    """
    Creates a several circles and rotates them around Y axis to create sphere-like shape.

    Returns:
        (pm.nodetypes.Transform): Transform of orb shape created.
    """
    control = pm.circle(nr=[0, 1, 0], *args, **kwargs)[0]

    circle_list = [pm.duplicate(rr=True)]
    pm.xform(ro=[90, 0, 0])

    circle_list.append(pm.duplicate(rr=True))
    pm.xform(ro=[90, 90, 0])

    circle_list.append(pm.duplicate(rr=True))
    pm.xform(ro=[90, 45, 0])

    circle_list.append(pm.duplicate(rr=True))
    pm.xform(ro=[90, -45, 0])

    pm.select(circle_list)
    pm.makeIdentity(apply=True, t=True, r=True, s=True)
    pm.pickWalk(d='down')
    pm.select(control, tgl=True)
    pm.parent(r=True, s=True)
    pm.delete(circle_list)
    pm.xform(control, cp=True)

    return control


def lever(*args, **kwargs):
    """
    Creates an orb at +1 Y with a single line joining it with the origin.

    Returns:
        (pm.nodetypes.Transform): Transform of lever shape created.
    """
    line = pm.curve(d=1, p=[(0, -1, 0), (0, -2, 0), (0, -3, 0), (0, -4, 0), (0, -5, 0)], k=[0, 1, 2, 3, 4])
    control = orb(*args, **kwargs)

    pm.select(line, r=True)
    pm.pickWalk(d='down')
    pm.select(control, tgl=True)
    pm.parent(r=True, s=True)

    pm.delete(line)
    pm.xform(control, rp=[0, -5, 0], sp=[0, -5, 0])
    pm.xform(control, t=[0, 5, 0])
    pm.scale(.2, .2, .2)
    pm.makeIdentity(control, apply=True, t=True, r=True, s=True)
    return control


def jack(*args, **kwargs):
    """
    Creates six diamonds, each at the +-1 of X, Y, Z. All joined by lines.

    Returns:
        (pm.nodetypes.Transform): Transform of jack shape created.
    """
    cross = pm.curve(d=1, p=[(0, 0, 0.75), (0, 0, 0), (0, 0, -0.75), (0, 0, 0), (0.75, 0, 0), (0, 0, 0), (-0.75, 0, 0),
                             (0, 0, 0), (0, 0.75, 0), (0, 0, 0), (0, -0.75, 0)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    control = diamond(*args, **kwargs)
    pm.scale(.3, .3, .3)
    pm.xform(t=[0, 0, 1])

    diamond_list = [pm.duplicate(rr=True)]
    pm.xform(t=[1, 0, 0])
    diamond_list.append(pm.duplicate(rr=True))
    pm.xform(t=[-1, 0, 0])
    diamond_list.append(pm.duplicate(rr=True))
    pm.xform(t=[0, -1, 0])
    diamond_list.append(pm.duplicate(rr=True))
    pm.xform(t=[0, 1, 0])
    diamond_list.append(pm.duplicate(rr=True))
    pm.xform(t=[0, 0, -1])

    pm.makeIdentity(control, apply=True, t=True, r=True, s=True)
    pm.select(diamond_list, r=True)
    pm.select(cross, tgl=True)

    pm.makeIdentity(apply=True, t=True, r=True, s=True)
    pm.pickWalk(d='down')
    pm.select(control, tgl=True)
    pm.parent(s=True, r=True)
    pm.xform(control, cp=True)

    pm.delete(diamond_list)
    pm.delete(cross)
    return control


def pointer(*args, **kwargs):
    """
    Creates two arrows, one facing Y and other facing X axis, pointing at origin towards +Z shape

    Returns:
        (pm.nodetypes.Transform): Transform of pointer shape created.
    """
    control = pm.curve(d=1, p=[(0, 1.003235, 0), (0.668823, 0, 0), (0.334412, 0, 0), (0.334412, -0.167206, 0),
                               (0.334412, -0.501617, 0), (0.334412, -1.003235, 0), (-0.334412, -1.003235, 0),
                               (-0.334412, -0.501617, 0), (-0.334412, -0.167206, 0), (-0.334412, 0, 0),
                               (-0.668823, 0, 0), (0, 1.003235, 0), (0, 0, -0.668823), (0, 0, -0.334412),
                               (0, -0.167206, -0.334412), (0, -0.501617, -0.334412), (0, -1.003235, -0.334412),
                               (0, -1.003235, 0.334412), (0, -0.501617, 0.334412), (0, -0.167206, 0.334412),
                               (0, 0, 0.334412), (0, 0, 0.668823), (0, 1.003235, 0)],
                       k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                       *args, **kwargs)
    control.rx.set(90)
    control.tz.set(-1)
    pm.xform(piv=[0, 0, 0], a=True, ws=True)
    pm.makeIdentity(apply=True, t=True, r=True, s=True)
    return control


def characters(word, font='Times New Roman', *args, **kwargs):
    """
    Creates a shape for EACH curve needed to write given word.

    Args:
        word (string): Word to create shape for.

        font (string): Name of font to generate curve in.

    Returns:
        (list): Transforms of all the character shapes created.
    """
    pm.textCurves(ch=0, f=font, t=word, *args, **kwargs)
    pm.ungroup()
    pm.ungroup()
    controls = pm.ls(sl=True)
    pm.xform(cp=True)
    return controls


def text(word, font='Times New Roman', *args, **kwargs):
    """
    Creates a shape for the given word as curve.

    Args:
        word (string): Word to create shape for.

        font (string): Name of font to generate curve in.

    Returns:
        (pm.nodetypes.Transform): Transform of text shape created.
    """
    pm.textCurves(ch=0, f=font, t=word, *args, **kwargs)
    pm.ungroup()
    pm.ungroup()

    curves = pm.ls(sl=True)
    pm.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    shapes = curves[1:]
    pm.select(shapes, r=True)
    pm.pickWalk(d='Down')
    pm.select(curves[0], tgl=True)
    pm.parent(r=True, s=True)
    pm.pickWalk(d='up')
    control = pm.ls(sl=True)[0]
    pm.delete(shapes)

    pm.xform(cp=True)
    pm.xform(ws=True, t=[0, 0, 0])
    return control
