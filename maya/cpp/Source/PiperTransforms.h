//  Copyright (c) Christian Corsica. All Rights Reserved.

#pragma once

#include <maya/MTypeId.h>
#include <maya/MPxTransform.h>


class PiperMesh : public MPxTransform
{
public:
    static void* creator();
    static MStatus initialize();

public:
    static MTypeId type_ID;
    static MString node_name;
};


class PiperSkinnedMesh : public MPxTransform
{
public:
    static void* creator();
    static MStatus initialize();

public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject wraps;
};


class PiperRig : public MPxTransform
{
public:
    static void* creator();
    static MStatus initialize();

public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject separator;
    static MObject high_poly;
};


class PiperAnimation : public MPxTransform
{
public:
    static void* creator();
    static MStatus initialize();

public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject clip_data;
};