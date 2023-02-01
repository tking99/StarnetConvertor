import os
from pathlib import Path
import tkinter as tk 
from tkinter import ttk
from tkinter import filedialog

from starnet_formatter.file_models import ImportedFile


class ImportTreeDisplay(ttk.Frame):
    """Import Tree Display"""
    ALLOWED_FILE_TYPES = (('TXT','.txt'), ('CSV', '.csv'),)

    def __init__(self, container, import_orgainser, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.container = container
        self.import_orgainser = import_orgainser    
        import_button_frame = ttk.Frame(self)
        import_button_frame.grid(column=0, row=0, sticky='NSEW')

        ttk.Button(import_button_frame, text='+', command=self.import_files).grid(column=0, row=0, sticky='NW')
        ttk.Button(import_button_frame, text='-', command=self.remove_files).grid(column=1, row=0, sticky='NW')

        heading_frame = ttk.Frame(self)
        heading_frame.grid(column=0, row=1, sticky='NSEW')
        ttk.Label(heading_frame, text='Imported Files').grid(column=0, row=1, sticky='EW')
        ttk.Separator(heading_frame, orient=tk.HORIZONTAL).grid(
            column=0, row=2, columnspan=2, sticky='EW')

        self.import_tree_display= ttk.Frame(self)
        self.import_tree_display.grid(column=0, row=3, sticky='NSEW', padx=5, pady=5)
    
        if not self.import_orgainser.is_empty():
            self.display_files()
      
    def display_files(self):
        """Displays the imported files in the tree"""
        for child in self.import_tree_display.winfo_children():
            child.destroy()

        self.active_file_vars = {}
        for f in self.import_orgainser.imported_files:
                if isinstance(f, ImportedFile):
                    self._add_active_var(f)
                else:
                    self.display_unsuccessful_import(f)
        
        for row, f in enumerate(self.import_orgainser):
            ttk.Checkbutton(self.import_tree_display, variable=self._get_active_var(f),
                onvalue=True, offvalue=False, command=f.file_active_toggle).grid(column=0, row=row, sticky='W')
            ttk.Label(self.import_tree_display, text=f.file_name).grid(column=1, row=row, sticky='W')

    def import_files(self):
        """Imports files to the list of imported files,
        after file has been imported, import tree structure is updated"""
        files = filedialog.askopenfilenames(filetypes=self.ALLOWED_FILE_TYPES)
        if files:
            self.import_orgainser.add_files(files)
            self.display_files()

    def remove_files(self):
        """Removes the selected files from the project"""
        self.import_orgainser.remove_non_active_files()
        self.display_files()

    def display_unsuccessful_import(self, file_name):
        tk.messagebox.showerror(
            title='Unsucessfull Import', 
            message=f'File "{os.path.basename(file_name)}"" already loaded into the project'
        )
    
    def _get_active_var(self, imported_file):
        """returns the active var for an imported file instance"""
        var = self.active_file_vars.get(imported_file)
        if not var:
            var = self._add_active_var(imported_file)
        return var

    def _add_active_var(self, imported_file):
        """adds the active varaible for a imported file 
        to the dictionary holding the active vars"""
        var = tk.BooleanVar(value=imported_file.file_active)
        self.active_file_vars[imported_file] = var
        return var
           
           
class SurveyImportSummaryDisplay(tk.Toplevel):
    """Survey Import Summary Display"""
    def __init__(self, parent, survey_processor, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.survey_processor = survey_processor
        pop_up_frame = ttk.Frame(self, width=300,height=400, padding="3 3 12 12")
        pop_up_frame.grid(column=0, row=0, padx=10, pady=10,
            sticky=(tk.N, tk.W, tk.E, tk.S))
        self.title('Import Summary')
        self.resizable(False, False)
    
        ttk.Label(pop_up_frame, text=f'Imported Stations: {self.total_imported_stations()} ').grid(
            column=0, row=1, pady=6, padx=3, sticky=tk.W)
        ttk.Label(pop_up_frame, text=f'Total Imported Observation: {self.survey_processor.total_imported_observations()}').grid(
            column=0, row=2, pady=6, padx=3, sticky=tk.W)

        ttk.Button(pop_up_frame, text='OK', command=self.quit_summary).grid(
            column=0, row=3, pady=3, padx=3, sticky=tk.W
        )

    def total_imported_stations(self):
        names = ''
        for setup in self.survey_processor.setups:
            names += f'{setup.name},'
        return names

    def quit_summary(self):
        self.destroy()

