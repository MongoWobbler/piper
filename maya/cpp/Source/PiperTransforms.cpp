//  Copyright (c) Christian Corsica. All Rights Reserved.

#include "PiperTransforms.h"
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnEnumAttribute.h>


MTypeId PiperMesh::type_ID(0x00137140);
MString PiperMesh::node_name("piperMesh");

MTypeId PiperSkinnedMesh::type_ID(0x00137141);
MString PiperSkinnedMesh::node_name("piperSkinnedMesh");
MObject PiperSkinnedMesh::wraps;

MTypeId PiperRig::type_ID(0x00137142);
MString PiperRig::node_name("piperRig");
MObject PiperRig::separator;
MObject PiperRig::high_poly;

MTypeId PiperAnimation::type_ID(0x00137143);
MString PiperAnimation::node_name("piperAnimation");
MObject PiperAnimation::clip_data;


void* PiperMesh::creator()
{
    return new PiperMesh();
}


MStatus PiperMesh::initialize()
{
    return MS::kSuccess;
}


void* PiperSkinnedMesh::creator()
{
    return new PiperSkinnedMesh();
}


MStatus PiperSkinnedMesh::initialize()
{
    MFnTypedAttribute typed_fn;

    wraps = typed_fn.create("wraps", "wap", MFnData::kString);
    typed_fn.setStorable(true);
    typed_fn.setWritable(true);
    addAttribute(wraps);

    return MS::kSuccess;
}


void* PiperRig::creator()
{
    return new PiperRig();
}


MStatus PiperRig::initialize()
{
    MFnEnumAttribute enum_fn;
    MFnNumericAttribute numeric_fn;

    separator = enum_fn.create("_", "_");
    enum_fn.addField("_", 0);
    enum_fn.setStorable(true);
    enum_fn.setKeyable(true);
    addAttribute(separator);

    high_poly = numeric_fn.create("highPolyVisibility", "hpv", MFnNumericData::kBoolean, false);
    numeric_fn.setWritable(true);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    addAttribute(high_poly);

    return MS::kSuccess;
}


void* PiperAnimation::creator()
{
    return new PiperAnimation();
}


MStatus PiperAnimation::initialize()
{
    MFnTypedAttribute typed_fn;

    clip_data = typed_fn.create("clipData", "clp", MFnData::kString);
    typed_fn.setStorable(true);
    typed_fn.setWritable(true);
    addAttribute(clip_data);

    return MS::kSuccess;
}
