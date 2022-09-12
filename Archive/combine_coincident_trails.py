import arcpy
arcpy.env.overwriteOutput = True
input_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Inputs\Trails.gdb\Trails_Merge_Deschutes_County"
output_fc = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Intermediate\Trails.gdb\Trails_Merge_Deschutes_County_Delete_Identical"
identical_table = r"P:\Projects3\USFS_OR_and_WA_Trails_2020_mike_gough\Tasks\EEMS_Modeling_Trail_Specific\Data\Inputs\Trails.gdb\Identical_Trails_Table"
xy_tolerance = 1

if not arcpy.Exists(identical_table):
    arcpy.FindIdentical_management(input_fc, identical_table, "SHAPE", xy_tolerance)

arcpy.Copy_management(input_fc, output_fc)

identical_dict = {}

with arcpy.da.SearchCursor(identical_table, ["IN_FID", "FEAT_SEQ"]) as sc:
    for row in sc:
        in_fid = row[0]
        feat_seq = row[1]
        if feat_seq not in identical_dict: 
            identical_dict[feat_seq] = []
        identical_dict[feat_seq].append(in_fid)
        
print identical_dict        
