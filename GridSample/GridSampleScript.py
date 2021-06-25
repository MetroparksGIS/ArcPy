__version__ = '6.0'
__pythonVersion__ = '3.0'

# Natural Resources Treatment Grid input tool. Allows the user to select grid cells and automatically
# add the selected treatment as a related record for all selected grid cells. The user can also select
# grid cells and select a treatment to be removed. When removing a treatment, the script iterates through
# the entire related table and may take a couple of seconds to finish running (the button usually in the
# "pressed" position for the duration of the iteration. The map window must be refreshed or zoomed after
# each update in order to refresh the related query.

# Import libraries
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os

# Set the active project to the current aprx open (used in the Refresh() function to refresh the map view).
aprx = arcpy.mp.ArcGISProject('current')

# Identify the polygon grid to be used and get the path. This must be a layer in the ArcGIS Pro document.
gridLayer = 'Grid'
gridsource = str(os.path.join(arcpy.Describe(gridLayer).path, os.path.basename(gridLayer))).replace('\\','/')

# Identify the primary key field.
primaryKey = 'UniqueID'

# Variable to hold field names.
fields = ['UniqueID','Treatment','Year','Quarter','Notes']

# Variable to track the status of tracking.
trackStatus = False

# Variable to hold uniqueID's.
unique = []

# Variable tracking to allow undo and redo.
uniqueTrack = []
entryTrack = []

# Get a count of how many cells are in the polygon grid.
allCells = 0
with arcpy.da.SearchCursor(gridsource,primaryKey) as cursor:
    for row in cursor:
        allCells += 1

# Set dropdown box options.
gridType = ['Completed','Planned']
entryType = ['Add Treatment','Remove Treatment']
years = [i for i in range(2015,2031)]
quarters = [0,1,2,3,4]
treatments = ['Basal Herbicide', 'Canopy Removal', 'Construction Monitoring', 'Dike Maintenance', 'Dormant Season Mow', 'Fish Stocking', 'Foliar Herbicide', 'Growing Season Mow', 'Gypsy Moth', 'Hand Pulling Invasives', 'Herbaceous Plant Introduction', 'Hydro Ax', 'Initial Seeding', 'Log Jam Removal', 'Oak Wilt Treatment', 'Over Seeding', 'Planting Maintenance', 'Prescribed Burn', 'Scraping', 'Stump Grinding', 'Tree/Shrub Introduction', 'Understory Removal', 'Water Control', 'Other']

# Function to refresh the map view.
def refresh():
    # Refresh the map view by changing the extent of the map view. The map view changes by such a small amount that
    # it isn't noticeable, but still causes the map view to refresh.
    mv = aprx.activeView
    ext = mv.camera.getExtent()
    ext.XMin = ext.XMin + 0.00001
    ext.YMin = ext.YMin + 0.00001
    ext.XMax = ext.XMax - 0.00001
    ext.YMax = ext.YMax - 0.00001
    mv.camera.setExtent(ext)

# Function to keep tracking up-to-date.
def tracking():
    global uniqueTrack
    global entryTrack
    global position
    global trackStatus

    if not trackStatus:
        trackStatus = True
        position = -1
        lbl_track.config(text='Tracking is enabled.')
    else:
        # Warn user that stopping the tracking session will discard all edits.
        if not messagebox.askyesno('Warning', 'You are about to stop tracking and all edits will be saved. Do you want to continue?'):
            return
        trackStatus = False
        uniqueTrack = []
        entryTrack = []
        lbl_track.config(text='Warning: Tracking is disabled.')

# Function to save all current edits and clear tracking lists.
def saveEdits():
    global uniqueTrack
    global entryTrack
    global position

    if not trackStatus:
        messagebox.showinfo('Error', 'Tracking is not currently enabled.')
        return
    else:
        # Warn user that stopping the tracking session will discard all edits.
        if not messagebox.askyesno('Warning', 'You are about to clear tracking and all edits will be saved. Do you want to continue?'):
            return
        uniqueTrack = []
        entryTrack = []
        position = -1

