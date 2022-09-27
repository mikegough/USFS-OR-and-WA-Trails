########################################################################################################################
# Author: Mike Gough
# Date Created: 09/12/2022
# Description: This script creates a common set of fields for the DTC trails composite and populates
# those fields based on information contained in the source data fields.
########################################################################################################################
import arcpy
import os 
arcpy.env.overwriteOutput = True

input_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Trails.gdb\CBI_DTC_Trails_Composite_Pre_Field_Standardization"
output_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Trails_Composite.gdb\CBI_DTC_Trails_Composite_v1_5"

intermediate_ws = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Trails.gdb"

# Make a copy of the input_fc to work on (add composite fields, etc).
input_fc_copy = intermediate_ws + os.sep + input_fc.split(os.sep)[-1] + "_Copy"
arcpy.Copy_management(input_fc, input_fc_copy)

add_composite_fields = True 

composite_fields_to_add = [
    ["original_oid",  "TEXT"],
    ["original_id",  "TEXT"],
    ["name",  "TEXT"],
    ["ownership",  "TEXT"],
    ["surface",  "TEXT"],
    ["length_miles", "TEXT"],
    ["width_ft", "TEXT"],
    ["grade", "TEXT"],
    ["type", "TEXT"],
    ["status", "TEXT"],
    ["hiker", "SHORT"],
    ["biker", "SHORT"],
    ["pack_saddle", "SHORT"],
    ["four_wheel_drive", "SHORT"],
    ["atv", "SHORT"],
    ["motorcycle", "SHORT"],
    ["motorized", "SHORT"],
    ["accessibility_status", "SHORT"],
    ["national_trail_designation", "SHORT"],
    ["special_mgmt_area", "TEXT"],
    ["notes", "TEXT", 10000],
]

# These fields aren't calculated in this script, but we want to keep them as-is in the composite output
input_fields_to_keep_as_is = [
    "stream_crossing"
]

if add_composite_fields:
    for field in composite_fields_to_add:
        # add a "c" for composite to the end of each field to avoid conflicts with existing fields
        field_name = field[0] + "_c"
        field_type = field[1]
        if len(field) == 3:
            field_length = field[2]
        else:
            field_length = "#" 
        arcpy.AddField_management(input_fc_copy, field_name, field_type, "#", "#", field_length)

all_field_names = [field.name for field in arcpy.ListFields(input_fc_copy)]
composite_field_names = [field[0] + "_c" for field in composite_fields_to_add]
#original_field_names = [field for field in all_field_names if field not in composite_field_names]


