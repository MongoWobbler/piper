//  Copyright (c) 2021 Christian Corsica. All Rights Reserved.#ifndef PIPER_PIPERMATH_H

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