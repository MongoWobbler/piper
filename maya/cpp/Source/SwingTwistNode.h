#pragma once

#include <maya/MPxNode.h>


// Thanks to Chad Vernon for this awesome plug-in.
// https://www.chadvernon.com/blog/swing-twist/
// https://github.com/chadmv/cmt/blob/1b1a9a4fb154d1d10e73373cf899e4d83c95a6a1/src/swingTwistNode.h


class SwingTwistNode : public MPxNode
{
public:
    static void* creator();
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);

public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject aOutMatrix;
    static MObject aRestMatrix;
    static MObject aTargetRestMatrix;
    static MObject aInMatrix;
    static MObject aTwistWeight;
    static MObject aSwingWeight;
    static MObject aTwistAxis;
};
