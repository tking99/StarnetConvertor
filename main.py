import os
import time 
from sys import exit 
from datetime import datetime
from pathlib import Path


import tkinter as tk 
from tkinter import ttk
from tkinter import messagebox

from datetime import datetime, timedelta

from gui.menu_displays.menus import MainNavbar
from gui.survey_displays.survey_main_display import SurveyMainDisplay
from gui.import_displays.import_displays import ImportTreeDisplay


from starnet_formatter.importer_processors import FormatFileProcessor
from starnet_formatter.file_models import StarnetFormatterProject
from starnet_formatter.pickler import ProjectPickler

class StarnetConvertor(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1450x800")
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.title('Star*net Convertor')
        self.import_frame = ttk.Frame(self, style='Main.TFrame')
        self.import_frame.grid(column=0, row=0, padx=5, pady=5, sticky='N') 
        self.main_frame = ttk.Frame(self, style='Main.TFrame')
        self.main_frame.grid(column=2, row=0, padx=5, pady=5, sticky='NESW')
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self._project = None
        self.nav_menu = MainNavbar(self, tearoff=0)
        self.config(menu=self.nav_menu)
        self.import_tree_display = None 
        self.survey_display = None

    @property 
    def project(self):
        return self._project 

    @project.setter 
    def project(self, project):
        if project: 
            self._project = project 
            self.title(f'Star*net Convertor - {self.project}')
            self.nav_menu.enable_project_menu()
            self.open_project()

    def process_project(self):
        if self._project:
            answer = True 
            if self._project.has_active_setups():
                # give yes no warning to proceed:
                answer = messagebox.askyesno(
                    title='Active Survey Present',
                    message='Do you still wish to proceed?')
            if answer:
                self._project.process_files()
                self.load_survey_window()
    
    def open_project(self):
        self.load_import_tree()
        self.load_survey_window()
    
    def load_import_tree(self):
        if self._project: 
            if self.import_tree_display:
                self.import_tree_display.forget()
                self.import_tree_display.destroy()
            self.import_tree_display = ImportTreeDisplay(self.import_frame, self._project.import_file_org)
            self.import_tree_display.grid(column=0, row=0, sticky='NSEW')
            ttk.Separator(self, orient=tk.VERTICAL).grid(column=1, row=0, sticky='NS',
                rowspan=2)
            # enable processing button 
            self.nav_menu.enable_survey_processor()

    def load_survey_window(self):
        if self._project and self._project.has_active_setups():
            if self.survey_display:
                self.survey_display.forget()
                self.survey_display.destroy()
            self.survey_display = SurveyMainDisplay(self.main_frame, self.import_frame, self._project)
            self.survey_display.grid(column=0, row=0, sticky='NSEW')

            # enable export button 
            self.nav_menu.enable_export()

    def load_export_window(self):
        if self._project and self._project.has_active_setups():
            if self.survey_display:
                self.survey_display.display_export_settings()

             
    def set_project_title(self):
        """Appends the project name to the title"""
        self.title(f'Starnet Convertor-{self.project}')
    
    def exit(self):
        """Asks if user wants to save before 
        exiting out of the program"""
        if self._project:
            answer = messagebox.askyesnocancel(
                title='Quit', message='Do you wish to save before quitting?')  
            if answer is None:
                # user cancels
                return
            elif answer:
                self.nav_menu.save_as_project()
        exit()






if __name__ == "__main__":
    main = StarnetConvertor()
    main.protocol('WM_DELETE_WINDOW', main.exit)
    main.mainloop()
