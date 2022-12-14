########################################################################################################################
# Author: Mike Gough
# Date Created: 09/12/2022
# Description: This script creates the DTC Trails Composite
# The input to this script is the output from the following model:  1. Create DTC Trail Composite (Reporting Units).
# To create the composite, this script performs the following steps:
# 1. It creates a common set of "composite" fields
# 2. It populates those fields based on information contained in the source data fields.
# 3. It dissolves all trails based on the trail name, but prior to doing that, it sets the other fields to the same
# value for all trail segments that have the same trail name (so that these fields can be used in the dissolve and be
# preserved in the dissolved output). This is done using one of three approaches. The user decides which fields
# get passed in to each function:
# A. Find True (if any trail segments are true, all trail segments are true)
# B. Longest Length (Keep the field value associated with the longest trail segment)
# C. Concatenate (Concatenates all the field values from the trail segments.
# Refer to the comments in each function for more information.
########################################################################################################################
import arcpy
import os 
arcpy.env.overwriteOutput = True

input_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Trails.gdb\CBI_DTC_Trails_Composite_Pre_Field_Standardization"
output_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Trails_Composite.gdb\CBI_DTC_Trails_Composite_v1_6"

intermediate_ws = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Trails.gdb"

input_fc_copy = intermediate_ws + os.sep + input_fc.split(os.sep)[-1] + "_Copy"
output_fc_pre_dissolve = intermediate_ws + os.sep + output_fc.split(os.sep)[-1] + "_Pre_Dissolve"
output_fc_pre_dissolve_combine_segment_values = intermediate_ws + os.sep + output_fc.split(os.sep)[-1] + "_Combine_Segment_Values"

