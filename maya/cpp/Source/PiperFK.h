//  Copyright (c) 2021 Christian Corsica. All Rights Reserved.#ifndef PIPER_PIPERFK_H

#pragma once

#include <maya/MTypeId.h>
#include <maya/MPxNode.h>
#include <maya/MPxTransform.h>

class PiperFK : public MPxTransform
{
public:
    PiperFK() = default;
    static void* creator() {return new PiperFK();};
    static MStatus initialize();
    MStatus compute(const MPlug& plug, MDataBlock& data) override;

public:
    static MTypeId type_ID;
    static MString node_name;
    static MObject separator;
    static MObject global_scale;
    static MObject initial_length;
    static MObject volumetric_scaling;
    static MObject scale_driver_matrix;
    static MObject scale_parent_matrix;
    static MObject scale_translate_x;
    static MObject scale_translate_y;
    static MObject scale_translate_z;
    static MObject scale_translate;
    static MObject output_scale;
    static MObject output_inverse_scale;
};