with arcpy.da.UpdateCursor(input_fc_copy, all_field_names) as uc:
    f = all_field_names  # for readability_below
    for row in uc:
        # Reset the notes field to avoid double concatenation.
        row[f.index("notes_c")] = "" 
        # USFS
        if row[f.index("original_trails_dataset_source")] == "USFS":
            # Original Trail ID 
            row[f.index("original_id_c")] = str(row[f.index("TRAIL_CN")])
            # Original OID 
            row[f.index("original_oid_c")] = str(row[f.index("USFS_ORIG_OID")])
            # Trail Name 
            row[f.index("name_c")] = row[f.index("TRAIL_NAME")]
            # Trail Ownership 
            row[f.index("ownership_c")] = "USFS"
            # Trail Surface 
            row[f.index("surface_c")] = row[f.index("TRAIL_SURFACE")]
            # Trail Length 
            row[f.index("length_miles_c")] = row[f.index("SEGMENT_LENGTH")]
            # Trail Width
            row[f.index("width_ft_c")] = row[f.index("TYPICAL_TREAD_WIDTH")]
            # Trail Grade 
            row[f.index("grade_c")] = row[f.index("TYPICAL_TRAIL_GRADE")]
            # Trail Type 
            row[f.index("type_c")] = row[f.index("TRAIL_TYPE")]
            # Trail Status
            row[f.index("status_c")] = "Open"
            # Hiker 
            if row[f.index("HIKER_PEDESTRIAN_MANAGED")]:
                row[f.index("hiker_c")] = 1
            else:
                row[f.index("hiker_c")] = 0
            # Biker
            if row[f.index("BICYCLE_MANAGED")]:
                row[f.index("biker_c")] = 1
            else:
                row[f.index("biker_c")] = 0
            # Pack & Saddle
            if row[f.index("PACK_SADDLE_MANAGED")]:
                row[f.index("pack_saddle_c")] = 1
            else:
                row[f.index("pack_saddle_c")] = 0
            # Four WD
            if row[f.index("FOURWD_MANAGED")]:
                row[f.index("four_wheel_drive_c")] = 1
            else:
                row[f.index("four_wheel_drive_c")] = 0
            # ATV
            if row[f.index("ATV_MANAGED")]:
                row[f.index("atv_c")] = 1
            else:
                row[f.index("atv_c")] = 0
            # ATV
            if row[f.index("MOTORCYCLE_MANAGED")]:
                row[f.index("motorcycle_c")] = 1
            else:
                row[f.index("motorcycle_c")] = 0
            # Motorized 
            if row[f.index("TERRA_MOTORIZED")] == 'Y':
                row[f.index("motorized_c")] = 1
            else:
                row[f.index("motorized_c")] = 0
            # Accessibility Status
            if row[f.index("ACCESSIBILITY_STATUS")] == "ACCESSIBLE":
                row[f.index("accessibility_status_c")] = 1
            else:
                row[f.index("accessibility_status_c")] = 0
            # National Trail Designation
            if row[f.index("NATIONAL_TRAIL_DESIGNATION")] in [2, 3]:
                row[f.index("national_trail_designation_c")] = 1 
            else:
                row[f.index("national_trail_designation_c")] = 0
            # Special Mgmt Area
            row[f.index("special_mgmt_area_c")] = row[f.index("SPECIAL_MGMT_AREA")]


        # USGS
        elif row[f.index("original_trails_dataset_source")] == "USGS":
            # Original Trail ID 
            row[f.index("original_id_c")] = str(row[f.index("permanentidentifier")])
            # Original OID 
            row[f.index("original_oid_c")] = str(row[f.index("USGS_ORIG_OID")])
            # Trail Name 
            row[f.index("name_c")] = row[f.index("name")]
            # Trail Ownership
            if row[f.index("name")] == "Radlands Spur":
                row[f.index("ownership_c")] = "Deschutes County"  # Source: https://www.raprd.org/radlands
            else:
                row[f.index("ownership_c")] = row[f.index("primarytrailmaintainer")]
            # Trail Surface
            row[f.index("surface_c")] = ""
            # Trail Length
            row[f.index("length_miles_c")] = row[f.index("lengthmiles")]
            # Trail Width
            row[f.index("width_ft_c")] = ""
            # Trail Grade 
            row[f.index("grade_c")] = ""
            # Trail Type
            if row[f.index("trailtype")] == 'Standard/Terra Trail':
                row[f.index("type_c")] = "TERRA"
            elif row[f.index("trailtype")] == 'Snow Trail':
                row[f.index("type_c")] = "SNOW"
            elif row[f.index("trailtype")] == 'Water Trail':
                row[f.index("type_c")] = "WATER"
            # Trail Status
            if row[f.index("name")]:
                if "closed" in row[f.index("name")].lower():
                    row[f.index("status_c")] = "Closed"
                else:
                    row[f.index("status_c")] = "Open"
            else:
                row[f.index("status_c")] = "Open"
            # Hiker
            if row[f.index("hikerpedestrian")] == "Y": #These are domain coded values. Attribute table says "Yes".
                row[f.index("hiker_c")] = 1
            else:
                row[f.index("hiker_c")] = 0
            # Biker
            if row[f.index("bicycle")] == "Y":
                row[f.index("biker_c")] = 1
            else:
                row[f.index("biker_c")] = 0
            # Pack & Saddle
            if row[f.index("packsaddle")] == "Y":
                row[f.index("pack_saddle_c")] = 1
            else:
                row[f.index("pack_saddle_c")] = 0
            # Four WD
            if row[f.index("ohvover50inches")] == "Y":
                row[f.index("four_wheel_drive_c")] = 1
            else:
                row[f.index("four_wheel_drive_c")] = 0
            # ATV
            if row[f.index("atv")] == "Y":
                row[f.index("atv_c")] = 1
            else:
                row[f.index("atv_c")] = 0
            # Motorcycle
            if row[f.index("motorcycle")] == "Y":
                row[f.index("motorcycle_c")] = 1
            else:
                row[f.index("motorcycle_c")] = 0
            # Motorized
            if row[f.index("ohvover50inches")] == "Y" or row[f.index("atv")] == "Y" or row[f.index("motorcycle")] == "Y":
                row[f.index("motorized_c")] = 1
            else:
                row[f.index("motorized_c")] = 0
            # Accessibility Status
            row[f.index("accessibility_status_c")] = 0
            # National Trail Designation
            if row[f.index("nationaltraildesignation")]:
                row[f.index("national_trail_designation_c")] = 1
            else:
                row[f.index("national_trail_designation_c")] = 0
            # Special Mgmt Area
            row[f.index("special_mgmt_area_c")] = ""

        # City of Bend
        elif row[f.index("original_trails_dataset_source")] == "City of Bend":
            # Original Trail ID
            row[f.index("original_id_c")] = "" 
            # Original OID 
            row[f.index("original_oid_c")] = str(row[f.index("CITY_OF_BEND_ORIG_OID")])
            # Trail Name
            row[f.index("name_c")] = row[f.index("TRAIL_NAME")]
            # Trail Ownership 
            row[f.index("ownership_c")] = row[f.index("Ownership")]
            # Trail Surface
            row[f.index("surface_c")] = row[f.index("Surface_Ma")]
            # Trail Length
            row[f.index("length_miles_c")] = round(float(row[f.index("Length")]), 3)
            # Trail Width
            row[f.index("width_ft_c")] = ""
            # Trail Grade
            row[f.index("grade_c")] = ""
            # Trail Type 
            if row[f.index("Type")] != "" and row[f.index("Type")] != " ":
                row[f.index("type_c")] = "TERRA" + "(" + row[f.index("Type")] + ")"
            else: 
                row[f.index("type_c")] = "TERRA"
                row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'Planned trails have Null values in the type field and are assumed to be "TERRA" trails.']))
            # Trail Status
            if "Planned" in row[f.index("Status")]:
                row[f.index("status_c")] = "Planned"
            else:
                row[f.index("status_c")] = "Open"
            # Hiker    
            row[f.index("hiker_c")] = 1
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'All Bend trails are assumed to be Hiker friendly.']))
            # Biker
            if "multi-use" in row[f.index("Type")].lower():
                row[f.index("biker_c")] = 1 
            else:
                row[f.index("biker_c")] = 1
            # Pack & Saddle
            row[f.index("pack_saddle_c")] = 0
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'Pack and Saddle believed to be prohibited on all trails in Bend including multi-use (bendoregon.gov)']))
            # Four WD
            row[f.index("four_wheel_drive_c")] = 0
            # ATV
            row[f.index("atv_c")] = 0
            # Motorcycle
            row[f.index("motorcycle_c")] = 0
            # Motorized
            row[f.index("motorized_c")] = 0
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'Motorized vehicles believed to be prohibited on all trails in Bend including multi-use (bendoregon.gov)']))
            # Accessibility Status
            row[f.index("accessibility_status_c")] = 0
            # National Trail Designation
            row[f.index("national_trail_designation_c")] = 0
            # Special Mgmt Area
            row[f.index("special_mgmt_area_c")] = ""

        # BLM 
        elif row[f.index("original_trails_dataset_source")] == "BLM":
            # Original Trail ID
            row[f.index("original_id_c")] = "" 
            # Original OID 
            row[f.index("original_oid_c")] = str(row[f.index("BLM_ORIG_OID")])
            # Trail Name
            row[f.index("name_c")] = row[f.index("TRAILNAME")]
            # Trail Ownership 
            row[f.index("ownership_c")] = row[f.index("Ownership")]
            # Trail Surface
            row[f.index("surface_c")] = row[f.index("SURFACETYP")]
            # Trail Length
            row[f.index("length_miles_c")] = round(float(row[f.index("TOTALMILES")]), 3)
            # Trail Width
            row[f.index("width_ft_c")] = row[f.index("AVGWIDTH")]
            # Trail Grade
            row[f.index("grade_c")] = ""
            # Trail Type
            if row[f.index("TRAILUSESN")] in ["NOSNOW", "UNK"]:
                row[f.index("type_c")] = "TERRA"
            else:
                row[f.index("type_c")] = "SNOW"
            # Trail Status 
            row[f.index("status_c")] = row[f.index("TRLCLOSURE")]
            # Hiker
            if "Hiking" in row[f.index("TRAILUSE")]:
                row[f.index("hiker_c")] = 1
            else:
                row[f.index("hiker_c")] = 0
            # Biker
            if "bike" in row[f.index("TRAILUSE")].lower():
                row[f.index("biker_c")] = 1
            else:
                row[f.index("biker_c")] = 1
            # Pack & Saddle
            if "equestrian" in row[f.index("TRAILUSE")].lower():
                row[f.index("pack_saddle_c")] = 1
            else:
                row[f.index("pack_saddle_c")] = 0
            # Four WD
            row[f.index("four_wheel_drive_c")] = 0
            # ATV
            row[f.index("atv_c")] = 0
            # Motorcycle
            row[f.index("motorcycle_c")] = 0
            # Motorized
            row[f.index("motorized_c")] = 0
            # Accessibility Status
            row[f.index("accessibility_status_c")] = 0
            # Accessibility Status
            if "Accessible" in row[f.index("COMMENTS")] or "ADA" in row[f.index("COMMENTS")]:
                row[f.index("accessibility_status_c")] = 1
            else:
                row[f.index("accessibility_status_c")] = 0
            # National Trail Designation
            if "national" in row[f.index("DSG_NAME")].lower():
                row[f.index("national_trail_designation_c")] = 1
            else:
                row[f.index("national_trail_designation_c")] = 0
            # Special Mgmt Area
            row[f.index("special_mgmt_area_c")] = ""

        # State Parks
        elif row[f.index("original_trails_dataset_source")] == "State Parks":
            # Original Trail ID
            row[f.index("original_id_c")] = "" 
            # Original OID
            row[f.index("original_oid_c")] = str(row[f.index("STATE_PARKS_ORIG_OID")])
            # Trail Name
            row[f.index("name_c")] = row[f.index("TRAIL_NAME")]
            # Trail Ownership 
            row[f.index("ownership_c")] = "State Parks"
            # Trail Surface
            if row[f.index("SURFACE_CLASS")] == 0 or not row[f.index("SURFACE_CLASS")]:
                row[f.index("surface_c")] = "Unknown"
            elif row[f.index("SURFACE_CLASS")] == 1:
                row[f.index("surface_c")] = "Hard"
            elif row[f.index("SURFACE_CLASS")] == 2:
                row[f.index("surface_c")] = "Soft"
            # Trail Length
            row[f.index("length_miles_c")] = round(float(row[f.index("Shape_Length")]) * 0.0006214, 3)
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'Trail Length is based on meters to miles conversion of the SHAPE_Length field']))
            # Trail Width
            row[f.index("width_ft_c")] = str(row[f.index("WIDTH")])
            # Trail Grade
            row[f.index("grade_c")] = ""
            # Trail Type
            row[f.index("type_c")] = "TERRA"
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'No information in the attribute table to indicate whether a trail is TERRA or SNOW. Assuming TERRA for state park trails.']))
            # Trail Status 
            row[f.index("status_c")] = "Open"
            # Hiker
            if row[f.index("PRIMARY_USE")] in [6, 7, 8, 11, 12]:
                row[f.index("hiker_c")] = 1
            else:
                row[f.index("hiker_c")] = 0
            # Biker
            if row[f.index("PRIMARY_USE")] in [7, 9, 11]:
                row[f.index("biker_c")] = 1
            else:
                row[f.index("biker_c")] = 1
            # Pack & Saddle
            if row[f.index("PRIMARY_USE")] in [7, 10, 12]:
                row[f.index("pack_saddle_c")] = 1
            else:
                row[f.index("pack_saddle_c")] = 0
            # All Motorized types
            if row[f.index("PRIMARY_USE")] == 13:
                # Four WD
                row[f.index("four_wheel_drive_c")] = 1
                # ATV
                row[f.index("atv_c")] = 1
                # Motorcycle
                row[f.index("motorcycle_c")] = 1
                # Motorized
                row[f.index("motorized_c")] = 1
            else:
                # Four WD
                row[f.index("four_wheel_drive_c")] = 0
                # ATV
                row[f.index("atv_c")] = 0
                # Motorcycle
                row[f.index("motorcycle_c")] = 0
                # Motorized
                row[f.index("motorized_c")] = 0
            # Accessibility Status
            if row[f.index("ADA")] == "Yes":
                row[f.index("accessibility_status_c")] = 1
            elif row[f.index("ADA")] == "No":
                row[f.index("accessibility_status_c")] = 0
            else:
                row[f.index("accessibility_status_c")] = 0
            # National Trail Designation
            row[f.index("national_trail_designation_c")] = 0
            # Special Mgmt Area
            row[f.index("special_mgmt_area_c")] = ""

        try:
            uc.updateRow(row)
        except:
            print("Bad value: " + row[f.index("notes_c")])
            row[f.index("notes_c")] = ""
            uc.updateRow(row)