# Function to get uniqueID's from selected grid cells.
def getUnique():
    global unique
    
    # Get a count of how many cells are selected.
    selectedCells = 0
    with arcpy.da.SearchCursor(gridLayer,primaryKey) as cursor:
        for row in cursor:
            selectedCells += 1

    # Check if any cells are selected. Function will fail if all cells are selected or if no cells are selected.
    if allCells == selectedCells:
        messagebox.showinfo('Error', 'Too many cells selected.')
        return
    elif selectedCells == 0:
        messagebox.showinfo('Error', 'No cells selected.')
        return

    # Populate a list with the UniqueID's of all polygons which are selected.
    unique = list(dict.fromkeys([i for i, in arcpy.da.SearchCursor(gridLayer,primaryKey) if i is not None]))
    unique = [str(i) for i in unique]
    
# Function to check inputs and add rows for each polygon into the table.
def verifyEntry():
    global uniqueTrack
    global entryTrack
    global position

    # Run function to get unique values.
    getUnique()

    # Get the values entered.
    gridIs = cb_grid.get()
    entryIs = cb_entry.get()
    treatment = cb_treatment.get()
    otherTreatment = txt_treatment.get()
    year = cb_year.get()
    quarter = cb_quarter.get()
    notes = txt_notes.get()

    # If 'Other' was selected in the dropdown, check that we have a valid value in Other Treatments.
    if treatment == 'Other':
        if len(otherTreatment.replace(' ','').replace('-','')) == 0:
            messagebox.showinfo('Error', 'Please enter a treatment.')
            return
        else:
            treatment = otherTreatment

    # Check that the treatment entered isn't longer than 50 characters.
    if len(treatment) > 50:
        messagebox.showinfo('Error', 'Treatment can\'t be longer than 50 characters.')
        return

    # Check that the notes entered aren't longer than 200 characters.
    if len(notes) > 200:
        messagebox.showinfo('Error', 'Notes can\'t be longer than 200 characters.')
        return

    # If notes was left blank or with a space, correct it to a hyphen.
    if notes in (' ',''):
        notes = '-'
        txt_notes.delete(0,END)
        txt_notes.insert(0,'-')

    # Update tracking lists.
    if trackStatus:
        # Check current position and update track lists if needed.
        if position != -1:
            position += 1
            del uniqueTrack[position:]
            del entryTrack[position:]
            position = -1

        # Add current entry to tracking lists.
        uniqueTrack.append(unique)
        entryTrack.append([gridIs,entryIs,treatment,year,quarter,notes])

        # Run function to enter rows.
        populate(uniqueTrack[position],entryTrack[position])
    else:
        if not messagebox.askyesno('Warning', 'You are about to edit with tracking disabled. Do you want to continue?'):
            return
        else:
            populate(unique,[gridIs,entryIs,treatment,year,quarter,notes])

    populate(uniqueTrack[position],entryTrack[position])

# Function to check inputs and add rows for each polygon into the table.
def populate(uList, eList, tracked = False, entryType = ''):

    # Check if this is from an undo / redo command.
    if not tracked:
        entryType = eList[1]
    
    # Define variable based on grid type selected.
    if eList[0] == 'Completed':
        tableLayer = 'CompletedTreatments'
        tablesource = str(os.path.join(arcpy.Describe(tableLayer).path, os.path.basename(tableLayer))).replace('\\','/')
    else:
        tableLayer = 'PlannedTreatments'
        tablesource = str(os.path.join(arcpy.Describe(tableLayer).path, os.path.basename(tableLayer))).replace('\\','/')

    # Complete the primary tool function of adding or deleting rows.
    if entryType == 'Add Treatment':
        # Insert a cursor into the table in order to add new rows.
        with arcpy.da.InsertCursor(tablesource, fields) as cursor:

            # For all UniqueID's in the selection, add new rows based on the values entered.
            for i in uList:
                cursor.insertRow([i,eList[2],eList[3],eList[4],eList[5]])

        #Deselect rows in the table
        arcpy.SelectLayerByAttribute_management(tableLayer,'CLEAR_SELECTION')
    else:
        # Insert an update cursor into the table in order to update the rows.
        with arcpy.da.UpdateCursor(tablesource, fields) as cursor:

            # For all UniqueID's in the selection, remove rows based on the values entered.
            for row in cursor:
                if row[0] in uList:
                    if row[1:] == [eList[2],eList[3],eList[4],eList[5]]:
                        cursor.deleteRow()

        # Deselect rows in the table.
        arcpy.SelectLayerByAttribute_management(tableLayer,'CLEAR_SELECTION')

    # Update the map view to show changes.
    refresh()

