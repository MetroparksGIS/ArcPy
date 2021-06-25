**Grid Tracking Tool v6.0**  
Designed for ArcGIS Pro and Python 3

The following directory contains sample data and the script used to track natural resource treatments using a polygon grid and related tables.

To explore the sample data, add the *Grid* feature class to your map. Use an SQL query to filter through the related tables. For example, using 
*UniqueID IN (SELECT UniqueID FROM CompletedTreatments WHERE Year = '2020')* will show you all grid cells which have related records in the *CompletedTreatments* table and the records containing 2020 in the *Year* field.
