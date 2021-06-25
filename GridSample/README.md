**Grid Tracking Tool v6.0**  
Designed for ArcGIS Pro and Python 3

The following directory contains sample data and the script used to track natural resource treatments using a polygon grid and related tables.

**Exploring the Data**  
To explore the sample data, add the *Grid* feature class to your map. Use an SQL definition query to filter through the related tables. For example, using 
*UniqueID IN (SELECT UniqueID FROM CompletedTreatments WHERE Year = '2020')* will show you all grid cells which have related records in the *CompletedTreatments* table and the records containing 2020 in the *Year* field.

**Add/Remove Treatments**  
To add or remove treatments, add the *Grid* feature class and both tables (*CompletedTreatments* and *PlannedTreatments*) to your map. Symbolize the *Grid* layer as hollow with a black border. In order to easily track entries, copy the *Grid* layer twice. If adding entries for 2021 (for example), use an SQL definition query on the first copied layer to show all grid cells with related records in the *CompletedTreatments* table for 2021, and symbolize these grid cells with a unique color. Do the same with the second copied *Grid* layer for *PlannedTreatments* and symbolize with a second color. Make the original *Grid* layer the only selectable layer.

Run the script tool to open the tkinter window. (I may add more details on how to use the tool and how the tool works later.)

***Disclaimer***  
I'm sure there are many things that can be updated/improved with this script to improve readability and make it more pythonic. This script was designed for use by one individual to make their life easier, and it currently does that. Improvements will be made as needed.
