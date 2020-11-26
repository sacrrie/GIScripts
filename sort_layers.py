#Reference: https://gis.stackexchange.com/a/153177
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0] # Assuming one data frame
group_lyr = [lyr for lyr in arcpy.mapping.ListLayers(mxd) if lyr.isGroupLayer][0] # The temp group layer should be the only one
lyr_names = sorted(lyr.name for lyr in arcpy.mapping.ListLayers(mxd))

for name in lyr_names:
    arcpy.mapping.MoveLayer(df, group_lyr, arcpy.mapping.ListLayers(mxd, name)[0], "BEFORE")

arcpy.mapping.RemoveLayer(df, group_lyr)