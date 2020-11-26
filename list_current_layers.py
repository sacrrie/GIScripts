'''
The naming conventions are presumed to be the same through out
the script. A.K.A. DataType_PlaceName_Date_Property.format
And in each of the phrases, they can be further proken down to
sub-phrases using _
'''
#set multi-processing
arcpy.env.parallelProcessingFactor="6"
#arcpy.env.parallelProcessingFactor="6"

#Set current workspace as the Map Document
mxd=arcpy.mapping.MapDocument("CURRENT")
#The first DataFrame would be the only one data frame
df=arcpy.mapping.ListDataFrames(mxd)[0]

def rename_gsmap():
    
    month={
        "01":"Jan","02":"Feb","03":"Mar","04":"Apr","05":"May","06":"Jun",
        "07":"Jul","08":"Aug","09":"Sep","10":"Oct","11":"Nov","12":"Dec",
    }
    
    for l in arcpy.mapping.ListLayers(df):
        #pre-processing GSMAP
        if l.name.find("gsmap") > -1:
            #renaming the layer names: Month attached
            file_names=l.name.split('.')
            l.name="GSMaP."+file_names[2]+"."+file_names[1][0:4]+"."+month[file_names[1][4:]]+".tif"

def clip(data="GSMaP"):
    #check the parameter for coordinates before running
    i=0
    total=len(arcpy.mapping.ListLayers(df))
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            file_names=l.name.split('.')
            #renaming the layer names: Month attached
            arcpy.Clip_management( l.name,"87.74965668 41.56768799 119.92430115 52.15429688", "D:\Research\\"+data+"_clipped\\"+"_".join(file_names[:-1])+".tif","gadm36_MNG_0", "#", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
            i+=1
            print(str(i)+"/"+str(total)+" Done")



def check_GSMaP():
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find("GSMaP") > -1:
            minimum=arcpy.GetRasterProperties_management(l.name,"MINIMUM")
            if float(minimum.getOutput(0))>10000:
                print l.name.split('_')[-2]," ",l.name.split('_')[-1][:3]
                arcpy.mapping.RemoveLayer(df,l)
            
def rename_NDVI():#adding the month function to the filename
    import datetime as dt
    month={
        "1":"Jan","2":"Feb","3":"Mar","4":"Apr","5":"May","6":"Jun",
        "7":"Jul","8":"Aug","9":"Sep","10":"Oct","11":"Nov","12":"Dec",
    }

    for l in arcpy.mapping.ListLayers(df):
        #YYYYDDD = Year and Day of Year of acquisition
        if l.name.find("A2") > -1:
            #renaming the layer names
            print("processed")
            file_names=l.name.split('_')
            dates=str(file_names[1][1:5])+" "+str(file_names[1][5:8])
            dates=dt.datetime.strptime(dates,"%Y %j")
            l.name=file_names[0]+"_"+str(dates.year)+"_"+month[str(dates.month)]+".tif"


def date_range(data="GSMaP"):
    years=set()
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            year=l.name[-12:-4]
            years.add(year)
    return years

def check_data_gaps(set1,set2):#check the two datasets discrepency in time, should be strings
    y1=date_range(set1)
    y2=date_range(set2)
    if len(y1)<len(y2):
        temp=y1
        y1=y2
        y2=temp
    return list(y1-y2)

    pass
def refresh():
    arcpy.RefreshTOC()
    arcpy.RefreshActiveView()

#TODO Refactor the raster algebra functions to make them independent(needed before processing the NDVI data)
def summation(collection):
    from arcpy.sa import *
    #input: a dictionary contians all the layers grouped by years in List
    #keys: year in string format, hashed: list contains layers
    #output: dictionary of layers that are yearly sum
    #side effect: Putting yearly_sum into current workspace
    records=[]
    for time, layers in collection.items():
        temp=CellStatistics(layers,"SUM","DATA")
        #temp=Raster(layers[0])
        #for i in layers[1:]:
        #    temp+=Raster(i)
        names=layers[0].split("_")
        temp.save("D:/Research/processed/summation/"+names[0]+"_sum_"+time+".tif")
        records.append(temp.name)
    return records
    '''
    <- ->
    reimplemented with cell statistics?
    '''
def maximum(collection):
    from arcpy.sa import *
    #input: a dictionary contians all the layers grouped by years in List
    #keys: year in string format, hashed: list contains layers
    #output: list of layers that are yearly maximum
    #side effect: Putting yearly_max into current workspace
    records=[]
    for time, layers in collection.items():
        temp=CellStatistics(layers,"MAXIMUM","DATA")
        #temp=Raster(layers[0])
        #for i in layers[1:]:
        #    temp=max(temp,Raster(i))
        names=layers[0].split("_")
        temp.save("D:/Research/processed/maximum/"+names[0]+"_max_"+time+".tif")
        records.append(temp.name)

    return records

    
def mean(name,collection):
    from arcpy.sa import *
    #input: filename and a list of layers
    #output: averaged layer and saved in the path stored as public variable(Not implemented yet)
    temp=CellStatistics(collection,"MEAN","DATA")
    #temp=Raster(collection[0])
    #for i in collection[1:]:
    #    temp+=Raster(i)
    #temp/=len(collection)
    names=collection[0].split("_")
    temp.save("D:/Research/processed/mean/"+names[0]+"_mean_"+name+".tif")

    return temp

def collection_by_time(time_unit,data):
    #TODO: Raster aggregation by its metadata/properties should be accessed through its object properties rather than the names. Refactor this function later.
    #input:
    #data: name in string, just some keywords in layer names like "NDVI" or "GSMaP"
    #time_unit: be it "month" or "year"
    #output: a yearly collection dictionary
    records={}
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            if time_unit=="year":
                unit=l.name.split('_')[-2]
            elif len(l.name)>14:
                unit=l.name.split('_')[-1][0:3]
            else:
                continue

            if unit not in records:
                records[unit]=[l.name]
            else:
                records[unit].append(l.name)
    return records
    
def conformation_NDVI():
    from arcpy.sa import *
    records=[]
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find("NDVI_") > -1:
            records.append(l.name)
    for n in records:
        temp=SetNull(n,n,"VALUE<-2000 OR VALUE>10000")
        temp*=0.0001
        temp.save("D:/Research/processed/fix/"+n)

def linear_slope(collection):
    #input: list of rasters' layer names
    #output: the linear slope of the trend presented on an raster
    #reference: https://gis.stackexchange.com/questions/65787/making-linear-regression-across-multiple-raster-layers-using-arcgis-desktop/65841#65841
    from arcpy.sa import *
    
    n=len(collection)
    temp=((12-6*(n+1))/(n*3.0 -n))*Raster(collection[0])
    temp=Con(IsNull(collection[0]),collection[0],temp)
    for i in range(2,n+1):
        coefficient=(12*i-6*(n+1))/(n*3.0 -n)
        temp+=coefficient*Raster(collection[i-1])
        temp=Con(IsNull(collection[i-1]),collection[i-1],temp)

        
    names=collection[0].split("_")
    temp.save("D:/Research/processed/linear_slope/"+names[0]+"_linear_slope.tif")
    return temp

'''
DEV Block

#------------------------------------------------
#check what months lack in NDVI compared to GSMaP
ans=check_data_gaps("GSMaP","NDVI")
ans.sort()
for i in ans:
    print(str(i).replace("_"," "))
#------------------------------------------------
#get the monthly mean of GSMaP
monthly_rec=collection_by_time("month","GSMaP")
for time, layers in monthly_rec.items():
    mean(time,layers)

#------------------------------------------------
#get the yearly mean of GSMaP

yearly_rec=[]
for l in arcpy.mapping.ListLayers(df):
    if l.name.find("GSMaP_2") > -1:
        yearly_rec.append(l.name)
mean("yearly_avg",yearly_rec)
'''



#rename_gsmap()
#rename_NDVI()
#refresh()
#clip("NDVI")
#clip()
#check_GSMaP()
#conformation_NDVI()
#yearly_rec=collection_by_time("year","GSMaP")
#yearly_rec=summation(yearly_rec)
#NDVI_yearly_rec=collection_by_time("year","NDVI")
#NDVI_yearly_rec=maximum(NDVI_yearly_rec)
#_=input("properly moved files?")
#mean("yearly_avg",NDVI_yearly_rec)

NDVI_yearly_rec=[]
for l in arcpy.mapping.ListLayers(df):
    if l.name.find("NDVI_max") > -1:
        NDVI_yearly_rec.append(l.name)
linear_slope(NDVI_yearly_rec)

GSMaP_yearly_rec=[]
for l in arcpy.mapping.ListLayers(df):
    if l.name.find("GSMaP_2") > -1:
        GSMaP_yearly_rec.append(l.name)
linear_slope(GSMaP_yearly_rec)
