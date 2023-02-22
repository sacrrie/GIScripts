import arcpy
from arcpy.sa import *

# Set multi-processing
arcpy.env.parallelProcessingFactor = "6"

# Set current workspace as the Map Document
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]

def clip(data):
    """Clip the layer by the specified extent and save as a new file.
    Args:
        data (str): The keyword to search for in the layer names.
    """
    # The four coordinates should be the extent of the shp file extent.
    # Check the parameter for coordinates before running.
    i = 0
    total = len(arcpy.mapping.ListLayers(df))
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            file_names = l.name.split('.')
            # Renaming the layer names: Month attached
            arcpy.Clip_management(
                l.name,
                "106.356384 47.563171 108.453430 48.257156",
                "D:/Research/operation_captial_city_ger/sub_operation_LUCC/LULC/UB_LULC_" + file_names[1][1:] + ".tif",
                "UB",
                "255",
                "ClippingGeometry",
                "NO_MAINTAIN_EXTENT"
            )
            # Be careful about the nodata_value option. Recheck this every time on the dataset.
            i += 1
            print(f"{i}/{total} Done")

def rectify_LULC(data):
    """Perform a setnull operation on the layer and save as a new file.
    Args:
        data (str): The keyword to search for in the layer names.
    """
    # The four coordinates should be the extent of the shp file extent.
    # Check the parameter for coordinates before running.
    i = 0
    total = len(arcpy.mapping.ListLayers(df))
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            inRaster = l.name
            inFalseRaster = l.name
            whereClause = "VALUE>=18 OR VALUE<1"
            out = sa.SetNull(inRaster, inFalseRaster, whereClause)
            out.save("D:/Research/operation_captial_city_ger/sub_operation_LUCC/tmp/" + l.name)
            i += 1
            print(f"{i}/{total} Done")

def transform(data):
    """Transform the original meaning table of MCD12Q1 to a simpler one and save as a new file.
    Args:
        data (str): The keyword to search for in the layer names.
    """
    i = 0
    total = len(arcpy.mapping.ListLayers(df))
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            inRaster = Raster(l.name)
            out = Con(((inRaster<=5)&(inRaster>=1)), 1, Con(((inRaster>=6)&(inRaster<=11)), 2, Con(inRaster==12, 3, Con(inRaster==13, 4, Con(inRaster==14, 5, Con(inRaster==16, 6, Con(((inRaster>=15)&(inRaster<=17)), 7)))))))
            out.save("D:/Research/operation_captial_city_ger/sub_operation_LUCC/tmp/" + l.name)
            i += 1
            print(f"{i}/{total} Done")

def export_AtrributeTable(data):
    """
    Exports an attribute table to a specific folder. This function takes a string 'data' as input which is used to find layers containing the specified keyword in the layer names. The output is saved in a specific folder.

    Parameters:
    data (str): keyword to find layers containing the specified keyword in the layer names.

    Returns:
    None
    """
    i = 0
    total = len(arcpy.mapping.ListLayers(df))
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            pass
            arcpy.TableToTable_conversion(l.name, "D:/Research/temp/", "table_" + l.name)

    
def collection(data="landscan"):
    #input:
    #data: name in string, just some keywords in layer names like "NDVI" or "GSMaP"
    #output: a list of layers containing "landscan"
    records=[]
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            records.append(l.name)
    return records


#this would be the resample for the GSMaP layer
def resample():
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find("GSMaP") > -1:
            arcpy.Resample_management(l,"D:/Research/operation_short_correlation/temp/"+l.name,"0.00833333","BILINEAR")

'''
Update: As of 2021-3-18
This is the new workflow of the Pearson Correlation analysis follows the latest result of literature research noted on March's reading circle ppt.
-------------Before-------------
Jun., Jul., Aug. Mean NDVI V.S. GSMaP
-------------After-------------
Yearly Max NDVI V.S. [Apirl, May, June, July] Sum. GSMaP
'''

