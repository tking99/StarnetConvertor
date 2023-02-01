import tkinter as tk 
from tkinter import ttk 

from starnet_formatter.importer_processors import FormatFileProcessor
from starnet_formatter.checkers import SetupsChecker
from gui.survey_displays.survey_processor_displays import SurveyProcessorFrame
from gui.survey_displays.summary_display import SummaryDisplay
from gui.export_displays.export_settings_displays import ExportSettingsDisplay

class SurveyMainDisplay(ttk.Frame):
    def __init__(self, container, import_frame, project, *args, **kwargs):
        super().__init__(container, *args, **kwargs) 
        self.import_frame = import_frame
        self.survey_processor = project.survey_processor
        self.format_file_processor = project.format_file_processor
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.display_summary_display()
        self.display_survey_processor()

    def display_summary_display(self):
        if self.format_file_processor:
            summary_display = SummaryDisplay(self.import_frame, self.format_file_processor)
            summary_display.grid(column=0, row=3, sticky='NSEW')

    def display_survey_processor(self):
        """Displays the Survey Processor Frame"""
        if self.survey_processor:
            SurveyProcessorFrame(self, self.survey_processor).grid(
                column=0, row=0, sticky='NESW')

    def display_export_settings(self):
        """Displays the export settings display """
        no_target_ob_setups = SetupsChecker.no_target_obs(self.survey_processor.setups)
        
        if no_target_ob_setups:
           tk.messagebox.showerror(title='No Active Target Obs', 
            message=f'Following setups have no active target obs {no_target_ob_setups}')
        
        else:
            export_settings_display = ExportSettingsDisplay(self,
                self.survey_processor.settings)
            export_settings_display.grab_set()

    def display_success_export(self, result2D, result3D):
        """display success export message"""
        message_2D = 'Successfully exported a 2D Starnet Dat File'
        message_3D = 'Successfully exported a 3D Starnet Dat File'
        message = ''
        if result2D and result3D:
            message = message_2D + '\n' + message_3D
        elif result2D:
            message = message_2D
        
        elif result3D:
            message = message_3D

        tk.messagebox.showinfo(title='Successful Export',
            message=message)
        

    


    
