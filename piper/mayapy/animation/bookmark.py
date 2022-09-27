#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm
import maya.plugin.timeSliderBookmark.timeSliderBookmark as bookmark

import piper.config.maya as mcfg
import piper.mayapy.convert as convert


def fromClipData(clip_data):
    """
    Creates bookmarks from the given clip data if it doesn't exist, else makes sure time and color is set correctly.

    Args:
        clip_data (dictionary): Name of clip as key, dict data as value with start and end times.

    Returns:
        (dictionary): Name of clip as key, bookmark as value.
    """
    if not clip_data:
        return {}

    marks = {}
    for name, data in clip_data.items():

        bookmark_name = name.lower() + mcfg.bookmark_suffix
        if pm.objExists(bookmark_name):
            mark = pm.PyNode(bookmark_name)
            mark.timeRangeStart.set(data['start'])
            mark.timeRangeStop.set(data['end'] + 1)
        else:
            mark = bookmark.createBookmark(name=name, start=data['start'], stop=data['end'] + 1)
            mark = pm.rename(mark, bookmark_name)

        if name in mcfg.bookmark_clip_colors:
            color = convert.colorToRGB(mcfg.bookmark_clip_colors[name])
            mark.color.set(*color)

        marks[name] = mark

    return marks
