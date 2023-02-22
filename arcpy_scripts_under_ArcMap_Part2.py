import arcpy

# set multi-processing
arcpy.env.parallelProcessingFactor = "6"

# Set current workspace as the Map Document
mxd = arcpy.mapping.MapDocument("CURRENT")

# The first DataFrame would be the only one data frame
df = arcpy.mapping.ListDataFrames(mxd)[0]

def convert(data):
    """
    Export each layer as JPEG image
    data - name of data layer to be exported
    """

    # Loop through each layer in the data frame
    for layer in arcpy.mapping.ListLayers(df):
        if layer.name.find(data) > -1:
            # Set the layer to be visible and refresh the active view
            layer.visible = True
            arcpy.RefreshActiveView()

            # Export the current layer as a JPEG image
            arcpy.mapping.ExportToJPEG(mxd,
                                       "D:/Research/GIFs/" + layer.name + ".jpg",
                                       resolution=1000,
                                       color_mode="8-BIT_PALETTE")

            # Set the layer to be invisible
            layer.visible = False
import os
import arcpy

# A dictionary to map month numbers to abbreviations and vice versa
month = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}

# Change file names from number to month abbreviation or vice versa
def change_name(direction):
    for file in os.listdir("./"):
        target = file.split(".")[0].split("_")[-1]
        for month_num, month_chr in month.items():
            if direction:
                if month_num == target:
                    os.rename(file, file.replace(target, month_chr))
            else:
                if month_chr == target:
                    os.rename(file, file.replace(target, month_num))

# Change layer names from number to month abbreviation or vice versa
def convert(direction):
    for layer in arcpy.mapping.ListLayers(df):
        target = layer.name.split(".")[0].split("_")[-1]
        for month_num, month_chr in month.items():
            if direction:
                if month_num == target:
                    layer.name = layer.name.replace(target, month_chr)
            else:
                if month_chr == target:
                    layer.name = layer.name.replace(target, month_num)

# Sort the layers in the table of contents alphabetically
# Reference: https://gis.stackexchange.com/a/153177
def sort_layers():
    # Get the current map document and the first data frame
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    
    # Find the group layer
    group_lyr = [lyr for lyr in arcpy.mapping.ListLayers(mxd) if lyr.isGroupLayer][0]

    # Get a sorted list of layer names
    lyr_names = sorted(lyr.name for lyr in arcpy.mapping.ListLayers(mxd))

    # Move each layer to the group layer in sorted order
    for name in lyr_names:
        lyr = arcpy.mapping.ListLayers(mxd, name)[0]
        arcpy.mapping.MoveLayer(df, group_lyr, lyr, "BEFORE")

    # Remove the group layer
    arcpy.mapping.RemoveLayer(df, group_lyr)

def extract_by_mask(data="landscan"):
    """
    Extracts the input data by mask and saves the output files in the designated path
    """
    i = 0
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            extract = ExtractByMask(l.name, "UB_city")
            extract.save("D:/Research/temp/UB_" + l.name)
            i += 1
            print(str(i) + " Done")
            
def rectify_raster(data="GSMaP"):
    """
    Filters out invalid raster values and saves the filtered output in the designated path
    """
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
            print(str(i) + "/" + str(total) + " Done")

def filter_lulc_grassland(data="LULC_Mongolia_"):
    """
    Filters out all pixels except grassland, and saves the filtered output in the designated path
    """
    i = 0
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            print(l.name)
            # the SetNull expression should filter out all pixels except for class 2
            out = sa.SetNull(Raster(l.name) != 2, Raster(l.name))
            out.save("D:/Research/temp/grassland_" + l.name[-8:-4] + ".tif")
            i += 1
            print(str(i) + " Done")

def convert_raster_to_polygon(data="grassland_"):
    """
    Converts raster data to polygon and saves the output in the designated path
    """
    i = 0
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            arcpy.RasterToPolygon_conversion(l.name, "d:/Research/processed/" + l.name[:-4] + ".shp", "SIMPLIFY")
            
