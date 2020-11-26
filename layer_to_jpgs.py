#set multi-processing
arcpy.env.parallelProcessingFactor="6"
#arcpy.env.parallelProcessingFactor="6"

#Set current workspace as the Map Document
mxd=arcpy.mapping.MapDocument("CURRENT")
#The first DataFrame would be the only one data frame
df=arcpy.mapping.ListDataFrames(mxd)[0]

def convert(data):
    '''
    '''
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            l.visible=True
            arcpy.RefreshActiveView()
            arcpy.mapping.ExportToPNG(mxd,"D:/Research/GIFs/"+data+"/"+l.name)
            l.visible=False
            
convert("GSMaP_Mon")
convert("NDVI_20")