composite_fields = ["composite_id", "original_trails_dataset_source"] + composite_field_names

output_fc_pre_dissolve = intermediate_ws + os.sep + output_fc.split(os.sep)[-1] + "_Pre_Dissolve"


def copy(in_fc, out_fc, keep_fields, where=''):

    """
    Creates the a pre-dissolved version of the output feature class in the intermediate workspace
    containing just the composite fields
    """

    fmap = arcpy.FieldMappings()
    fmap.addTable(in_fc)

    # get all fields
    fields = {f.name: f for f in arcpy.ListFields(in_fc)}

    # clean up field map
    for fname, fld in fields.iteritems():
        #if fld.type not in ('OID', 'Geometry') and 'shape' not in fname.lower():
        if fld.type not in ('OID', 'Geometry'):
            if fname not in keep_fields:
                fmap.removeFieldMap(fmap.findFieldMapIndex(fname))

    # copy features
    path, name = os.path.split(out_fc)
    arcpy.conversion.FeatureClassToFeatureClass(in_fc, path, name, where, fmap)
    
    for field_name in keep_fields:
        if field_name not in input_fields_to_keep_as_is:
            try:
                new_field_name = field_name.split("_c")[0] # don't want to split "stream_crossing"..
                arcpy.AlterField_management(out_fc, field_name, new_field_name)
            except:
                # Some fields we want to keep, but they aren't calculated and don't have a "_c"
                print ("Failed to rename field: " + field_name)

    return out_fc

