//  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

#include "PiperTransforms.h"


MTypeId PiperMatrix::type_ID(0x00137140);

MTypeId PiperMesh::type_ID(0x00137141);
MString PiperMesh::node_name("piperMesh");

MTypeId PiperSkinnedMesh::type_ID(0x00137142);
MString PiperSkinnedMesh::node_name("piperSkinnedMesh");

MTypeId PiperRig::type_ID(0x00137143);
MString PiperRig::node_name("piperRig");

MTypeId PiperAnimation::type_ID(0x00137144);
MString PiperAnimation::node_name("piperAnimation");


MPxTransformationMatrix* PiperMatrix::creator()
{
    return new PiperMatrix();
}

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
    return MS::kSuccess;
}