# Function to reset the treatment dropdown box and notes.
def reset():
    txt_treatment.delete(0,END)
    txt_notes.delete(0,END)
    txt_notes.insert(0,'-')

# Function to reset all values entered into the tool.
def resetAll():
    cb_entry.current(0)
    cb_treatment.current(0)
    cb_year.current(0)
    cb_quarter.current(0)
    txt_treatment.delete(0,END)
    txt_notes.delete(0,END)
    txt_notes.insert(0,'-')

# Function to undo an operation.
def editUndo():
    global position

    if not trackStatus:
        messagebox.showinfo('Error', 'Tracking is disabled.')
        return

    if len(entryTrack) == 0:
        messagebox.showinfo('Error', 'There are no edits to undo.')
        return
    elif abs(position) > len(entryTrack):
        messagebox.showinfo('Error', 'All edits have been undone.')
        return
    else:
        if entryTrack[position][1] == 'Add Treatment':
            populate(uniqueTrack[position],entryTrack[position],True,'Remove Treatment')
        else:
            populate(uniqueTrack[position],entryTrack[position],True,'Add Treatment')

        # Update to the next position to undo.
        position -= 1

        # Update the map view to show changes.
        refresh()

# Function to redo an operation.
def editRedo():
    global position

    if not trackStatus:
        messagebox.showinfo('Error', 'Tracking is disabled.')
        return

    if len(entryTrack) == 0:
        messagebox.showinfo('Error', 'There are no edits to redo.')
        return

    if position == -1:
        messagebox.showinfo('Error', 'All edits have been redone.')
        return
    else:
        # Update to the position that needs redone.
        position += 1

        if entryTrack[position][1] == 'Add Treatment':
            populate(uniqueTrack[position],entryTrack[position],True,'Add Treatment')
        else:
            populate(uniqueTrack[position],entryTrack[position],True,'Remove Treatment')

        # Update the map view to show changes.
        refresh()

# Function to open pop-up menu with information about this tool.
def about():
    messagebox.showinfo('About',
                        'Natural Resources Grid Input Tool v6.0 \n'\
                        'Designed for ArcGIS Pro and Python Version 3 \n'\
                        '\n'\
                        'For help, contact: ...')

# Function to create a scrollable pop-up window that lists all records for selected grid cells.
def getRecords():
    relatedPlanned = []
    relatedCompleted = []
    
    # Get a count of how many cells are selected. If more than one are selected, warn the user.
    selectedCells = 0
    with arcpy.da.SearchCursor(gridLayer,primaryKey) as cursor:
        for row in cursor:
            selectedCells += 1

    if selectedCells > 1:
        if not messagebox.askyesno('Warning', 'You have selected more than one grid cell. Do you want to continue?'):
            return

    # Run function to get unique values.
    getUnique()

    plannedLayer = 'PlannedTreatments'
    plannedSource = str(os.path.join(arcpy.Describe(plannedLayer).path, os.path.basename(plannedLayer))).replace('\\','/')

    completedLayer = 'CompletedTreatments'
    completedSource = str(os.path.join(arcpy.Describe(completedLayer).path, os.path.basename(completedLayer))).replace('\\','/')

    # Iterate through both tables to get related records for selected grid cells.
    for k,v in {'Planned':plannedSource,'Completed':completedSource}.items():

        with arcpy.da.SearchCursor(v, fields) as cursor:
            # For all UniqueID's in the selection, get related records.
            for row in cursor:
                if row[0] in unique:
                    arcpy.AddMessage(k)
                    if k == 'Planned':
                        arcpy.AddMessage('hmm')
                        relatedPlanned.append([row[0],row[2],row[3],row[1]])
                    else:
                        relatedCompleted.append([row[0],row[2],row[3],row[1]])

    # Cancel the function if there are no related records for the selected grid cells.
    if len(relatedPlanned) + len(relatedCompleted) == 0:
        messagebox.showinfo('Error', 'There are no related records for the selected grid cell(s).')
        return