def extract_and_compute_area(data="grassland_20"):
    """
    Extracts the input data by mask, calculates the area, and saves the output in the designated path
    """
    i = 0
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            extract = ExtractByMask("nvg_classi", l.name)
            # use ZonalGeometry to calculate the area of each polygon
            arcpy.sa.ZonalGeometry(extract, "Value", "AREA").save("D:/Research/temp/" + l.name + ".tif")
            # use the Spatial Analyst tool ZonalStatisticsAsTable to calculate the statistics and save the output as a csv file
            arcpy.sa.ZonalStatisticsAsTable(extract, "Value", "nvg_classi", "D:/Research/temp/area_" + l.name + ".dbf") 
            i += 1
            print(str(i) + " Done")```


def linear_slope(collection):
    """
    This function calculates the linear slope of the trend presented on a raster given a list of raster layers.

    Parameters:
    collection (list): A list of rasters' layer names.

    Returns:
    None: The calculated linear slope is saved in a new raster layer in the specified location.

    Reference:
    https://gis.stackexchange.com/questions/65787/making-linear-regression-across-multiple-raster-layers-using-arcgis-desktop/65841#65841
    """

    # Calculate the length of the collection
    n = len(collection)

    # Initialize the result raster layer as the first raster layer in the collection
    temp = 12 * Raster(collection[0])

    # Iterate over the remaining raster layers in the collection
    for i in range(2, n + 1):
        # Calculate the coefficient for the current raster layer
        coefficient = 12 * i - 6 * (n + 1)
        # Multiply the coefficient by the raster layer and add to the result layer
        temp += coefficient * Raster(collection[i - 1])

    # Divide the result layer by the total coefficient and save the result to a new raster layer
    temp /= n ** 3 - n * 1.0
    names = collection[0].split("_")
    temp.save("D:/Research/temp/" + names[0] + "_linear_slope.tif")


def rename_gsmap_month():
    """
    Renames the GSMaP layers with month names appended to the layer names.

    Inputs:
    None

    Outputs:
    None
    """
    month = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
        "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
    }

    for layer in arcpy.mapping.ListLayers(df):
        # Pre-processing GSMAP
        if layer.name.find("gsmap") > -1:
            # Renaming the layer names: Month attached
            file_names = layer.name.split('.')
            layer.name = f"GSMaP.{file_names[2]}.{file_names[1][0:4]}.{month[file_names[1][4:]]}.tif"


def remove_GSMaP_if_corrupted():
    """
    Checks the GSMaP layers for corruption and removes any corrupted layers from the dataframe.

    Inputs:
    None

    Outputs:
    None
    """
    for layer in arcpy.mapping.ListLayers(df):
        if layer.name.find("GSMaP") > -1:
            minimum = arcpy.GetRasterProperties_management(layer.name, "MINIMUM")
            if float(minimum.getOutput(0)) > 10000:
                print layer.name.split('_')[-2], " ", layer.name.split('_')[-1][:3]
                arcpy.mapping.RemoveLayer(df, layer)


def get_years(data):
    """
    Returns the years found in the layers for the input data name.

    Inputs:
    data: Name of the data as string, just some keywords in layer names like "NDVI" or "GSMaP".

    Outputs:
    A set of years.
    """
    years = set()
    for layer in arcpy.mapping.ListLayers(df):
        if layer.name.find(data) > -1:
            year = layer.name[-12:-4]
            years.add(year)
    return years


def check_data_gaps(set1, set2):
    """
    Checks the discrepency in time between two datasets.

    Inputs:
    set1: The first dataset as a string.
    set2: The second dataset as a string.

    Outputs:
    A list of the years that exist in set1 but not in set2.
    """
    y1 = get_years(set1)
    y2 = get_years(set2)
    if len(y1) < len(y2):
        temp = y1
        y1 = y2
        y2 = temp
    return list(y1 - y2)


def refresh_display():
    """
    Refreshes the Table of Contents and the active view.

    Inputs:
    None

    Outputs:
    None
    """
    arcpy.RefreshTOC()
    arcpy.RefreshActiveView()


def collection_by_time(time_unit, data):
    """
    Collects raster layers into yearly or monthly collections based on their time stamps.
    Args:
        time_unit (str): The time unit to group by. Either "year" or "month".
        data (str): The name in string, just some keywords in layer names like "NDVI" or "GSMaP".
    Returns:
        dict: A dictionary containing yearly or monthly collections of the raster layers.
    """
    # TODO: Raster aggregation by its metadata/properties should be accessed through its object properties rather 
    # than the names. Refactor this function later.
    records = {}
    for l in arcpy.mapping.ListLayers(df):
        if l.name.find(data) > -1:
            if time_unit == "year":
                unit = l.name.split('_')[-2]
            elif len(l.name) > 14:
                unit = l.name.split('_')[-1][0:3]
            else:
                continue

            if unit not in records:
                records[unit] = [l.name]
            else:
                records[unit].append(l.name)
    return records
