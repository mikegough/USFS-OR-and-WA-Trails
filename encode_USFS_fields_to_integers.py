import arcpy

input_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Reporting_Units.gdb\DTC_Reporting_Units_Trails_Intersect_270m_v2_0_0"


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
            "orig_field_name": "TRAIL_CLASS",
            "int_field_name": "Trail_Class_Int",
            "field_mapping": {
                "1": 1,
                "2": 2,
                "3": 3,
                "4": 4,
                "5": 5,
                "N": 6,
                "NULL": 7,
            }
        },
        {
            "orig_field_name": "TERRA_MOTORIZED",
            "int_field_name": "Terra_Motorized_Int",
            "field_mapping": {
                "NULL": 1,
                None: 1,
                "X": 2,
                "N": 3,
                "Y": 4,
            }
        },
        {
            "orig_field_name": "TRAIL_SURFACE",
            "int_field_name": "Trail_Surface_Int",
            "field_mapping": {
                "IMPORTED COMPACTED MATERIAL": 1,
                "NULL": 2,
                "N/A": 3,
                "AC- ASPHALT": 4,
                "NAT - NATIVE MATERIAL": 5,
                "SNOW": 6,
                }
        },
        {
            "orig_field_name": "SURFACE_FIRMNESS",
            "int_field_name": "Surface_Firmness_Int",
            "field_mapping": {
                "N/A": 1,
                "NULL": 2,
                "VS - VERY SOFT": 3,
                "S - SOFT": 4,
                "P - PAVED": 5,
                "F - FIRM": 6,
                "H - HARD": 7,
            }
        },
        {
            "orig_field_name": "TYPICAL_TRAIL_GRADE",
            "int_field_name": "Typical_Trail_Grade_Int",
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
            }
        },
        {
            "orig_field_name": "ACCESSIBILITY_STATUS",
            "int_field_name": "Accessibility_Status_Int",
            "field_mapping": {
                "NOT ACCESSIBLE": 1,
                "NULL": 2,
                "N/A": 3,
                "ACCESSIBLE": 4,
            }
        },
        {
            "orig_field_name": "NATIONAL_TRAIL_DESIGNATION",
            "int_field_name": "National_Trail_Designation_int",
            "field_mapping": {
                "0": 0,
                "1": 1,
                "2": 2,
                "3": 3,
            }
        },
        {
            "orig_field_name": "SPECIAL_MGMT_AREA",
            "int_field_name": "Special_Mgmt_Area_Int",
            "field_mapping": {
                "NM - NATIONAL MONUMENT": 1,
                "RNA - RESEARCH NATURAL AREA": 2,
                "WSR - SCENIC": 3,
                "WILDERNESS-placeholder for": 4,
                "WSA - WILD": 5,
                "NULL": 6,
                "N/A": 7,
                "NRA - NATIONAL RECREATION AREA": 8,
                "WSR - RECREATION": 9,
                "URA - UNROADED AREA": 10,
                "IRA - INVENTORIED ROADLESS AREA": 11,
                "WSA - WILDERNESS STUDY AREA": 12,
            }
        }

    ]
    
    existing_fields = arcpy.ListFields(input_fc)

    for int_field_dict in int_fields_list:
        
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
                
#calculate_allowed_uses()
calculate_integer_categories()