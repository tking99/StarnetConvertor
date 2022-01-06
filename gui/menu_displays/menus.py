import tkinter as tk 

from gui.setting_displays.main_settings import SettingsDisplay
from gui.help_displays.about_displays import AboutDisplay
from gui.project_displays.project_managers import ProjectDisplayManager

class MainNavbar(tk.Menu):
    def __init__(self, controller, *args, **kwargs):
        tk.Menu.__init__(self, controller, *args, **kwargs)
        self.controller = controller
        # file Menu
        self.file_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label='New Project', command=self.new_project)
        self.file_menu.add_command(label='Open', command=self.open_project)
        self.file_menu.add_command(label='Save As', command=self.save_as_project, state='disabled')
        self.file_menu.add_command(label='Save', command=self.save_project, state='disabled')
        self.file_menu.add_command(label="Exit", command=self.controller.exit)
        
        # Options Menu
        self.options_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label='Settings', menu=self.options_menu)
        self.options_menu.add_command(label='Project Settings', command=self.display_settings, state='disabled')

        # Survey Menu
        self.survey_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label='Survey', menu=self.survey_menu)
        self.survey_menu.add_command(label='Process Files', command=self.controller.process_project, state='disabled')
        self.survey_menu.add_command(label='Export', command=self.controller.load_export_window, state='disabled')
        
        # Help Menu 
        self.help_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label='Help', menu=self.help_menu)
        self.help_menu.add_command(label='Contents')
        self.help_menu.add_command(label='About', command=self.display_about)

    def new_project(self):
        """Create a new project"""
        self.controller.project = ProjectDisplayManager.new_project()

    def open_project(self):
        """Load an existing project"""
        project = ProjectDisplayManager.open_project()
        if not project:
            # failed to pickle file so raise error
            tk.messagebox.showerror(title='Project Error',
                message='Project Failed to Load')
        else:
            self.controller.project = project 

    def save_project(self):
        """Saves an existing project"""
        ProjectDisplayManager.save_project(self.controller.project)
    
    def save_as_project(self):
        """Saves as an exisiting project and sets the 
        project title"""
        ProjectDisplayManager.save_as_project(self.controller.project)
        self.controller.set_project_title()

    def display_settings(self):
        # Check if project exists before continuing
        if self.controller.project:
            settings_display = SettingsDisplay(self.controller.main_frame, 
                self.controller.project.settings)
            settings_display.grab_set()
    
    def display_about(self):
        """Displays the about view"""
        about_display = AboutDisplay(self.controller.main_frame)
        about_display.grab_set()

    def enable_project_menu(self):
        """If project is loaded, enables project related menu items"""
        self.file_menu.entryconfig('Save As', state='normal')
        self.file_menu.entryconfig('Save', state='normal')
        self.options_menu.entryconfig('Project Settings', state='normal')

    def enable_survey_processor(self):
        """If imported files, survey processor will be enabled"""
        self.survey_menu.entryconfig('Process Files', state='normal')
    
    def disable_survey_processor(self):
        """If no imported files, survey processor will be disabled"""
        self.survey_menu.entryconfig('Process Files', state='disabled')

    def enable_export(self):
        """If setups and survey processor is active, then enable export"""
        self.survey_menu.entryconfig('Export', state='normal')

    def disable_export(self):
        """If no setups and survey processor is not active, then 
        disable export"""
        self.survey_menu.entryconfig('Export', state='disabled')

   