def get_month(data_type):
    """
    Get averaged NDVI or GSMaP for the specified months of each year from 2001 to 2019.

    Parameters:
    data_type (str): The data type, 'NDVI' or 'GSMaP_Mongolia'.

    Returns:
    None

    """
    months = ['Jul', 'Jun', 'Apr', 'May']

    for year in range(2001, 2020):
        # Record the layers that need to be processed for each year
        month_rec = []
        for layer in arcpy.mapping.ListLayers(mxd):
            # Pre-process GSMaP layer
            if layer.name.find(f"{data_type}_{year}") > -1:
                for m in months:
                    if layer.name.find(m) > -1:
                        month_rec.append(layer.name)

        # Calculate the average NDVI or GSMaP for the specified months
        if data_type == 'GSMaP_Mongolia':
            summer = CellStatistics(month_rec, "SUM", "DATA")
        else:
            summer = CellStatistics(month_rec, "MEAN", "DATA")
        summer.save(os.path.join(output_path, data_type, f"{data_type}_{year}.tif"))


def temporal_pearson_correlation():
    """
    Calculates the temporal Pearson correlation between yearly max NDVI and [Apr, May, Jun, Jul] sum GSMaP.

    Output:
    - A raster file containing the Pearson correlation coefficients.
    """
    # Collect the relevant NDVI and GSMaP layers
    ndvi_layers = []
    gsmap_layers = []
    for year in range(2001, 2021):
        for l in arcpy.mapping.ListLayers(mxd):
            if l.name.find(str(year)) > -1:
                if l.name.find("GSMaP") > -1:
                    gsmap_layers.append(l.name)
                else:
                    ndvi_layers.append(l.name)

    # Calculate the Pearson correlation coefficients
    ndvi_sum = CellStatistics(ndvi_layers, "SUM", "DATA")
    gsmap_sum = CellStatistics(gsmap_layers, "SUM", "DATA")
    dot_product_sum = CellStatistics([Raster(ndvi) * Raster(gsmap) for ndvi, gsmap in zip(ndvi_layers, gsmap_layers)], "SUM", "DATA")
    ndvi_sum_square = CellStatistics([Raster(ndvi) * Raster(ndvi) for ndvi in ndvi_layers], "SUM", "DATA")
    gsmap_sum_square = CellStatistics([Raster(gsmap) * Raster(gsmap) for gsmap in gsmap_layers], "SUM", "DATA")
    temp = (ndvi_sum_square - ndvi_sum * ndvi_sum / len(ndvi_layers)) * (gsmap_sum_square - gsmap_sum * gsmap_sum / len(gsmap_layers))
    output = (dot_product_sum - ndvi_sum * gsmap_sum / len(ndvi_layers)) / SquareRoot(temp)
    output_path = os.path.join(output_folder, "temporal_pearson_coef.tif")
    output.save(output_path)


month = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}

def extract_yearly_DN_to_points():
    """
    Extracts yearly NDVI and KBDI data values to the extraction points.
    """
    # Create empty lists for storing layer names
    KBDI = []
    NDVI = []
    for l in arcpy.mapping.ListLayers(df):
        # Find KBDI layers
        if l.name.find("KBDI_") > -1:
            temp = []
            temp.append(l.name)
            temp.append("KBDI " + l.name[-8:-4])
            KBDI.append(temp)

        # Find NDVI layers
        elif l.name.find("NDVI") > -1:
            temp = []
            temp.append(l.name)
            temp.append("NDVI " + l.name[-8:-4])
            NDVI.append(temp)

def extract_monthly_DN_to_points():
    """
    Extracts monthly NDVI and KBDI data values to the extraction points.
    """
    # Create empty lists for storing layer names
    KBDI = []
    NDVI = []
    for l in arcpy.mapping.ListLayers(df):
        # Find KBDI layers
        if l.name.find("KBDI_") > -1:
            temp = []
            temp.append(l.name)
            temp.append("K_" + l.name[5:9] + "_" + month[l.name[10:13]])
            KBDI.append(temp)

        # Find NDVI layers
        elif l.name.find("NDVI_20") > -1:
            temp = []
            temp.append(l.name)
            temp.append("N_" + l.name[5:9] + "_" + month[l.name[10:13]])
            NDVI.append(temp)


