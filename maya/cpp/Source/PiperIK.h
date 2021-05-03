#pragma once

#include <maya/MTypeId.h>
#include <maya/MPxNode.h>
#include <maya/MPxTransform.h>

class PiperIK : public MPxTransform
{
public:
    PiperIK() = default;
    static void* creator() {return new PiperIK();};
	static MStatus initialize();
	MStatus compute(const MPlug& plug, MDataBlock& data) override;

private:
    static MAngle calculatePreferredAngle(const double& angle, const double& length, const double& blend);

public:
	static MTypeId type_ID;
    static MString node_name;
	static MObject start_matrix;
	static MObject handle_parent_matrix;
    static MObject handle_translate_x;
    static MObject handle_translate_y;
    static MObject handle_translate_z;
    static MObject handle_translate;
	static MObject separator;
	static MObject start_initial_length;
	static MObject end_initial_length;
    static MObject start_control_scale;
    static MObject start_scale;
    static MObject end_scale;
	static MObject direction;
	static MObject start_output;
	static MObject end_output;
	static MObject start_output_scale;
    static MObject end_output_scale;
	static MObject slide;
    static MObject volumetric;
	static MObject stretch;
    static MObject softness;
	static MObject global_scale;
	static MObject pole_vector_matrix;
    static MObject pole_control_scale;
	static MObject pole_vector_lock;
	static MObject twist;
    static MObject preferred_angle_input_x;
    static MObject preferred_angle_input_y;
    static MObject preferred_angle_input_z;
    static MObject preferred_angle_input;
    static MObject preferred_angle_output_x;
    static MObject preferred_angle_output_y;
    static MObject preferred_angle_output_z;
    static MObject preferred_angle_output;
    static MObject preferred_angle_blend;

};
