#include "PiperIK.h"
#include "util.h"

#include <algorithm>
#include <maya/MGlobal.h>
#include <maya/MAngle.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnCompoundAttribute.h>

#include <iso646.h>


MTypeId PiperIK::type_ID(0x00137145);
MString PiperIK::node_name("piperIK");
MObject PiperIK::start_matrix;
MObject PiperIK::handle_parent_matrix;
MObject PiperIK::handle_translate_x;
MObject PiperIK::handle_translate_y;
MObject PiperIK::handle_translate_z;
MObject PiperIK::handle_translate;
MObject PiperIK::separator;
MObject PiperIK::start_initial_length;
MObject PiperIK::end_initial_length;
MObject PiperIK::direction;
MObject PiperIK::start_output;
MObject PiperIK::end_output;
MObject PiperIK::start_output_scale;
MObject PiperIK::end_output_scale;
MObject PiperIK::start_scale;
MObject PiperIK::end_scale;
MObject PiperIK::slide;
MObject PiperIK::volumetric;
MObject PiperIK::stretch;
MObject PiperIK::softness;
MObject PiperIK::global_scale;
MObject PiperIK::pole_vector_matrix;
MObject PiperIK::pole_vector_lock;
MObject PiperIK::twist;
MObject PiperIK::preferred_angle_input_x;
MObject PiperIK::preferred_angle_input_y;
MObject PiperIK::preferred_angle_input_z;
MObject PiperIK::preferred_angle_input;
MObject PiperIK::preferred_angle_output_x;
MObject PiperIK::preferred_angle_output_y;
MObject PiperIK::preferred_angle_output_z;
MObject PiperIK::preferred_angle_output;
MObject PiperIK::preferred_angle_blend;


