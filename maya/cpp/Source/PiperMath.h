//  Copyright (c) Christian Corsica. All Rights Reserved.

#pragma once

#include <maya/MTypeId.h>
#include <maya/MPxNode.h>


class PiperMultiply : public MPxNode
{
public:
    static void* creator();
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject weight;
    static MObject main_term;
    static MObject input;
    static MObject outputX;
    static MObject outputY;
    static MObject outputZ;
    static MObject output;
};


class PiperReciprocal : public MPxNode
{
public:
    static void* creator();
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject input;
    static MObject output;
};


class PiperOneMinus : public MPxNode
{
public:
    static void* creator();
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject input;
    static MObject output;

};


class PiperOrientMatrix : public MPxNode
{
public:
    static void* creator();
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject weight;
    static MObject position_matrix;
    static MObject orient_matrix;
    static MObject output;
};


class PiperBlendAxis : public MPxNode
{
public:
    static void* creator();
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject weight;
    static MObject axis1;
    static MObject axis1X;
    static MObject axis1Y;
    static MObject axis1Z;
    static MObject axis2;
    static MObject axis2X;
    static MObject axis2Y;
    static MObject axis2Z;
    static MObject output;
    static MObject outputX;
    static MObject outputY;
    static MObject outputZ;
};


class PiperSafeDivide : public MPxNode
{
public:
    static void* creator();
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject input1;
    static MObject input2;
    static MObject output;
};