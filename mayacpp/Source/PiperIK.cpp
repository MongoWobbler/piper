#include "PiperIK.h"
#include "util.h"

#include <maya/MGlobal.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFloatVector.h>
#include <maya/MMatrix.h>

#include <iso646.h>


MTypeId PiperIK::type_ID(0x00137145);
MString PiperIK::node_name("piperIK");
MObject PiperIK::start_matrix;
MObject PiperIK::end_matrix;
MObject PiperIK::separator;
MObject PiperIK::start_initial_length;
MObject PiperIK::end_initial_length;
MObject PiperIK::start_output;
MObject PiperIK::end_output;
MObject PiperIK::start_scale;
MObject PiperIK::end_scale;
MObject PiperIK::slide;
MObject PiperIK::stretch;
MObject PiperIK::softness;
MObject PiperIK::global_scale;
MObject PiperIK::pole_vector_matrix;
MObject PiperIK::pole_vector_lock;
MObject PiperIK::twist;
MObject PiperIK::output_scale;


PiperMatrix* PiperIK::getPiperMatrix()
{
    PiperMatrix* piper_matrix = (PiperMatrix *) transformationMatrixPtr();
    return piper_matrix;
}


MStatus PiperIK::initialize()
{
	MFnNumericAttribute numeric_fn;
	MFnMatrixAttribute matrix_fn;
	MFnEnumAttribute enum_fn;

	start_matrix = matrix_fn.create("startMatrix", "stm");
	matrix_fn.setStorable(true);
	matrix_fn.setKeyable(true);
	addAttribute(start_matrix);

	end_matrix = matrix_fn.create("endMatrix", "edm");
	matrix_fn.setStorable(true);
	matrix_fn.setKeyable(true);
	addAttribute(end_matrix);

	pole_vector_matrix = matrix_fn.create("poleVectorMatrix", "pvm");
	matrix_fn.setStorable(true);
	matrix_fn.setKeyable(true);
	addAttribute(pole_vector_matrix);

	separator = enum_fn.create("_", "_");
	enum_fn.addField("_", 0);
	enum_fn.setStorable(true);
	enum_fn.setKeyable(true);
	addAttribute(separator);

	start_initial_length = numeric_fn.create("startInitialLength", "sil", MFnNumericData::kDouble, 0);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setHidden(true);
	numeric_fn.setMin(0.001);
	addAttribute(start_initial_length);

	end_initial_length = numeric_fn.create("endInitialLength", "eil", MFnNumericData::kDouble, 0);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
    numeric_fn.setHidden(true);
	numeric_fn.setMin(0.001);
	addAttribute(end_initial_length);

	start_scale = numeric_fn.create("start_scale", "sts", MFnNumericData::kDouble, 1);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setMin(0.001);
	addAttribute(start_scale);

	end_scale = numeric_fn.create("end_scale", "eds", MFnNumericData::kDouble, 1);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setMin(0.001);
	addAttribute(end_scale);

	global_scale = numeric_fn.create("globalScale", "gbs", MFnNumericData::kDouble, 1);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
    numeric_fn.setHidden(true);
	numeric_fn.setMin(0.001);
	addAttribute(global_scale);

	pole_vector_lock = numeric_fn.create("poleVectorLock", "pvl", MFnNumericData::kDouble, 0);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setMin(0);
	numeric_fn.setMax(1);
	addAttribute(pole_vector_lock);

    twist = numeric_fn.create("twist", "tws", MFnNumericData::kDouble, 0);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    addAttribute(twist);

	slide = numeric_fn.create("slide", "sld", MFnNumericData::kDouble, 0);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setMin(-1);
	numeric_fn.setMax(1);
	addAttribute(slide);

	stretch = numeric_fn.create("stretch", "stc", MFnNumericData::kDouble, 1);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setMin(0);
	numeric_fn.setMax(1);
	addAttribute(stretch);

    softness = numeric_fn.create("softness", "sof", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    addAttribute(softness);

    output_scale = numeric_fn.create("outputScale", "ops", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    numeric_fn.setHidden(true);
    addAttribute(output_scale);

	start_output = numeric_fn.create("startOutput", "sto", MFnNumericData::kDouble, 1);
	numeric_fn.setStorable(false);
	numeric_fn.setKeyable(false);
	numeric_fn.setWritable(false);
	addAttribute(start_output);

	end_output = numeric_fn.create("endOutput", "edo", MFnNumericData::kDouble, 1);
	numeric_fn.setStorable(false);
	numeric_fn.setKeyable(false);
	numeric_fn.setWritable(false);
	addAttribute(end_output);

	attributeAffects(start_matrix, start_output);
	attributeAffects(end_matrix, start_output);
	attributeAffects(stretch, start_output);
	attributeAffects(slide, start_output);
	attributeAffects(softness, start_output);
	attributeAffects(pole_vector_lock, start_output);
	attributeAffects(pole_vector_matrix, start_output);
	attributeAffects(global_scale, start_output);
	attributeAffects(start_scale, start_output);
	attributeAffects(start_initial_length, start_output);
	attributeAffects(output_scale, start_output);

	attributeAffects(start_matrix, end_output);
	attributeAffects(end_matrix, end_output);
	attributeAffects(stretch, end_output);
	attributeAffects(slide, end_output);
	attributeAffects(softness, start_output);
	attributeAffects(pole_vector_lock, end_output);
	attributeAffects(pole_vector_matrix, end_output);
	attributeAffects(global_scale, end_output);
	attributeAffects(end_scale, end_output);
	attributeAffects(end_initial_length, end_output);
	attributeAffects(output_scale, end_output);

	return MS::kSuccess; 

}


MStatus PiperIK::compute(const MPlug& plug, MDataBlock& data)
{
	if (plug == start_output or plug == end_output)
	{
		MMatrix start_matrix_value = data.inputValue(start_matrix).asMatrix();
		MMatrix end_matrix_value = data.inputValue(end_matrix).asMatrix();
		MMatrix pole_vector_matrix_value = data.inputValue(pole_vector_matrix).asMatrix();

		double start_initial_length_value = data.inputValue(start_initial_length).asDouble();
		double end_initial_length_value = data.inputValue(end_initial_length).asDouble();

		double soft_value = data.inputValue(softness).asDouble();
		double stretch_value = data.inputValue(stretch).asDouble();
		double slide_value = data.inputValue(slide).asDouble();
		double pole_vector_lock_value = data.inputValue(pole_vector_lock).asDouble();
		double global_scale_value = data.inputValue(global_scale).asDouble();
		double start_scale_value = data.inputValue(start_scale).asDouble();
		double end_scale_value = data.inputValue(end_scale).asDouble();
        double output_scale_value = data.inputValue(output_scale).asDouble();

		// scaling joint lengths
		start_initial_length_value *= global_scale_value;
		end_initial_length_value *= global_scale_value;
		start_initial_length_value *= start_scale_value;
		end_initial_length_value *= end_scale_value;
		double chain_initial_length = start_initial_length_value + end_initial_length_value;

		MVector start_position = getPosition(start_matrix_value);
		MVector end_position = getPosition(end_matrix_value);
		
		double current_chain_length = getDistance(start_position, end_position);
		double start_output_value = start_initial_length_value;
		double end_output_value = end_initial_length_value;
		double soft_distance = chain_initial_length - soft_value;

		// soft ik
		if (soft_value != 0 and current_chain_length > soft_distance)
        {
		    double new_distance = soft_distance + soft_value * (1 - exp( -1 * (current_chain_length - soft_distance)));
            double scale = current_chain_length / new_distance;

            start_output_value = start_output_value * scale;
            end_output_value = end_output_value * scale;

            start_output_value = lerp(start_initial_length_value, start_output_value, stretch_value);
            end_output_value = lerp(end_initial_length_value, end_output_value, stretch_value);
        }

		// stretch
		if (stretch_value != 0 and soft_value == 0)
		{
			double delta = current_chain_length / chain_initial_length;

			if (delta > 1)
			{
				start_output_value = lerp(start_initial_length_value, delta * start_output_value, stretch_value);
				end_output_value = lerp(end_initial_length_value, delta * end_output_value, stretch_value);
			}
		}

		// slide
		double output_total = start_output_value + end_output_value;
		double slide_alpha = abs(slide_value) == 1? abs(slide_value) - .001 : abs(slide_value);  // prevents joint collapse
		if (slide_value >= 0)
		{
			start_output_value = lerp(start_output_value, output_total, slide_alpha);
			end_output_value = lerp(end_output_value, 0.0, slide_alpha);
		}
		else
		{
			start_output_value = lerp(start_output_value, 0.0, slide_alpha);
			end_output_value = lerp(end_output_value, output_total, slide_alpha);
		}

		// pole vector lock
		if (pole_vector_lock_value > 0.001)
		{
			MVector pole_position = getPosition(pole_vector_matrix_value);
			
			double start_pole_distance = getDistance(start_position, pole_position);
			double end_pole_distance = getDistance(pole_position, end_position);

			start_output_value = lerp(start_output_value, start_pole_distance, pole_vector_lock_value);
			end_output_value = lerp(end_output_value, end_pole_distance, pole_vector_lock_value);
		}

		data.outputValue(start_output).set(start_output_value * output_scale_value);
		data.outputValue(start_output).setClean();

		data.outputValue(end_output).set(end_output_value * output_scale_value);
		data.outputValue(end_output).setClean();

        return MS::kSuccess;
	}

	else if( (plug.attribute() == MPxTransform::matrix)
         or  (plug.attribute() == MPxTransform::inverseMatrix)
         or  (plug.attribute() == MPxTransform::worldMatrix)
         or  (plug.attribute() == MPxTransform::worldInverseMatrix)
         or  (plug.attribute() == MPxTransform::parentMatrix)
         or  (plug.attribute() == MPxTransform::parentInverseMatrix) )
    {
        PiperMatrix* piper_matrix = getPiperMatrix();
        if (piper_matrix)
        {
            computeLocalTransformation(piper_matrix, data);
        }
        else
        {
            MGlobal::displayError("Failed to get Piper IK's matrix");
        }

        return MPxTransform::compute(plug, data);
    }

    return MS::kSuccess;

}