MStatus PiperIK::initialize()
{
    MFnCompoundAttribute compound_fn;
    MFnNumericAttribute numeric_fn;
    MFnMatrixAttribute matrix_fn;
    MFnUnitAttribute unit_fn;
    MFnEnumAttribute enum_fn;

	start_matrix = matrix_fn.create("startMatrix", "stm");
	matrix_fn.setStorable(true);
	matrix_fn.setKeyable(true);
	addAttribute(start_matrix);

	pole_vector_matrix = matrix_fn.create("poleVectorMatrix", "pvm");
	matrix_fn.setStorable(true);
	matrix_fn.setKeyable(true);
	addAttribute(pole_vector_matrix);

    handle_parent_matrix = matrix_fn.create("handleParentMatrix", "hpm");
    matrix_fn.setStorable(true);
    matrix_fn.setKeyable(true);
    addAttribute(handle_parent_matrix);

    handle_translate_x = numeric_fn.create("scaleTranslateX", "htx", MFnNumericData::kDouble, 0);
    numeric_fn.setStorable(true);
    numeric_fn.setWritable(true);
    numeric_fn.setHidden(true);
    addAttribute(handle_translate_x);

    handle_translate_y = numeric_fn.create("scaleTranslateY", "hty", MFnNumericData::kDouble, 0);
    numeric_fn.setStorable(true);
    numeric_fn.setWritable(true);
    numeric_fn.setHidden(true);
    addAttribute(handle_translate_y);

    handle_translate_z = numeric_fn.create("scaleTranslateZ", "htz", MFnNumericData::kDouble, 0);
    numeric_fn.setStorable(true);
    numeric_fn.setWritable(true);
    numeric_fn.setHidden(true);
    addAttribute(handle_translate_z);

    handle_translate = compound_fn.create("handleTranslate", "htl");
    compound_fn.addChild(handle_translate_x);
    compound_fn.addChild(handle_translate_y);
    compound_fn.addChild(handle_translate_z);
    compound_fn.setStorable(true);
    compound_fn.setWritable(true);
    compound_fn.setHidden(true);
    addAttribute(handle_translate);

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

    preferred_angle_input_x = unit_fn.create("preferredAngleInputX", "pix", MFnUnitAttribute::kAngle, 0);
    unit_fn.setStorable(true);
    unit_fn.setWritable(true);
    unit_fn.setHidden(true);
    addAttribute(preferred_angle_input_x);

    preferred_angle_input_y = unit_fn.create("preferredAngleInputY", "piy", MFnUnitAttribute::kAngle, 0);
    unit_fn.setStorable(true);
    unit_fn.setWritable(true);
    unit_fn.setHidden(true);
    addAttribute(preferred_angle_input_y);

    preferred_angle_input_z = unit_fn.create("preferredAngleInputZ", "piz", MFnUnitAttribute::kAngle, 0);
    unit_fn.setStorable(true);
    unit_fn.setWritable(true);
    unit_fn.setHidden(true);
    addAttribute(preferred_angle_input_z);

    preferred_angle_input = compound_fn.create("preferredAngleInput", "pai");
    compound_fn.addChild(preferred_angle_input_x);
    compound_fn.addChild(preferred_angle_input_y);
    compound_fn.addChild(preferred_angle_input_z);
    compound_fn.setStorable(true);
    compound_fn.setKeyable(true);
    compound_fn.setHidden(true);
    addAttribute(preferred_angle_input);

	start_scale = numeric_fn.create("startScale", "sts", MFnNumericData::kDouble, 1);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setMin(0.001);
	addAttribute(start_scale);

	end_scale = numeric_fn.create("endScale", "eds", MFnNumericData::kDouble, 1);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setMin(0.001);
	addAttribute(end_scale);

    direction = numeric_fn.create("direction", "dir", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    numeric_fn.setHidden(true);
    addAttribute(direction);

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

    twist = unit_fn.create("twist", "tws", MFnUnitAttribute::kAngle, 0);
    unit_fn.setStorable(true);
    unit_fn.setKeyable(true);
    addAttribute(twist);

	slide = numeric_fn.create("slide", "sld", MFnNumericData::kDouble, 0);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setMin(-1);
	numeric_fn.setMax(1);
	addAttribute(slide);

    volumetric = numeric_fn.create("volumetric", "vol", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    numeric_fn.setMin(0);
    numeric_fn.setMax(1);
    addAttribute(volumetric);

	stretch = numeric_fn.create("stretch", "stc", MFnNumericData::kDouble, 0);
	numeric_fn.setStorable(true);
	numeric_fn.setKeyable(true);
	numeric_fn.setMin(0);
	numeric_fn.setMax(1);
	addAttribute(stretch);

    softness = numeric_fn.create("softness", "sof", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    addAttribute(softness);

    preferred_angle_blend = numeric_fn.create("preferredAngleBlend", "pab", MFnNumericData::kDouble, 7);
    numeric_fn.setStorable(true);
    numeric_fn.setKeyable(true);
    addAttribute(preferred_angle_blend);

    // Outputs

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

    start_output_scale = numeric_fn.create("startOutputScale", "sos", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(false);
    numeric_fn.setKeyable(false);
    numeric_fn.setWritable(false);
    addAttribute(start_output_scale);

    end_output_scale = numeric_fn.create("endOutputScale", "eos", MFnNumericData::kDouble, 1);
    numeric_fn.setStorable(false);
    numeric_fn.setKeyable(false);
    numeric_fn.setWritable(false);
    addAttribute(end_output_scale);

    preferred_angle_output_x = unit_fn.create("preferredAngleOutputX", "pox", MFnUnitAttribute::kAngle, 0.0);
    unit_fn.setStorable(false);
    unit_fn.setKeyable(false);
    unit_fn.setWritable(false);
    addAttribute(preferred_angle_output_x);

    preferred_angle_output_y = unit_fn.create("preferredAngleOutputY", "poy", MFnUnitAttribute::kAngle, 0.0);
    unit_fn.setStorable(false);
    unit_fn.setKeyable(false);
    unit_fn.setWritable(false);
    addAttribute(preferred_angle_output_y);

    preferred_angle_output_z = unit_fn.create("preferredAngleOutputZ", "poz", MFnUnitAttribute::kAngle, 0.0);
    unit_fn.setStorable(false);
    unit_fn.setKeyable(false);
    unit_fn.setWritable(false);
    addAttribute(preferred_angle_output_z);

    preferred_angle_output = compound_fn.create("preferredAngleOutput", "pao");
    compound_fn.addChild(preferred_angle_output_x);
    compound_fn.addChild(preferred_angle_output_y);
    compound_fn.addChild(preferred_angle_output_z);
    compound_fn.setStorable(false);
    compound_fn.setKeyable(false);
    compound_fn.setWritable(false);
    addAttribute(preferred_angle_output);

	attributeAffects(start_matrix, start_output);
	attributeAffects(handle_parent_matrix, start_output);
    attributeAffects(handle_translate, start_output);
	attributeAffects(stretch, start_output);
    attributeAffects(volumetric, start_output);
	attributeAffects(slide, start_output);
	attributeAffects(softness, start_output);
	attributeAffects(pole_vector_lock, start_output);
	attributeAffects(pole_vector_matrix, start_output);
    attributeAffects(direction, start_output);
	attributeAffects(global_scale, start_output);
	attributeAffects(start_scale, start_output);
	attributeAffects(start_initial_length, start_output);
    attributeAffects(preferred_angle_input, start_output);
    attributeAffects(preferred_angle_blend, start_output);

	attributeAffects(start_matrix, end_output);
	attributeAffects(handle_parent_matrix, end_output);
    attributeAffects(handle_translate, end_output);
	attributeAffects(stretch, end_output);
    attributeAffects(volumetric, end_output);
	attributeAffects(slide, end_output);
	attributeAffects(softness, start_output);
	attributeAffects(pole_vector_lock, end_output);
	attributeAffects(pole_vector_matrix, end_output);
    attributeAffects(direction, start_output);
	attributeAffects(global_scale, end_output);
	attributeAffects(end_scale, end_output);
    attributeAffects(end_initial_length, end_output);
    attributeAffects(preferred_angle_input, end_output);
    attributeAffects(preferred_angle_blend, end_output);

    attributeAffects(start_matrix, start_output_scale);
    attributeAffects(handle_parent_matrix, start_output_scale);
    attributeAffects(handle_translate, start_output_scale);
    attributeAffects(stretch, start_output_scale);
    attributeAffects(volumetric, start_output_scale);
    attributeAffects(slide, start_output_scale);
    attributeAffects(softness, start_output);
    attributeAffects(pole_vector_lock, start_output_scale);
    attributeAffects(pole_vector_matrix, start_output_scale);
    attributeAffects(direction, start_output);
    attributeAffects(global_scale, start_output_scale);
    attributeAffects(start_scale, start_output_scale);
    attributeAffects(start_initial_length, start_output_scale);
    attributeAffects(preferred_angle_input, start_output_scale);
    attributeAffects(preferred_angle_blend, start_output_scale);

    attributeAffects(start_matrix, end_output_scale);
    attributeAffects(handle_parent_matrix, end_output_scale);
    attributeAffects(handle_translate, end_output_scale);
    attributeAffects(stretch, end_output_scale);
    attributeAffects(volumetric, end_output_scale);
    attributeAffects(slide, end_output_scale);
    attributeAffects(softness, start_output);
    attributeAffects(pole_vector_lock, end_output_scale);
    attributeAffects(pole_vector_matrix, end_output_scale);
    attributeAffects(direction, start_output);
    attributeAffects(global_scale, end_output_scale);
    attributeAffects(end_scale, end_output_scale);
    attributeAffects(end_initial_length, end_output_scale);
    attributeAffects(preferred_angle_input, end_output_scale);
    attributeAffects(preferred_angle_blend, end_output_scale);

    attributeAffects(start_matrix, preferred_angle_output);
    attributeAffects(handle_parent_matrix, preferred_angle_output);
    attributeAffects(handle_translate, preferred_angle_output);
    attributeAffects(stretch, preferred_angle_output);
    attributeAffects(volumetric, preferred_angle_output);
    attributeAffects(slide, preferred_angle_output);
    attributeAffects(softness, start_output);
    attributeAffects(pole_vector_lock, preferred_angle_output);
    attributeAffects(pole_vector_matrix, preferred_angle_output);
    attributeAffects(direction, start_output);
    attributeAffects(global_scale, preferred_angle_output);
    attributeAffects(end_scale, preferred_angle_output);
    attributeAffects(end_initial_length, preferred_angle_output);
    attributeAffects(preferred_angle_input, preferred_angle_output);
    attributeAffects(preferred_angle_blend, preferred_angle_output);

	return MS::kSuccess; 

}


MStatus PiperIK::compute(const MPlug& plug, MDataBlock& data)
{
	if (plug == start_output or plug == end_output or plug == start_output_scale or plug == end_output_scale
	or plug == preferred_angle_output or plug == preferred_angle_output_x or plug == preferred_angle_output_y or plug == preferred_angle_output_z)
	{
		MMatrix start_matrix_value = data.inputValue(start_matrix).asMatrix();
		MMatrix handle_parent_matrix_value = data.inputValue(handle_parent_matrix).asMatrix();
		MMatrix pole_vector_matrix_value = data.inputValue(pole_vector_matrix).asMatrix();
        MVector handle_translate_value = data.inputValue(handle_translate).asVector();
        MVector input_angle = data.inputValue(preferred_angle_input).asVector();

		double start_initial_length_value = data.inputValue(start_initial_length).asDouble();
		double end_initial_length_value = data.inputValue(end_initial_length).asDouble();
        double preferred_angle_blend_value = data.inputValue(preferred_angle_blend).asDouble();

		double soft_value = data.inputValue(softness).asDouble();
        double slide_value = data.inputValue(slide).asDouble();
        double volumetric_value = data.inputValue(volumetric).asDouble();
        double stretch_value = data.inputValue(stretch).asDouble();
		double pole_vector_lock_value = data.inputValue(pole_vector_lock).asDouble();
		double global_scale_value = data.inputValue(global_scale).asDouble();
		double start_scale_value = data.inputValue(start_scale).asDouble();
		double end_scale_value = data.inputValue(end_scale).asDouble();
        double direction_value = data.inputValue(direction).asDouble();

        // get position vectors
        MVector start_position = getPosition(start_matrix_value);
        MMatrix handle_matrix = matrixFromVector(handle_translate_value);
        MMatrix target_matrix = handle_matrix * handle_parent_matrix_value;
        MVector end_position = getPosition(target_matrix);

		// scaling joint lengths
		start_initial_length_value *= global_scale_value;
		end_initial_length_value *= global_scale_value;
		start_initial_length_value *= start_scale_value;
		end_initial_length_value *= end_scale_value;
		double chain_initial_length = start_initial_length_value + end_initial_length_value;

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
		double slide_alpha = abs(slide_value) == 1 ? abs(slide_value) - .001 : abs(slide_value);  // prevents joint collapse
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
		if (pole_vector_lock_value > 0.001) {
            MVector pole_position = getPosition(pole_vector_matrix_value);

            double start_pole_distance = getDistance(start_position, pole_position);
            double end_pole_distance = getDistance(pole_position, end_position);

            start_output_value = lerp(start_output_value, start_pole_distance, pole_vector_lock_value);
            end_output_value = lerp(end_output_value, end_pole_distance, pole_vector_lock_value);
        }

        // joint scaling
        double normalized_distance = start_output_value / start_initial_length_value;
        normalized_distance = lerp(1.0, normalized_distance, volumetric_value);
        double start_output_scale_value = 1.0 / normalized_distance;

        double end_normalized_distance = end_output_value / end_initial_length_value;
        end_normalized_distance = lerp(1.0, end_normalized_distance, volumetric_value);
        double end_output_scale_value = 1.0 / end_normalized_distance;

        start_output_value = start_output_value * normalized_distance;
        end_output_value = end_output_value * end_normalized_distance * normalized_distance;

        // preferred angle
        double normalized_chain_length = current_chain_length / chain_initial_length;
        if (input_angle.x > input_angle.y and input_angle.x > input_angle.z)
        {
            MAngle output_angle = calculatePreferredAngle(input_angle.x, normalized_chain_length, preferred_angle_blend_value);
            data.outputValue(preferred_angle_output).set(output_angle.asRadians(), 0.0, 0.0);
        }
        else if (input_angle.y > input_angle.x and input_angle.y > input_angle.z)
        {
            MAngle output_angle = calculatePreferredAngle(input_angle.y, normalized_chain_length, preferred_angle_blend_value);
            data.outputValue(preferred_angle_output).set(0.0, output_angle.asRadians(), 0.0);
        }
        else
        {
            MAngle output_angle = calculatePreferredAngle(input_angle.z, normalized_chain_length, preferred_angle_blend_value);
            data.outputValue(preferred_angle_output).set(0.0, 0.0, output_angle.asRadians());
        }

        // output
		data.outputValue(start_output).set(start_output_value * direction_value);
		data.outputValue(start_output).setClean();

		data.outputValue(end_output).set(end_output_value * direction_value);
		data.outputValue(end_output).setClean();

        data.outputValue(start_output_scale).set(start_output_scale_value);
        data.outputValue(start_output_scale).setClean();

        data.outputValue(end_output_scale).set(end_output_scale_value);
        data.outputValue(end_output_scale).setClean();

        data.outputValue(preferred_angle_output).setClean();

    }

    return MPxTransform::compute(plug, data);

}


MAngle PiperIK::calculatePreferredAngle(const double& input_angle, const double& length, const double& blend)
{
    double sign = signOf(input_angle);
    double angle = abs(input_angle);

    double output_angle = (angle * blend) - ((angle * (blend - 1)) * length);
    output_angle = std::clamp(output_angle, 1.0, 90.0);
    output_angle *= sign;

    return MAngle(output_angle, MAngle::kDegrees);
}
