//  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

#include "PiperTransforms.h"
#include <maya/MFnTypedAttribute.h>


MTypeId PiperMesh::type_ID(0x00137140);
MString PiperMesh::node_name("piperMesh");

MTypeId PiperSkinnedMesh::type_ID(0x00137141);
MString PiperSkinnedMesh::node_name("piperSkinnedMesh");

MTypeId PiperRig::type_ID(0x00137142);
MString PiperRig::node_name("piperRig");

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
    return MS::kSuccess;
}


void* PiperRig::creator()
{
    return new PiperRig();
}


MStatus PiperRig::initialize()
{
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