def dissolve(in_fc, out_fields, out_fc):
    
    """ 
    Dissolves the trails feature class where the values in all the composite fields are the same in order to create
    the final output. Since the ID fields may be different, take the first ID value when trails are dissolved.
    """
    
    id_fields = ["composite_id", "original_id", "original_oid"]
    dissolve_fields = ";".join([field for field in out_fields if field not in id_fields])
    statistics_fields = ";".join([field + " FIRST" for field in id_fields])

    arcpy.Dissolve_management(in_features=in_fc,
                              out_feature_class=out_fc,
                              dissolve_field=dissolve_fields,
                              statistics_fields=statistics_fields,
                              multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

    for id_field in id_fields:
        # Remove "FIRST_" from the id fields created using the FIRST statistic. 
        old_id_field_name = "FIRST_" + id_field 
        new_id_field_name = id_field 
        arcpy.AlterField_management(out_fc, old_id_field_name, new_id_field_name)


####### COPY with only fields wanting to keep ##########################################################################
fields_to_keep_in_copy = composite_fields + input_fields_to_keep_as_is
copy(input_fc_copy, output_fc_pre_dissolve, fields_to_keep_in_copy)

####### DISSOLVE #######################################################################################################
# Dissolving on all composite fields and "input_fields_to_keep as is" (e.g., stream_crossing).
# Should be the same as the fields in the "fields_to_keep_in_copy" list, but may want to change it.
final_output_fields = [composite_field.split("_c")[0] for composite_field in composite_fields] + input_fields_to_keep_as_is
dissolve(output_fc_pre_dissolve, final_output_fields, output_fc)