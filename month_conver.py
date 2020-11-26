month={
    "01":"Jan","02":"Feb","03":"Mar","04":"Apr","05":"May","06":"Jun",
    "07":"Jul","08":"Aug","09":"Sep","10":"Oct","11":"Nov","12":"Dec",
}


#set multi-processing
arcpy.env.parallelProcessingFactor="6"
#arcpy.env.parallelProcessingFactor="6"

#Set current workspace as the Map Document
mxd=arcpy.mapping.MapDocument("CURRENT")
#The first DataFrame would be the only one data frame
df=arcpy.mapping.ListDataFrames(mxd)[0]

def convert(direction):
    '''
    direction as in boolean
    True -> transform direction as key:value pair
    False -> the reverse
    '''
    for layer in arcpy.mapping.ListLayers(df):
        target=layer.name.split(".")[0].split("_")[-1]
        for month_num,month_chr in month.items():
            if direction:
                if month_num==target:
                    layer.name=layer.name.replace(target,month_chr)
            else:
                if month_chr==target:
                    layer.name=layer.name.replace(target,month_num)


convert(True)
convert(False)