import arcpy
fc = r"\\loxodonta\gis\Source_Data\transportation\county\OR\Deschutes\BLM_Trails\DeschutesTrails\DeschutesTrails.shp"
fc = r"\\loxodonta\gis\Source_Data\society\state\OR\OR_State_Parks_Trails\OPRD_Trails_forCons.gdb\OPRD_Trails_Export"
fc = r"\\loxodonta\gis\Source_Data\society\county\OR\Deschutes\Bend_Trails_From_Bend_Park_and_Recreation\BPRD_Trails_Public___All_Trails_2020\BPRD_Trails_Public.gdb\All_Trails_2020"
fc = r"\\loxodonta\gis\Source_Data\transportation\state\OR\usgs_trails\TRAN_Oregon_State_GDB\TRAN_Oregon_State_GDB.gdb\Transportation\Trans_TrailSegment"
fc = r"\\loxodonta\gis\Source_Data\transportation\national\forest_service_trails\USFS_National_Trails_Dataset_2021\S_USA.TrailNFS_Publish.gdb\TrailNFS_Publish"
fc = r"\\loxodonta\gis\Source_Data\society\state\OR\OR_State_Parks_Trails\OPRD_Trails_forCons.gdb\OPRD_Trails_Export"
fields_to_ignore = []
fields = [field.name for field in arcpy.ListFields(fc) if field.name not in fields_to_ignore]
for field in fields:
	values = []
	with arcpy.da.SearchCursor(fc, field) as sc: 
		for row in sc:
			try:
				value = row[0].encode('utf-8').strip()
			except:
				value = str(row[0])
			if value not in values and len(values) < 25:
				values.append(value)
		print("Field: " + field)
		print("Values: " + ",".join([v for v in values]))

