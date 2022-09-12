import arcpy
import os 
arcpy.env.overwriteOutput = True

input_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Trails.gdb\CBI_DTC_Trails_Composite_Pre_Field_Standardization"
output_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Reporting_Units.gdb\CBI_DTC_Trails_Composite_v1_1"

intermediate_ws = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Trails.gdb"

# Make a copy of the input_fc to work on (add composite fields, etc).
input_fc_copy = intermediate_ws + os.sep + input_fc.split(os.sep)[-1] + "_Copy"
arcpy.Copy_management(input_fc, input_fc_copy)

add_composite_fields = True 

composite_fields_to_add = [
    ["original_oid",  "TEXT"],
    ["original_id",  "TEXT"],
    ["trail_name",  "TEXT"],
    ["trail_ownership",  "TEXT"],
    ["trail_surface",  "TEXT"],
    ["trail_length_miles", "TEXT"],
    ["trail_width_ft", "TEXT"],
    ["trail_grade", "TEXT"],
    ["trail_type", "TEXT"],
    ["trail_status", "TEXT"],
    ["hiker", "SHORT"],
    ["biker", "SHORT"],
    ["pack_saddle", "SHORT"],
    ["four_wheel_drive", "SHORT"],
    ["atv", "SHORT"],
    ["motorcycle", "SHORT"],
    ["motorized", "SHORT"],
    ["accessibility_status", "TEXT"],
    ["national_trail_designation", "SHORT"],
    ["notes", "TEXT", 10000],
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
            row[f.index("trail_name_c")] = row[f.index("TRAIL_NAME")]
            # Trail Ownership 
            row[f.index("trail_ownership_c")] = "USFS"
            # Trail Surface 
            row[f.index("trail_surface_c")] = row[f.index("TRAIL_SURFACE")]
            # Trail Length 
            row[f.index("trail_length_miles_c")] = row[f.index("SEGMENT_LENGTH")]
            # Trail Width
            row[f.index("trail_width_ft_c")] = row[f.index("TYPICAL_TREAD_WIDTH")]
            # Trail Grade 
            row[f.index("trail_grade_c")] = row[f.index("TYPICAL_TRAIL_GRADE")]
            # Trail Type 
            row[f.index("trail_type_c")] = row[f.index("TRAIL_TYPE")]
            # Trail Status
            row[f.index("trail_status_c")] = "Open"
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
            if row[f.index("TERRA_MOTORIZED")]:
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

        # USGS
        elif row[f.index("original_trails_dataset_source")] == "USGS":
            # Original Trail ID 
            row[f.index("original_id_c")] = str(row[f.index("PERMANENT_IDENTIFIER")])
            # Original OID 
            row[f.index("original_oid_c")] = str(row[f.index("USGS_ORIG_OID")])
            # Trail Name 
            row[f.index("trail_name_c")] = row[f.index("NAME")]
            # Trail Ownership 
            if "Cline Butte" in row[f.index("NAME")] or "Connector" in row[f.index("NAME")]: 
                row[f.index("trail_ownership_c")] = "BLM"  # Source: https://www.mtbproject.com/trail/7001860/cline-butte-3-downhill
            elif row[f.index("NAME")] == "Dry Canyon Trail": 
                row[f.index("trail_ownership_c")] = "City of Redmond"  # Source: https://www.redmondoregon.gov/Home/Components/FacilityDirectory/FacilityDirectory/24/2751
            elif row[f.index("NAME")] == "Radlands Spur": 
                row[f.index("trail_ownership_c")] = "Deschutes County"  # Source: https://www.raprd.org/radlands
            # Trail Surface
            row[f.index("trail_surface_c")] = ""
            # Trail Length
            row[f.index("trail_length_miles_c")] = float(row[f.index("Shape_Length")]) * 0.0006214
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'Trail Length is based on meters to miles conversion of the SHAPE_Length field']))
            # Trail Width
            row[f.index("trail_width_ft_c")] = ""
            # Trail Grade 
            row[f.index("trail_grade_c")] = ""
            # Trail Type
            if row[f.index("FCODE")] == 20602:
                row[f.index("trail_type_c")] = "TERRA"
            elif row[f.index("FCODE")] == 20606:
                    row[f.index("trail_type_c")] = "SNOW"
            elif row[f.index("FCODE")] == 20604:
                row[f.index("trail_type_c")] = "WATER"
            # Trail Status
            row[f.index("trail_status_c")] = "Open"
            # Hiker
            row[f.index("hiker_c")] = 1
            # Biker
            row[f.index("biker_c")] = 1
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'The USGS trails in this dataset all originate from IMBA Recreational Equipment Inc and appear to all be hiker-biker allowed.']))
            # Pack & Saddle
            if "Cline Butte" in row[f.index("NAME")]:
                row[f.index("pack_saddle_c")] = 1
            else:
                row[f.index("pack_saddle_c")] = 0
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'The Cline Butte trails are part of the Maston Trail system and also permit pack/saddle. https://www.blm.gov/visit/maston-trail-system']))
            # Four WD
            row[f.index("four_wheel_drive_c")] = 0
            # ATV
            row[f.index("atv_c")] = 0
            # Motorcycle
            row[f.index("motorcycle_c")] = 0
            # Motorized
            row[f.index("motorized_c")] = 0
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'Motorized vehicles are believed to be prohibited on the remaining USGS trails in the Cline Butte/Maston Trail System and Radlands']))
            # Accessibility Status
            row[f.index("accessibility_status_c")] = ""
            # National Trail Designation
            if "national" in row[f.index("SOURCE_DATADESC")].lower():
                row[f.index("national_trail_designation_c")] = 1
            else:
                row[f.index("national_trail_designation_c")] = 0

        # City of Bend
        elif row[f.index("original_trails_dataset_source")] == "City of Bend":
            # Original Trail ID
            row[f.index("original_id_c")] = "" 
            # Original OID 
            row[f.index("original_oid_c")] = str(row[f.index("CITY_OF_BEND_ORIG_OID")])
            # Trail Name
            row[f.index("trail_name_c")] = row[f.index("TRAIL_NAME")]
            # Trail Ownership 
            row[f.index("trail_ownership_c")] = row[f.index("Ownership")]
            # Trail Surface
            row[f.index("trail_surface_c")] = row[f.index("Surface_Ma")]
            # Trail Length
            row[f.index("trail_length_miles_c")] = round(float(row[f.index("LENGTH")]), 3)
            # Trail Width
            row[f.index("trail_width_ft_c")] = ""
            # Trail Grade
            row[f.index("trail_grade_c")] = ""
            # Trail Type 
            if row[f.index("Type")] != "" and row[f.index("Type")] != " ":
                row[f.index("trail_type_c")] = "TERRA" + "(" + row[f.index("Type")] + ")"
            else: 
                row[f.index("trail_type_c")] = "TERRA" 
                row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'Planned trails have Null values in the type field and are assumed to be "TERRA" trails.']))
            # Trail Status
            if "Planned" in row[f.index("Status")]:
                row[f.index("trail_status_c")] = "Planned"
            else:
                row[f.index("trail_status_c")] = "Open"
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
            row[f.index("accessibility_status_c")] = ""
            # National Trail Designation
            row[f.index("national_trail_designation_c")] = 0


        # BLM 
        elif row[f.index("original_trails_dataset_source")] == "BLM":
            # Original Trail ID
            row[f.index("original_id_c")] = "" 
            # Original OID 
            row[f.index("original_oid_c")] = str(row[f.index("BLM_ORIG_OID")])
            # Trail Name
            row[f.index("trail_name_c")] = row[f.index("TRAILNAME")]
            # Trail Ownership 
            row[f.index("trail_ownership_c")] = row[f.index("Ownership")]
            # Trail Surface
            row[f.index("trail_surface_c")] = row[f.index("SURFACETYP")]
            # Trail Length
            row[f.index("trail_length_miles_c")] = round(float(row[f.index("TOTALMILES")]), 3)
            # Trail Width
            row[f.index("trail_width_ft_c")] = row[f.index("AVGWIDTH")]
            # Trail Grade
            row[f.index("trail_grade_c")] = ""
            # Trail Type
            if row[f.index("TRAILUSESN")] in ["NOSNOW", "UNK"]:
                row[f.index("trail_type_c")] = "TERRA"
            else:
                row[f.index("trail_type_c")] = "SNOW"
            # Trail Status 
            row[f.index("trail_status_c")] = row[f.index("TRLCLOSURE")]
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
            row[f.index("accessibility_status_c")] = ""
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

        # State Parks
        elif row[f.index("original_trails_dataset_source")] == "State Parks":
            # Original Trail ID
            row[f.index("original_id_c")] = "" 
            # Original OID
            row[f.index("original_oid_c")] = str(row[f.index("STATE_PARKS_ORIG_OID")])
            # Trail Name
            row[f.index("trail_name_c")] = row[f.index("TRAIL_NAME")]
            # Trail Ownership 
            row[f.index("trail_ownership_c")] = "State Parks"
            # Trail Surface
            if row[f.index("SURFACE_CLASS")] == 0 or not row[f.index("SURFACE_CLASS")]:
                row[f.index("trail_surface_c")] = "Unknown"
            elif row[f.index("SURFACE_CLASS")] == 1:
                row[f.index("trail_surface_c")] = "Hard"
            elif row[f.index("SURFACE_CLASS")] == 2:
                row[f.index("trail_surface_c")] = "Soft" 
            # Trail Length
            row[f.index("trail_length_miles_c")] = round(float(row[f.index("Shape_Length")]) * 0.0006214, 3)
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'Trail Length is based on meters to miles conversion of the SHAPE_Length field']))
            # Trail Width
            row[f.index("trail_width_ft_c")] = str(row[f.index("WIDTH")])
            # Trail Grade
            row[f.index("trail_grade_c")] = ""
            # Trail Type
            row[f.index("trail_type_c")] = "TERRA"
            row[f.index("notes_c")] = ' | '.join(filter(None, [row[f.index("notes_c")], 'No information in the attribute table to indicate whether a trail is TERRA or SNOW. Assuming TERRA for state park trails.']))
            # Trail Status 
            row[f.index("trail_status_c")] = "Open"
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
                row[f.index("accessibility_status_c")] = ""
            # National Trail Designation
            row[f.index("national_trail_designation_c")] = 0

        try:
            uc.updateRow(row)
        except:
            print("Bad value: " + row[f.index("notes_c")])
            row[f.index("notes_c")] = ""
            uc.updateRow(row)

def copy_fc_keep_composite_fields(in_fc, out_fc, keep_fields, where=''):
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
        new_field_name = field_name.split("_c")[0]
        arcpy.AlterField_management(out_fc, field_name, new_field_name)

    return out_fc


def dissolve(input_Fc):
    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
    # The following inputs are layers or table views: "CBI_DTC_Trails_Composite_v1_1"
    arcpy.Dissolve_management(in_features=input_fc,
                              out_feature_class=output_fc
                              dissolve_field = 
                              dissolve_field=original_trails_dataset_source;trail_name;trail_ownership;trail_surface;trail_length_miles;trail_width_ft;trail_grade;trail_type;trail_status;hiker;biker;pack_saddle;four_wheel_drive;atv;motorcycle;motorized;accessibility_status;national_trail_designation;notes",
                              statistics_fields="composite_id FIRST;original_oid FIRST;original_id FIRST",
                              multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

output_fields =  ["composite_id", "original_trails_dataset_source"] + composite_field_names
    
copy_fc_keep_composite_fields(input_fc_copy, output_fc, output_fields)
dissolve(input_fc_copy, output_fc)
