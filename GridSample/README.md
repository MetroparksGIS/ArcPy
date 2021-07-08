**Grid Tracking Tool v6.1**  
Designed for ArcGIS Pro and Python 3

The following directory contains sample data and the script used to track natural resource treatments using a polygon grid and related tables.

**Exploring the Data**  
Download the sample zipped geodatabase and python scipt. The geodatabase contains a small section of the natural resources grid with treatments.

To explore the sample data, add the *Grid* feature class to your map. Use an SQL definition query to filter through the related tables. For example, using 
*UniqueID IN (SELECT UniqueID FROM CompletedTreatments WHERE Year = '2020')* will show you all grid cells which have related records in the *CompletedTreatments* table and whose records contain 2020 in the *Year* field.

**Adding the Tool**  
Instructions on how to add script tools in ArcGIS Pro can be found [here](https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/adding-a-script-tool.htm). This tool doesn't use parameters. All Python packages needed for this script are part of ArcGIS Pro's native Conda environment.

**Add/Remove Treatments**  
To add or remove treatments, add the *Grid* feature class and both tables (*CompletedTreatments* and *PlannedTreatments*) to your map. Symbolize the *Grid* layer as hollow with a black border. In order to easily track entries, copy the *Grid* layer twice. If adding entries for 2021 (for example), use an SQL definition query on the first copied layer to show all grid cells with related records in the *CompletedTreatments* table for 2021, and symbolize these grid cells with a unique color. Do the same with the second copied *Grid* layer for *PlannedTreatments* and symbolize with a second color. Make the original *Grid* layer the only selectable layer.

Run the script tool to open the tkinter window. (I may add more details on how to use the tool and how the tool works later. It's mostly straight forward though.)

***Disclaimer***  
I'm sure there are many things that can be updated/improved with this script to improve readability and make it more pythonic. (For instance, it uses the much hated global variable.) This script was designed for use by one individual to make their life easier, and it currently does that. Improvements will be made as needed.

Also, this script could be much simpler using *arcpy.da.Editor*, but I wanted to be able to undo/redo commands and see edits in real time in the map view; but with *editor* the edits don't commit until you run *stopEditing(True)*. (At least from all the testing I did, it appears that *stopOperation()* doesn't commit the edits.)
