//  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

#include "PiperTransforms.h"
#include "PiperIK.h"
#include "PiperFK.h"
#include "PiperMath.h"
#include "TensionNode.h"
#include <maya/MFnPlugin.h>


MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin_fn(obj, "Christian Corsica", "1.0", "Any");

    // Piper Mesh
    status = plugin_fn.registerTransform(PiperMesh::node_name,
                                         PiperMesh::type_ID,
                                         PiperMesh::creator,
                                         PiperMesh::initialize,
                                         MPxTransformationMatrix::creator,
                                         MPxTransformationMatrix::baseTransformationMatrixId);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper Mesh node.");
    }

    // Piper Skinned Mesh
    status = plugin_fn.registerTransform(PiperSkinnedMesh::node_name,
                                         PiperSkinnedMesh::type_ID,
                                         PiperSkinnedMesh::creator,
                                         PiperSkinnedMesh::initialize,
                                         MPxTransformationMatrix::creator,
                                         MPxTransformationMatrix::baseTransformationMatrixId);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper Skinned Mesh node.");
    }

    // Piper Rig
    status = plugin_fn.registerTransform(PiperRig::node_name,
                                         PiperRig::type_ID,
                                         PiperRig::creator,
                                         PiperRig::initialize,
                                         MPxTransformationMatrix::creator,
                                         MPxTransformationMatrix::baseTransformationMatrixId);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper Rig node.");
    }

    // Piper Animation
    status = plugin_fn.registerTransform(PiperAnimation::node_name,
                                         PiperAnimation::type_ID,
                                         PiperAnimation::creator,
                                         PiperAnimation::initialize,
                                         MPxTransformationMatrix::creator,
                                         MPxTransformationMatrix::baseTransformationMatrixId);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper Animation node.");
    }

    // Piper FK
    status = plugin_fn.registerTransform(PiperFK::node_name,
                                         PiperFK::type_ID,
                                         PiperFK::creator,
                                         PiperFK::initialize,
                                         MPxTransformationMatrix::creator,
                                         MPxTransformationMatrix::baseTransformationMatrixId);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper FK node.");
    }

    // Piper IK
    status = plugin_fn.registerTransform(PiperIK::node_name,
                                         PiperIK::type_ID,
                                         PiperIK::creator,
                                         PiperIK::initialize,
                                         MPxTransformationMatrix::creator,
                                         MPxTransformationMatrix::baseTransformationMatrixId);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper IK node.");
    }

    // Multiply Node
    status = plugin_fn.registerNode(PiperMultiply::node_name,
                                    PiperMultiply::type_ID,
                                    PiperMultiply::creator,
                                    PiperMultiply::initialize);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper Multiply node.");
    }

    // Tension Node
    status = plugin_fn.registerNode(TensionNode::node_name,
                                    TensionNode::type_ID,
                                    TensionNode::creator,
                                    TensionNode::initialize);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Tension node.");
    }

    return status;
}


MStatus uninitializePlugin(MObject obj)
{
    MFnPlugin plugin_fn;
    plugin_fn.deregisterNode(TensionNode::type_ID);
    plugin_fn.deregisterNode(PiperMultiply::type_ID);
    plugin_fn.deregisterNode(PiperIK::type_ID);
    plugin_fn.deregisterNode(PiperFK::type_ID);
    plugin_fn.deregisterNode(PiperAnimation::type_ID);
    plugin_fn.deregisterNode(PiperRig::type_ID);
    plugin_fn.deregisterNode(PiperSkinnedMesh::type_ID);
    plugin_fn.deregisterNode(PiperMesh::type_ID);

    return MS::kSuccess;
}
