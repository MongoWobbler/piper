#pragma once

#include <maya/MPxNode.h>

// Thanks to Anno Schachner for this awesome plugin.
// https://github.com/wiremas/tension

// Macros
#define MCheckStatus(status,message)        \
        if( MStatus::kSuccess != status ) { \
                cerr << message << "\n";    \
                return status;              \
        }

class TensionNode : public MPxNode
{
public:
    TensionNode() = default;
    virtual ~TensionNode() {}
    virtual void postConstructor();
    virtual MStatus compute( const MPlug& plug, MDataBlock& data );
    virtual MStatus setDependentsDirty( const MPlug& dirtyPlug, MPlugArray& affectedPlugs );
    static void* creator(){ return new TensionNode(); }
    static MStatus initialize();
    static MDoubleArray getEdgeLen( const MDataHandle& inMesh );

public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject aOrigShape;
    static MObject aDeformedShape;
    static MObject aOutShape;
    static MObject aColorRamp;

    static bool isOrigDirty;
    static bool isDeformedDirty;
    static MDoubleArray origEdgeLenArray;
    static MDoubleArray deformedEdgeLenArray;
};