composite_fields_to_add = [
    #["original_oid", "TEXT"], # since we are dissolving now, these id values are meaningless.
    #["original_id", "TEXT"],
    ["name", "TEXT"],
    ["ownership", "TEXT", 1000],
    ["surface", "TEXT"],
    #["length_miles", "DOUBLE"],
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

# original_field_names = [field for field in all_field_names if field not in composite_field_names]
composite_field_names = [field[0] + "_c" for field in composite_fields_to_add]
composite_fields = ["original_trails_dataset_source", "stream_crossing"] + composite_field_names

def add_composite_fields(input_fc_copy):
    '''
    Adds the composite fields to the copy of the input feature class.
    These fields  have a "_c" at the end to avoid conflicts with existing fields.
    '''

    print("Adding composite fields...")

    for field in composite_fields_to_add:
        # add a "c" for composite to the end of each field to avoid conflicts with existing fields
        field_name = field[0] + "_c"
        field_type = field[1]
        if len(field) == 3:
            field_length = field[2]
        else:
            field_length = "#"
        arcpy.AddField_management(input_fc_copy, field_name, field_type, "#", "#", field_length)


def populate_composite_fields(input_fc_copy):
    '''
    Populates the composite fields using information from different fields from each dataset source
    '''

    print("Populating composite fields...")

    all_field_names = [field.name for field in arcpy.ListFields(input_fc_copy)]
    with arcpy.da.UpdateCursor(input_fc_copy, all_field_names) as uc:
        f = all_field_names  # for readability_below
        for row in uc:
            # Reset the notes field to avoid double concatenation.
            row[f.index("notes_c")] = ""
            # USFS
            if row[f.index("original_trails_dataset_source")] == "USFS":
                # Original Trail ID
                #row[f.index("original_id_c")] = str(row[f.index("TRAIL_CN")])
                # Original OID
                #row[f.index("original_oid_c")] = str(row[f.index("USFS_ORIG_OID")])
                # Trail Name
                row[f.index("name_c")] = row[f.index("TRAIL_NAME")]
                # Trail Ownership
                row[f.index("ownership_c")] = "USFS"
                # Trail Surface
                row[f.index("surface_c")] = row[f.index("TRAIL_SURFACE")]
                # Trail Length
                #row[f.index("length_miles_c")] = row[f.index("SEGMENT_LENGTH")]
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
                #row[f.index("original_id_c")] = str(row[f.index("permanentidentifier")])
                # Original OID
               # row[f.index("original_oid_c")] = str(row[f.index("USGS_ORIG_OID")])
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
                #row[f.index("length_miles_c")] = row[f.index("lengthmiles")]
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
                #row[f.index("original_id_c")] = ""
                # Original OID
                #row[f.index("original_oid_c")] = str(row[f.index("CITY_OF_BEND_ORIG_OID")])
                # Trail Name
                row[f.index("name_c")] = row[f.index("TRAIL_NAME")]
                # Trail Ownership
                row[f.index("ownership_c")] = row[f.index("Ownership")]
                # Trail Surface
                row[f.index("surface_c")] = row[f.index("Surface_Ma")]
                # Trail Length
                #row[f.index("length_miles_c")] = round(float(row[f.index("Length")]), 3)
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
                #row[f.index("original_id_c")] = ""
                # Original OID
                #row[f.index("original_oid_c")] = str(row[f.index("BLM_ORIG_OID")])
                # Trail Name
                row[f.index("name_c")] = row[f.index("TRAILNAME")]
                # Trail Ownership
                row[f.index("ownership_c")] = row[f.index("Ownership")]
                # Trail Surface
                row[f.index("surface_c")] = row[f.index("SURFACETYP")]
                # Trail Length
                #row[f.index("length_miles_c")] = round(float(row[f.index("TOTALMILES")]), 3)
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
                #row[f.index("original_id_c")] = ""
                # Original OID
                #row[f.index("original_oid_c")] = str(row[f.index("STATE_PARKS_ORIG_OID")])
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
                #row[f.index("length_miles_c")] = round(float(row[f.index("Shape_Length")]) * 0.0006214, 3)
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


def keep_only_composite_fields(input_fc_copy, output_fc_pre_dissolve, where=""):
    """
    Creates a pre-dissolved version of the output feature class in the intermediate workspace
    containing just the composite fields(removes the original data source fields used to populate the composite fields).
    """

    print("Creating a new feature class with only the composite fields...")
    print(output_fc_pre_dissolve)


    fmap = arcpy.FieldMappings()
    fmap.addTable(input_fc_copy)

    # get all fields
    fields = {f.name: f for f in arcpy.ListFields(input_fc_copy)}

    # clean up field map
    for fname, fld in fields.iteritems():
        #if fld.type not in ('OID', 'Geometry') and 'shape' not in fname.lower():
        if fld.type not in ('OID', 'Geometry'):
            if fname not in composite_fields:
                fmap.removeFieldMap(fmap.findFieldMapIndex(fname))

    # copy features
    path, name = os.path.split(output_fc_pre_dissolve)
    arcpy.conversion.FeatureClassToFeatureClass(input_fc_copy, path, name, where, fmap)
    
    for field_name in composite_fields:
        try:
            new_field_name = field_name.rstrip("_c")
            arcpy.AlterField_management(output_fc_pre_dissolve, field_name, new_field_name)
        except:
            # Some fields we want to keep, but they aren't calculated and don't have a "_c"
            print ("Failed to rename field: " + field_name)

    return output_fc_pre_dissolve


def name_nameless_trails(output_fc_pre_dissolve):
    '''
    Renames nameless trail segments so that they don't all get dissolved into one.
    '''

    print("Giving names to nameless trails...")

    count = 1
    with arcpy.da.UpdateCursor(output_fc_pre_dissolve, ["name"]) as uc:
        for row in uc:
            if row[0] == '0':
                new_name = "No Name Trail #" + str(count)
                row[0] = new_name
            count += 1
            uc.updateRow(row)


def combine_segment_values_find_true(fields):

    """
    For each field passed into this function, determine whether or not any trail segment for a given trail
    has a value of 1.

    In other words, if any of the segments have a 1 in the field, this will set the field value to 1 for all segments.

    Example: if bikers are allowed on any of the segments, all segments will get a field value of 1 to indicate
    that the trail does allow bikers.
    """
    print("Combining trail segment values ('Find True')")

    for field in fields:
        d = {}
        # Create a dictionary that stores the trail name and a 1 or a zero for the field if any of the trail segments
        # have a 1 in that field.
        # Example: {"Trail 1": 1}

        with arcpy.da.SearchCursor(output_fc_pre_dissolve_combine_segment_values, ["name", field, "Shape_Length"]) as sc:
            for row in sc:
                name = row[0]
                field_value = row[1]
                if name not in d:
                    d[name] = 0
                # if none of the segments have a 1, the dictionary will just store a 0 for the trail name.
                if field_value == 1 or field_value == '1':
                    d[name] = field_value

        # Update the field to store a 1 if any of the line segments among trails with the same name have a value of 1.
        with arcpy.da.UpdateCursor(output_fc_pre_dissolve_combine_segment_values, ["name", field]) as uc:
            for row in uc:
                name = row[0]
                # the dictionary will have either a 1 or a zero.
                row[1] = d[name]
                uc.updateRow(row)


def combine_segment_values_longest_length(fields):

    """
    For each field passed into this function, determine what the dominant value is across all trail segments for a given
    trail (i.e. line segments with the same name) based on the value associated with the longest trail segment.

    For example, if a given trail (lines having the same name) has one segment that is 5 miles of Asphalt, and another
    segment that has 2 miles of Natural, his function will recalculate the the value in the surface field to be
    Asphalt for each segment since the trail is mostly Asphalt.
    """
    #fields = [field.name for field in arcpy.ListFields(output_fc_pre_dissolve) if field.name not in ('Shape', 'OBJECTID')]

    print("Combining trail segment values ('Longest Length')")

    for field in fields:
        d = {}
        # Create a dictionary that stores the max length for each category for each trail name.
        # Example: {"Trail 1": {"Aggregate": 10, "Asphalt":9}}

        with arcpy.da.SearchCursor(output_fc_pre_dissolve_combine_segment_values, ["name", field, "Shape_Length"]) as sc:
            for row in sc:
                name = row[0]
                field_category = row[1]
                length = row[2]
                if name not in d:
                    d[name] = {}
                if field_category not in d[name]:
                    d[name][field_category] = length
                # Add to the total for that category
                else:
                    d[name][field_category] += length

        #print "Fryrear Trailhead Site Trail (TEST):"
        #print d["Fryrear Trailhead Site Trail"]

        # Create a dictionary that stores the category with the longest length for each trail
        # Example: {"Trail 1": "Aggregate"}
        d_max_cat = {}
        for k, value_dict in d.iteritems():
            d_max_cat[k] = max(value_dict, key=value_dict.get)

        #print "MAX LENGTH CATEGORY: " + str(d_max_cat["Fryrear Trailhead Site Trail"])

        # Update the datast to store the max category for each trail name.
        with arcpy.da.UpdateCursor(output_fc_pre_dissolve_combine_segment_values, ["name", field]) as uc:
            for row in uc:
                name = row[0]
                # Get the category with the max length out of the dictionary
                row[1] = d_max_cat[name]
                uc.updateRow(row)


def combine_segment_values_concatenate(fields):

    """
    For each field passed into this function, concatenate the field values for all trail segments of a given trail
    (i.e. line segments with the same name).

    For example, if a trail has two line segments and one of them has an owner of "USFS" and the other has an owner
    of "BLM", this function will recalculate the ownership field for both line segments to be "USFS, BLM"
    """

    print("Combining trail segment values ('Concatenate')")

    for field in fields:
        d = {}
        # Create a dictionary that stores the max length for each category for each trail name.
        # Example: {"Trail 1": {"Aggregate": 10, "Asphalt":9}}

        with arcpy.da.SearchCursor(output_fc_pre_dissolve_combine_segment_values, ["name", field]) as sc:
            for row in sc:
                name = row[0]
                field_value = row[1].rstrip()
                if name not in d:
                    d[name] = []
                if field_value and field_value != "" and field_value not in d[name]:
                    d[name].append(field_value)
        # Update the dataset to store the max category for each trail name.
        with arcpy.da.UpdateCursor(output_fc_pre_dissolve_combine_segment_values, ["name", field]) as uc:
            for row in uc:
                name = row[0]
                # Get the category with the max length out of the dictionary
                concatenated_value = ",".join(d[name])
                row[1] = concatenated_value
                uc.updateRow(row)


def dissolve_on_composite_fields(in_fc, dissolve_fields, out_fc):

    """
    Dissolves the trails feature class where the values in all the composite fields are the same in order to create
    the final output.
    """

    print("Dissolving on composite fields...")
    print(out_fc)

    #id_fields = ["composite_id", "original_id", "original_oid"]
    #dissolve_fields = ";".join([field for field in out_fields if field not in id_fields])
    #statistics_fields = ";".join([field + " FIRST" for field in id_fields])

    arcpy.Dissolve_management(in_features=in_fc,
                              out_feature_class=out_fc,
                              dissolve_field=dissolve_fields,
                              #statistics_fields=statistics_fields,
                              multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

    print("Adding composite ID..")

    arcpy.AddField_management(out_fc, "composite_id", "LONG")
    arcpy.CalculateField_management(out_fc, "composite_id", "!OBJECTID!", "PYTHON")

######## CREATE A COPY OF THE INPUT FEATURE CLASS TO ADD THE COMPOSITE FIELDS TO #######################################
print("Making a copy of the input feature class...")
print(input_fc)
print(input_fc_copy)
arcpy.Copy_management(input_fc, input_fc_copy)

######## ADD COMPOSITE FIELDS ##########################################################################################
add_composite_fields(input_fc_copy)

######## POPULATE COMPOSITE FIELDS #####################################################################################
populate_composite_fields(input_fc_copy)

####### CREATE VERSION WITH JUST THE COMPOSITE FIELDS (AND FIELDS TO KEEP AS-IS) #######################################
keep_only_composite_fields(input_fc_copy, output_fc_pre_dissolve)

####### GIVE A NAME TO THE NAMELESS TRAILS (NO NAME TRAIL #1) ##########################################################
name_nameless_trails(output_fc_pre_dissolve)

######## CREATE VERSION IN WHICH TO COMBINE THE SEGMENT VALUES #########################################################
arcpy.Copy_management(output_fc_pre_dissolve, output_fc_pre_dissolve_combine_segment_values)

####### COMBINE SEGMENT VALUES: IF ANY OF THE TRAIL SEGMENTS HAVE A VALUE OF 1, CALCULATE ALL SEGMENT FIELD VALUES AS 1
combine_segment_values_find_true(["stream_crossing", "hiker", "biker", "pack_saddle", "four_wheel_drive", "atv", "motorcycle", "motorized", "accessibility_status", "national_trail_designation"])

####### COMBINE SEGMENT VALUES: KEEP FIELD VALUE from the segment that has THE LONGEST LENGTH #####
combine_segment_values_longest_length(["surface", "width_ft", "grade", "type", "status", "special_mgmt_area"])

####### COMBINE SEGMENT VALUES: CONCATENATE FIELD VALUES FROM EACH TRAIL SEGMENT #######################################
combine_segment_values_concatenate(["ownership"])

####### CREATE DISSOLVED VERSION (DISSOLVED ON COMPOSITE FIELDS THAT HAVE BEEN COMBINED) ##############################
dissolve_fields = [composite_field.rstrip("_c") for composite_field in composite_fields]
dissolve_on_composite_fields(output_fc_pre_dissolve_combine_segment_values, dissolve_fields, output_fc) # now using output from above.