##    # Sort the related records based on all values returned.
##    relatedPlanned = sorted(relatedPlanned, key=lambda record: (record[0],record[1],record[2],record[3]))
##    completedPlanned = sorted(completedPlanned, key=lambda record: (record[0],record[1],record[2],record[3]))

    # Create the Tkinter pop-up window.
    win = Toplevel()
    win.geometry('300x450')

    win.title('Related Records')
    Grid.rowconfigure(win, 0, weight=1)
    Grid.columnconfigure(win, 0, weight=1)

    win_fc = Frame(win)

    win_fc.grid(row = 0, column = 0, sticky = (N,S,E,W))

    Grid.rowconfigure(win_fc, 1, weight=1)
    Grid.columnconfigure(win_fc, 0, weight=1)

    Grid.rowconfigure(win_fc, 3, weight=1)
    Grid.columnconfigure(win_fc, 0, weight=1)

    lbl_planned = Label(win_fc, text='Planned Treatments:')
    lbl_planned.grid(row = 0, column = 0, sticky = W, padx = 2, pady = 2)

    lbx_planned = Listbox(win_fc)
    lbx_planned.grid(row = 1, column = 0, columnspan = 2, sticky = (N,S,E,W))
    scb_planned = Scrollbar(win_fc)
    scb_planned.grid(row = 1, column = 1, sticky = (N,S,E,W))

    # Populate the related records for planned treatments.
    if len(relatedPlanned) != 0:
        for i in relatedPlanned:
            r = ' '.join(i)
            lbx_planned.insert(END, r)
    else:
        lbx_planned.insert(END, 'None')

    lbx_planned.config(yscrollcommand = scb_planned.set)
    scb_planned.config(command = lbx_planned.yview)

    lbl_completed = Label(win_fc, text='Completed Treatments:')
    lbl_completed.grid(row = 2, column = 0, sticky = W, padx = 2, pady = 2)

    lbx_completed = Listbox(win_fc)
    lbx_completed.grid(row = 3, column = 0, columnspan = 2, sticky = (N,S,E,W))
    scb_completed = Scrollbar(win_fc)
    scb_completed.grid(row = 3, column = 1, sticky = (N,S,E,W))

    # Populate the related records for completed treatments.
    if len(relatedCompleted) != 0:
        for i in relatedCompleted:
            r = ' '.join(i)
            lbx_completed.insert(END, r)
    else:
        lbx_completed.insert(END, 'None')

    lbx_completed.config(yscrollcommand = scb_completed.set)
    scb_completed.config(command = lbx_completed.yview)
      
    win.mainloop()

# Create the visual representation of the tool.
root = Tk()
root.title('NR Grid Input Tool v6.0')
root.geometry('293x290')
root.resizable(0,0)

# Create a menu bar and add options.
menuBar = Menu(root)

editMenu = Menu(menuBar, tearoff=0)
editMenu.add_command(label = 'Toggle Tracking', command = tracking)

editMenu.add_separator()

editMenu.add_command(label = 'Save Edits', command = saveEdits)

editMenu.add_separator()

editMenu.add_command(label = 'Undo', command = editUndo)
editMenu.add_command(label = 'Redo', command = editRedo)

menuBar.add_cascade(label = 'Edit', menu = editMenu)

aboutMenu = Menu(menuBar, tearoff=0)
aboutMenu.add_command(label = 'About', command = about)

menuBar.add_cascade(label = 'Help', menu = aboutMenu)

# Add form choices.
frm_fc = Frame(root)
frm_fc.pack(fill=X)

lbl_grid = Label(frm_fc, text='Treatment type:')
lbl_grid.grid(row = 0, column = 0, sticky = W, padx = 2, pady = 2)