import datetime as dt
import arcpy
from arcpy.sa import *

# Set current workspace as the Map Document
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]

# Function to calculate the mean of a list of rasters
def calculate_mean(load, file):
    '''
    Calculate the mean of a list of rasters and save the result to a specified file path.

    Args:
    load (list): A list of rasters to calculate the mean from.
    file (str): A file path to save the result.

    Returns:
    None.
    '''
    overall = CellStatistics(load, "MEAN", "DATA")
    overall.save(file)
    print("Done!")

# Function to calculate the maximum value of a list of rasters
def calculate_maximum(load, file):
    '''
    Calculate the maximum value of a list of rasters and save the result to a specified file path.

    Args:
    load (list): A list of rasters to calculate the maximum value from.
    file (str): A file path to save the result.

    Returns:
    None.
    '''
    overall = CellStatistics(load, "MAXIMUM", "DATA")
    overall.save(file)
    print("Done!")

# Function to calculate the sum of a collection of rasters
def calculate_sum(collection):
    '''
    Calculate the sum of a collection of rasters and save the result to a specified file path.

    Args:
    collection (list): A list of rasters to calculate the sum from.

    Returns:
    None.
    '''
    summer = CellStatistics(collection, "SUM", "DATA")
    summer.save("D:/Research/operation_short_correlation/GSMaP_2020.tif")
    print("Done!")

# Function to rename NDVI files by adding the month to the filename
def rename_ndvi():
    '''
    Rename NDVI files by adding the month to the filename.

    Args:
    None.

    Returns:
    None.
    '''
    month={
        "1":"Jan","2":"Feb","3":"Mar","4":"Apr","5":"May","6":"Jun",
        "7":"Jul","8":"Aug","9":"Sep","10":"Oct","11":"Nov","12":"Dec",
    }

    for l in arcpy.mapping.ListLayers(df):
        if l.name.find("A2") > -1:
            # Renaming the layer names
            print("processed")
            file_names = l.name.split('.')
            dates = str(file_names[1][1:5]) + " " + str(file_names[1][5:8])
            dates = dt.datetime.strptime(dates,"%Y %j")
            l.name = file_names[0] + "_" + str(dates.year) + "_" + month[str(dates.month)] + ".tif"

# Function to fix NDVI files with invalid values
def fix_ndvi(name):
    '''
    Fix NDVI files with invalid values and save the result to a specified file path.

    Args:
    name (str): A string to search for in layer names.

    Returns:
    None.
    '''
    records = []
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(name) > -1:
            records.append(l.name)
    for n in records:
        temp = SetNull(n, n, "VALUE<-2000 OR VALUE>10000")
        temp *= 0.0001
        temp.save("D:/Research/processed/fix/" + n)

def NDVI_special():
    # A string used to generate salt to append to filenames for unique identification
    salt="01234567890123456789012345"
    i=0
    # Rename the layer names and put them in a dictionary
    print("Renaming layers...")
    dic = {} # Key: month abbreviation, Value: List of layer names
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find("MOD13A2_2020") > -1:
            file_names = l.name.split('_')
            file_names[0] += salt[i]
            # If the month abbreviation is not in the dictionary, add it and create an empty list
            if file_names[-1][:3] not in dic:
                dic[file_names[-1][:3]] = []
            l.name = "_".join(file_names)
            i += 1
            # Append the layer name to the list corresponding to the month abbreviation in the dictionary
            dic[file_names[-1][:3]].append(l.name)
    # Create the maximum NDVI layer for each month and save it to a new file
    print("Creating monthly NDVI layers...")
    for month_abbrev in dic:
        monthly_max = CellStatistics(dic[month_abbrev], "MAXIMUM", "DATA")
        name = "NDVI_2020_" + month_abbrev + ".tif"
        monthly_max.save("D:/Research/NDVI_clipped/" + name)
    print("Done.")
