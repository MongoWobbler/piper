//  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

#include "PiperFK.h"
#include "util.h"

#include <maya/MGlobal.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnCompoundAttribute.h>

#include <iso646.h>


MString PiperFK::node_name("piperFK");
MTypeId PiperFK::type_ID(0x00137144);
MObject PiperFK::separator;
MObject PiperFK::global_scale;
MObject PiperFK::initial_length;
MObject PiperFK::volumetric_scaling;
MObject PiperFK::scale_driver_matrix;
MObject PiperFK::scale_parent_matrix;
MObject PiperFK::scale_translate_x;
MObject PiperFK::scale_translate_y;
MObject PiperFK::scale_translate_z;
MObject PiperFK::scale_translate;
MObject PiperFK::output_scale;
MObject PiperFK::output_inverse_scale;

MStatus PiperFK::initialize()
{

    MFnNumericAttribute numeric_fn;
    MFnMatrixAttribute matrix_fn;
    MFnEnumAttribute enum_fn;
    MFnCompoundAttribute compound_fn;

    separator = enum_fn.create("_", "_");
    enum_fn.addField("_", 0);
    enum_fn.setStorable(true);
    enum_fn.setKeyable(true);
    addAttribute(separator);

    global_scale = numeric_fn.create("globalScale", "gbs", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    numeric_fn.setHidden(true);
    numeric_fn.setMin(0.001);
    addAttribute(global_scale);

    initial_length = numeric_fn.create("initialLength", "ile", MFnNumericData::kDouble, 0.001);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    numeric_fn.setHidden(true);
    numeric_fn.setMin(0.001);
    addAttribute(initial_length);

    volumetric_scaling = numeric_fn.create("volumetric", "vol", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    numeric_fn.setMin(0.0);
    numeric_fn.setMax(1.0);
    addAttribute(volumetric_scaling);

    scale_driver_matrix = matrix_fn.create("scaleDriverMatrix", "sdm");
    matrix_fn.setStorable(true);
    matrix_fn.setKeyable(true);
    addAttribute(scale_driver_matrix);

    scale_parent_matrix = matrix_fn.create("scaleParentMatrix", "spm");
    matrix_fn.setStorable(true);
    matrix_fn.setKeyable(true);
    addAttribute(scale_parent_matrix);

    scale_translate_x = numeric_fn.create("scaleTranslateX", "stx", MFnNumericData::kDouble, 0);
    numeric_fn.setStorable(true);
    numeric_fn.setWritable(true);
    numeric_fn.setHidden(true);
    addAttribute(scale_translate_x);

    scale_translate_y = numeric_fn.create("scaleTranslateY", "sty", MFnNumericData::kDouble, 0);
    numeric_fn.setStorable(true);
    numeric_fn.setWritable(true);
    numeric_fn.setHidden(true);
    addAttribute(scale_translate_y);

    scale_translate_z = numeric_fn.create("scaleTranslateZ", "stz", MFnNumericData::kDouble, 0);
    numeric_fn.setStorable(true);
    numeric_fn.setWritable(true);
    numeric_fn.setHidden(true);
    addAttribute(scale_translate_z);

    scale_translate = compound_fn.create("scaleTranslate", "itc");
    compound_fn.addChild(scale_translate_x);
    compound_fn.addChild(scale_translate_y);
    compound_fn.addChild(scale_translate_z);
    compound_fn.setStorable(true);
    compound_fn.setWritable(true);
    compound_fn.setHidden(true);
    addAttribute(scale_translate);

    // OUTPUTS

    output_scale = numeric_fn.create("outputScale", "ops", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(false);
    numeric_fn.setKeyable(false);
    numeric_fn.setHidden(false);
    addAttribute(output_scale);

    output_inverse_scale = numeric_fn.create("outputInverseScale", "ois", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(false);
    numeric_fn.setKeyable(false);
    numeric_fn.setWritable(false);
    addAttribute(output_inverse_scale);

    attributeAffects(global_scale, output_scale);
    attributeAffects(initial_length, output_scale);
    attributeAffects(volumetric_scaling, output_scale);
    attributeAffects(scale_driver_matrix, output_scale);
    attributeAffects(scale_parent_matrix, output_scale);
    attributeAffects(scale_translate, output_scale);

    attributeAffects(global_scale, output_inverse_scale);
    attributeAffects(initial_length, output_inverse_scale);
    attributeAffects(volumetric_scaling, output_inverse_scale);
    attributeAffects(scale_driver_matrix, output_inverse_scale);
    attributeAffects(scale_parent_matrix, output_inverse_scale);
    attributeAffects(scale_translate, output_inverse_scale);

    return MS::kSuccess;
}


MStatus PiperFK::compute(const MPlug &plug, MDataBlock &data)
{

    if (plug == output_scale or plug == output_inverse_scale)
    {
        MMatrix driver_matrix_value = data.inputValue(scale_driver_matrix).asMatrix();
        MMatrix parent_matrix_value = data.inputValue(scale_parent_matrix).asMatrix();

        double global_scale_value = data.inputValue(global_scale).asDouble();
        double initial_length_value = data.inputValue(initial_length).asDouble();
        double volumetric_value = data.inputValue(volumetric_scaling).asDouble();
        MVector translate_value = data.inputValue(scale_translate).asVector();

        MVector driver_position = getPosition(driver_matrix_value);
        MMatrix translate_matrix = matrixFromVector(translate_value);
        MMatrix target_matrix = translate_matrix * parent_matrix_value;
        MVector target_position = getPosition(target_matrix);

        double distance = getDistance(driver_position, target_position);
        double normalized_distance = distance / (initial_length_value  * global_scale_value);

        double inverse_distance = 1.0 / normalized_distance;

        normalized_distance = lerp(global_scale_value, normalized_distance, volumetric_value);
        inverse_distance = lerp(global_scale_value, inverse_distance, volumetric_value);

        data.outputValue(output_scale).set(normalized_distance);
        data.outputValue(output_scale).setClean();

        data.outputValue(output_inverse_scale).set(inverse_distance);
        data.outputValue(output_inverse_scale).setClean();

    }

    return MPxTransform::compute(plug, data);

}