cb_grid = ttk.Combobox(frm_fc, values = gridType)
cb_grid.current(0)
cb_grid.grid(row = 0, column = 1, sticky = W, padx = 2, pady = 2)

sep_second = ttk.Separator(frm_fc, orient = 'horizontal')
sep_second.grid(row = 1, column = 0, columnspan = 2, sticky = W + E, padx=2, pady=4)

lbl_entry = Label(frm_fc, text='Entry type:')
lbl_entry.grid(row = 2, column = 0, sticky = W, padx = 2, pady = 2)

cb_entry = ttk.Combobox(frm_fc, values = entryType)
cb_entry.current(0)
cb_entry.grid(row = 2, column = 1, sticky = W, padx = 2, pady = 2)

sep_second = ttk.Separator(frm_fc, orient = 'horizontal')
sep_second.grid(row = 3, column = 0, columnspan = 2, sticky = W + E, padx=2, pady=4)

lbl_treatment = Label(frm_fc, text='Select the treatment type:')
lbl_treatment.grid(row = 4, column = 0, sticky = W, padx = 2, pady = 2)

cb_treatment = ttk.Combobox(frm_fc, values = treatments)
cb_treatment.current(0)
cb_treatment.grid(row = 4, column = 1, sticky = W, padx = 2, pady = 2)

lbl_treatment2 = Label(frm_fc, text='Other treatment:')
lbl_treatment2.grid(row = 5, column = 0, sticky = W, padx = 2, pady = 2)

txt_treatment = ttk.Entry(frm_fc)
txt_treatment.grid(row = 5, column = 1, sticky = W, padx=2, pady=2)

sep_second = ttk.Separator(frm_fc, orient = 'horizontal')
sep_second.grid(row = 6, column = 0, columnspan = 2, sticky = W + E, padx=2, pady=4)

lbl_year = Label(frm_fc, text='Select the year:')
lbl_year.grid(row = 7, column = 0, sticky = W, padx = 2, pady = 2)

cb_year = ttk.Combobox(frm_fc, values = years)
cb_year.current(0)
cb_year.grid(row = 7, column = 1, sticky = W, padx = 2, pady = 2)

lbl_quarter = Label(frm_fc, text='Select the quarter:')
lbl_quarter.grid(row = 8, column = 0, sticky = W, padx = 2, pady = 2)

cb_quarter = ttk.Combobox(frm_fc, values = quarters)
cb_quarter.current(0)
cb_quarter.grid(row = 8, column = 1, sticky = W, padx = 2, pady = 2)

sep_second = ttk.Separator(frm_fc, orient = 'horizontal')
sep_second.grid(row = 9, column = 0, columnspan = 2, sticky = W + E, padx=2, pady=4)

lbl_notes = Label(frm_fc, text='Notes:')
lbl_notes.grid(row = 10, column = 0, sticky = W, padx = 2, pady = 2)

txt_notes = ttk.Entry(frm_fc)
txt_notes.insert(0,'-')
txt_notes.grid(row = 11, column = 0, columnspan = 2, sticky = W+E, padx=2, pady=2)

# Add user interface buttons.
frm_btn = Frame(root)
frm_btn.pack(fill=X)

btn_update = Button(frm_btn, text='Update', command = verifyEntry)
btn_update.pack(side = LEFT, padx=2, pady=2)

btn_reset = Button(frm_btn, text='Reset', command = reset)
btn_reset.pack(side = LEFT, padx=2, pady=2)

btn_resetAll = Button(frm_btn, text='Reset All', command = resetAll)
btn_resetAll.pack(side = LEFT, padx=2, pady=2)

btn_getRecords = Button(frm_btn, text='Get Records', command = getRecords)
btn_getRecords.pack(side = RIGHT, padx=2, pady=2)

# Add tracking status text.
frm_sta = Frame(root)
frm_sta.pack(fill=X)

lbl_track = Label(frm_sta, text='Warning: Tracking is disabled.')
lbl_track.pack(side = LEFT, padx = 2, pady = 2)

#Add a menu bar and keep the window open until closed by the user.
root.config(menu = menuBar)
root.mainloop()
