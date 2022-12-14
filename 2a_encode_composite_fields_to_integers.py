########################################################################################################################
# Author: Mike Gough
# Date Created: 09/20/2022
# Description: This script adds additional fields needed for the EEMS model that we don't want to be in the
# composite.
# 1. Integer fields created out of string fields
# 2. Duplicate fields needed more than once in the EEMS model
# It should therefore be run on the composite dataset intersected with the landscape dataset.
# created by the following model:  Combine Trail Specific and Landscape Models (vx)
########################################################################################################################

import arcpy

# Output from model 2. Prepare Reporting Units (Intersect with Landscape)
input_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Reporting_Units.gdb\DTC_Reporting_Units_Trails_Composite_Intersect_270m_v4_0_3"

def encode_string_fields_as_integers():
    
    null_integer_value = -999  

    int_fields_list = [
        {
            "orig_field_name": "surface",
            "int_field_name": "surface_int",
            "field_mapping": {
                "IMPORTED COMPACTED MATERIAL": 1,
                "NULL": 2,
                "N/A": 3,
                "AC- ASPHALT": 4,
                "NAT - NATIVE MATERIAL": 5,
                "SNOW": 6,
                "Soft": 7,
                "Hard": 8,
                "Natural Unimproved": 9,
                "Bituminous": 10,
                "Aggregate": 11,
                "Grid Rolled": 12,
                "Asphalt": 13,
                "Natural": 14,
                "Natural Surface": 15,
                "Concrete": 16,
                "Other": 17,
                "Wood Deck": 18,
                "Multi-use": 19,
                "Trail": 20,
                "Unknown": 21,
                },
                "ignore": False
        },
        {
            "orig_field_name": "grade",
            "int_field_name": "grade_int",
            "field_mapping": {
                "0-5%": 1,
                "5-8%": 2,
                "8-10%": 3,
                "10-12%": 4,
                "12-20%": 5,
                "20-30%": 6,
                "30-40%": 7,
                "40-50%": 8,
                ">50%": 9,
                "NULL": 10,
                "N/A": 11,
            },
            "ignore": False
        },
        {
            "orig_field_name": "special_mgmt_area",
            "int_field_name": "special_mgmt_area_int",
            "field_mapping": {
                "NM - NATIONAL MONUMENT": 1,
                "RNA - RESEARCH NATURAL AREA": 2,
                "WSR - SCENIC": 3,
                "WILDERNESS-placeholder for": 4,
                "WSA - WILD": 5,
                "NULL": 6,
                "N/A": 7,
                "NRA - NATIONAL RECREATION AREA": 8,
                "WSR - RECREATION": 9, # Trail segment is in a Recreation section of a Wild and Scenic River corridor
                "URA - UNROADED AREA": 10,
                "IRA - INVENTORIED ROADLESS AREA": 11,
                "WSA - WILDERNESS STUDY AREA": 12,
            },
            "ignore": False
        }

    ]
    
    existing_fields = arcpy.ListFields(input_fc)

    for int_field_dict in int_fields_list:
        if int_field_dict["ignore"] != True:
        
            orig_field_name = int_field_dict["orig_field_name"]
            int_field_name = int_field_dict["int_field_name"]
            field_mapping = int_field_dict["field_mapping"]

            print "Calculating Integer-Based Field for: " + orig_field_name

            if int_field_name not in existing_fields:
                arcpy.AddField_management(input_fc, int_field_name, "INTEGER")

            with arcpy.da.UpdateCursor(input_fc, [orig_field_name, int_field_name]) as uc:

                for row in uc:
                    if row[0] in field_mapping:
                        row[1] = field_mapping[row[0]]
                    elif str(row[0]) in field_mapping:
                         row[1] = field_mapping[str(row[0])]
                    else:
                        row[1] = null_integer_value

                    uc.updateRow(row)

def duplicate_fields(fields, dup_string_to_tack_on="_2"):
    for field in fields:
        print ("Duplicating field: " + field)
        original_field_name = field
        duplicate_field = field + dup_string_to_tack_on
        field_type = [f.type for f in arcpy.ListFields(input_fc, field)][0]
        arcpy.AddField_management(input_fc, duplicate_field, field_type)
        arcpy.CalculateField_management(input_fc, duplicate_field, "!" + original_field_name + "!", "PYTHON")


encode_string_fields_as_integers()
duplicate_fields(["surface_int", "hiker", "biker", "pack_saddle", "motorized", "stream_crossing"], "_2")
duplicate_fields(["surface_int", "hiker", "biker", "motorized", "pack_saddle"], "_3")

