# GIScripts

During my PhD study and the writing of this journal paper:
https://aars-ajg.org/journal.php?paper=AJG-2208005

I used bash scripts and Python scripts (inside ArcGIS Desktop) to help process decades-long hundred layers of Remote Sensing data. This is a repository sharing all key functions with comments and explanations. I hope it helps other researchers/students who have similar needs. And boy was ArcMap and arcpy package difficult to work with.

I might have missed some important functions in this repository, feel free to explore it with new Bing or ChatGPT or something else. Feel free to submit a pull request if you have better suggestions for this README file. Thanks and hope it helps!

| Function Name                             | Description                                                                                        |
|-------------------------------------------|----------------------------------------------------------------------------------------------------|
| MEAN                                      | Averages input rasters and saves result to a new file.                                            |
| MAX                                       | Finds the maximum value from input rasters and saves result to a new file.                        |
| SUM                                       | Sums input rasters and saves result to a new file.                                                |
| rename_NDVI                               | Renames NDVI layers by appending the month and year to the file name.                              |
| conformation_NDVI                         | Sets null values outside the valid range and rescales the values.                                  |
| NDVI_speical                              | Renames NDVI layers by appending a salt value and creates a dictionary of monthly maximum values.  |
| linear_slope                              | Calculates the linear slope of a trend on a set of rasters.                                        |
| rename_gsmap                              | Renames GSMaP layers by appending the month and year to the file name.                             |
| check_GSMaP                               | Removes GSMaP layers that have invalid minimum values.                                            |
| date_range                                | Returns a set of the unique years found in the input data.                                        |
| check_data_gaps                           | Finds the gaps in time between two datasets.                                                      |
| refresh                                   | Refreshes the active view in ArcMap.                                                               |
| collection_by_time                        | Groups rasters by year or month depending on the specified time unit.                             |
| temporal_pearson_correlation              | Calculates the temporal Pearson correlation between yearly max NDVI and [Apr, May, Jun, Jul] sum GSMaP. |
| extract_yearly_DN_to_points               | Extracts yearly NDVI and KBDI data values to the extraction points.                               |
| extract_monthly_DN_to_points              | Extracts monthly NDVI and KBDI data values to the extraction points.                              |

