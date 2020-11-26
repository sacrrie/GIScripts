month={
    "01":"Jan","02":"Feb","03":"Mar","04":"Apr","05":"May","06":"Jun",
    "07":"Jul","08":"Aug","09":"Sep","10":"Oct","11":"Nov","12":"Dec",
}

import os

def change_name(direction):
    for file in os.listdir("./"):
        target=file.split(".")[0].split("_")[-1]
        for month_num,month_chr in month.items():
            if direction:
                if month_num==target:
                    os.rename(file, file.replace(target,month_chr))
            else:
                if month_chr==target:
                    os.rename(file, file.replace(target,month_num))
                    
change_name(False)