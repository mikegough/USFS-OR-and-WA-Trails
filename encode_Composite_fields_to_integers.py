########################################################################################################################
# Author: Mike Gough
# Date Created: 07/26/2021
# Description: This script was used to create integer fields from text based fields in the USFS trails dataset so that
# those fields can be used in EEMS.
########################################################################################################################

import arcpy

input_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Reporting_Units.gdb\DTC_Reporting_Units_Trails_Composite_Intersect_270m_v4_0_1"


def calculate_allowed_uses():
    
    fields_to_add = ["hiker_pedestrian", "pack_and_saddle", "bicycle", "motorcycle", "atv", "FourWD_gt_50_inches"]

    for field in fields_to_add:
        arcpy.AddField_management(input_fc, field, "INTEGER")

    fields_for_uc = ["ALLOWED_TERRA_USE"] + fields_to_add

    with arcpy.da.UpdateCursor(input_fc, fields_for_uc) as uc:
        
        for row in uc:
            
            allowed_uses = row[0]
            
            if allowed_uses: 
                # Hiker/Pedestrian 
                if "1" in allowed_uses:
                    row[1] = 1
                else:
                    row[1] = 0

                # Pack and Saddle 
                if "2" in allowed_uses:
                    row[2] = 1
                else:
                    row[2] = 0

                # Bicycle 
                if "3" in allowed_uses:
                    row[3] = 1
                else:
                    row[3] = 0
                    
                # Motorcycle 
                if "4" in allowed_uses:
                    row[4] = 1
                else:
                    row[4] = 0
                    
                #ATV
                if "5" in allowed_uses:
                    row[5] = 1
                else:
                    row[5] = 0
                    
                #4WD
                if "6" in allowed_uses:
                    row[6] = 1
                else:
                    row[6] = 0
            else:
                for field_index in range(1, 7):
                    row[field_index] = 0

            uc.updateRow(row)
       
        
def calculate_integer_categories():
    
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


#calculate_allowed_uses() # Not used for composite
calculate_integer_categories()
duplicate_fields(["surface_int", "special_mgmt_area_int", "hiker", "biker", "pack_saddle", "motorized"], "_2")
duplicate_fields(["surface_int", "hiker", "biker", "motorized", "pack_saddle"], "_3")

