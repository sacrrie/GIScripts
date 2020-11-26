import os

def change_name(key):
    for file in os.listdir("./"):
        if key in file:
            os.rename(file, file.replace("geotiff","tif"))
            #print(file.replace("geotiff","tiff"))

#change_name("NDVI")