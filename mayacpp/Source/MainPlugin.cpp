//  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

#include "PiperTransforms.h"
#include <maya/MFnPlugin.h>


MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin_fn(obj, "Christian Corsica", "1.0", "Any");
    status = plugin_fn.registerTransform(PiperMesh::node_name,
                                         PiperMesh::type_ID,
                                         PiperMesh::creator,
                                         PiperMesh::initialize,
                                         PiperMatrix::creator,
                                         PiperMatrix::type_ID);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper Mesh node.");
    }

    status = plugin_fn.registerTransform(PiperSkinnedMesh::node_name,
                                         PiperSkinnedMesh::type_ID,
                                         PiperSkinnedMesh::creator,
                                         PiperSkinnedMesh::initialize,
                                         PiperMatrix::creator,
                                         PiperMatrix::type_ID);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper Skinned Mesh node.");
    }

    status = plugin_fn.registerTransform(PiperRig::node_name,
                                         PiperRig::type_ID,
                                         PiperRig::creator,
                                         PiperRig::initialize,
                                         PiperMatrix::creator,
                                         PiperMatrix::type_ID);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper Rig node.");
    }

    status = plugin_fn.registerTransform(PiperAnimation::node_name,
                                         PiperAnimation::type_ID,
                                         PiperAnimation::creator,
                                         PiperAnimation::initialize,
                                         PiperMatrix::creator,
                                         PiperMatrix::type_ID);

    if (status != MS::kSuccess)
    {
        status.perror("Could not register Piper Animation node.");
    }

    return status;
}


MStatus uninitializePlugin(MObject obj)
{
    MFnPlugin plugin_fn;
    plugin_fn.deregisterNode(PiperAnimation::type_ID);
    plugin_fn.deregisterNode(PiperRig::type_ID);
    plugin_fn.deregisterNode(PiperSkinnedMesh::type_ID);
    plugin_fn.deregisterNode(PiperMesh::type_ID);

    return MS::kSuccess;
}
