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

public:
	static MTypeId type_ID;
    static MString node_name;
	static MObject start_matrix;
	static MObject end_matrix;
	static MObject separator;
	static MObject start_initial_length;
	static MObject end_initial_length;
	static MObject start_scale;
	static MObject end_scale;
	static MObject start_output;
	static MObject end_output;
	static MObject slide;
	static MObject stretch;
    static MObject softness;
	static MObject global_scale;
	static MObject pole_vector_matrix;
	static MObject pole_vector_lock;
	static MObject twist;
	static MObject output_scale;

};
