import tkinter as tk 
from tkinter import ttk 
from tkinter.messagebox import askyesno

from gui.survey_displays.labels import GonObservationLabelProcessor, GonMeanLabelProcessor, \
                                    DMSObservationLabelProcessor, DMSMeanLabelProcessor
from gui.survey_displays.survey_model_edits_displays import SetupEditFrame, \
         TargetEditFrame, SideShotEditFrame

from starnet_formatter.convertors import gons_to_dms, dms_to_str
from starnet_formatter.checkers import SetupsChecker

# Need to refactor all of the factories depending if its GONS and DMS - single factory
# that returns all the frames required

class SurveyProcessorFrame(ttk.Frame):
    SETUP_TAB_ROW = 0 
    SETUP_ROW = 1
    EXPORT_ROW = 2 
    def __init__(self, controller, survey_processor, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.survey_processor = survey_processor

        # set main container for the survey processor frame
        self.container = ttk.Frame(self)
        self.container.grid(column=0, row=0, sticky="NESW")
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=1)
        
        self.current_setup_tab_frame = None 
        self.current_setup = self.first_setup()
       
        # display the setup tabs
        self.display_setup_tabs()
        
        # display first_setup
        if self.current_setup:
            self.current_setup_frame = SetupFrame(
                    self.container, self, self.current_setup
                )
            self.set_setup_frame(self.current_setup_frame)
            # create export button
            button_frame = ttk.Frame(self.container)
            button_frame.grid(column=0, row=self.EXPORT_ROW, sticky='E',
            padx=3, pady=5)
            s = ttk.Style()
            s.configure('Export.TButton', font=('Sans', '9', 'bold'),
                padding=(3,3,3,3))

            ttk.Button(button_frame, text='Export', style='Export.TButton',
                command=self.export).grid(column=0, row=0, sticky='E')

    def first_setup(self):
        try:
            return next(iter(self.survey_processor.setups))
        except StopIteration:
            pass
    
    def display_setup_tabs(self):
        """display the setup tabs frame"""
        if self.current_setup_tab_frame:
            self.current_setup_tab_frame.destroy()

        self.current_setup_tab_frame = SetupTabsFrame(
            self.container, self, self.survey_processor.setups
        )
        self.current_setup_tab_frame.grid(column=0, row=self.SETUP_TAB_ROW, sticky="NW",
            pady=(0,10))
    
    def update_current_setup_frame(self):
        """Updates the current setup frame"""
        if self.current_setup_frame:
            self.current_setup_frame.destroy()
        self.current_setup_frame = SetupFrame(
            self.container, self, self.current_setup
        )
        self.set_setup_frame(self.current_setup_frame)

    def display_setup(self, setup=None):
        """Displays the setup frame"""
        # display first setup if None
        if setup is None:
            setup = self.first_setup()
        
        # click button of new setup tab
        if setup != self.current_setup and setup is not None:
            if self.current_setup_frame:
                self.current_setup_frame.destroy()
            self.current_setup = setup 
            self.current_setup_frame = SetupFrame(
                self.container, self, self.current_setup
            ) 
            self.set_setup_frame(self.current_setup_frame)
            # set the tab button style 
      
    def set_setup_frame(self, setup_frame):
        """sets the setup frame to the grid"""
        setup_frame.grid(column=0, row=self.SETUP_ROW, sticky="NSEW", pady=10,
                    padx=10)
        setup_frame.columnconfigure(0, weight=1)
        setup_frame.rowconfigure(1, weight=1)
        # set setup tab to be bold for that setup frame
        self.current_setup_tab_frame.set_current_button_style(setup_frame.setup)
        
    def export(self):
        """Calls the controller and displays the 
        starnet setups display"""
        # load export display 
        # check all setups have an at least 1 active target ob
        no_target_ob_setups = SetupsChecker.no_target_obs(self.survey_processor.setups)
        if no_target_ob_setups:
           tk.messagebox.showerror(title='No Active Target Obs', 
            message=f'Following setups have no active target obs {no_target_ob_setups}')
        else:
            self.controller.display_export_settings()


class SetupTabsFrame(ttk.Frame):
    def __init__(self, container, controller, setups, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.container = container
        self.controller = controller 
        self.setups = setups
        self.current_button = None
        self.buttons = {setup: ttk.Button(self, text=setup.name,
            command=lambda setup=setup: self.controller.display_setup(setup))for setup 
                in self.setups}   
        self.current_tab_style = 'SetupTabActive.TButton'
        s_active = ttk.Style()
        s_active.configure(self.current_tab_style, font=('Sans', '11', 'bold'),
            padding=(3,3,3,3), background='blue') 
        
        self.tab_style = 'SetupTab.TButton'
        non_active = ttk.Style()
        non_active.configure(self.tab_style, font=('Sans', '10'),
            padding=(3,3,3,3))
      
        self.display_setup_tabs()

    def update_current_button(self, setup_name):
        """Updates a current setup tab with the latest 
        setup name""" 
        if self.current_button:
            self.current_button.configure(text=setup_name)

    def display_setup_tabs(self):  
        """Displays the setup tabs"""
        col = 0
        row = 0
        count = 1 
        for button in self.buttons.values():
            button.configure(style=self.tab_style)
            button.grid(column=col, row=row)
            col += 1 
            count += 1
            # split the setups into new row every 10 setups
            if count > 10:
                row += 1
                col = 0
                count = 1

    def set_current_button_style(self, setup):
        """Sets the current button style and change 
        previous tab button to old style"""
        button = self.buttons.get(setup)
        if button:
            button.configure(style=self.current_tab_style)
            if self.current_button:
                self.current_button.configure(style=self.tab_style)
            self.current_button = button
           

class SetupFrame(ttk.Frame):
    def __init__(self, container, controller, setup, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.container = container
        self.controller = controller
        self.survey_processor = self.controller.survey_processor
        self.setup = setup

        # variable to hold the reduce_to_target
        self.reduce_to_target = tk.StringVar()
        self.set_reduce_to()

        # dic that holds the row number of the differenct targets Target:row
        self.target_row = dict()
  
        # display the setup info
        self._display_setup_info() 

        # create the survey observation window
        self.target_obs_window = ttk.Frame(self)
        self.target_obs_window.grid(column=0, row=1, sticky="NSEW",
            pady=10, padx=10)
        self.target_obs_window.columnconfigure(0, weight=1)
        self.target_obs_window.rowconfigure(0, weight=1)

        # display canvas 
        self.canvas = TargetsObservationsCanvas(self.target_obs_window, self, self.setup)
        self.canvas.grid(column=0, row=0, sticky="NSEW")
      
    def set_reduce_to(self):
        if self.setup.reduce_to:
            self.reduce_to_target.set(self.setup.reduce_to.name)
    
    def delete_setup(self):
        self.survey_processor.delete_setup(self.setup)
        self.destroy()
        # reload the displays
        self.controller.display_setup_tabs()
        self.controller.display_setup()

    def delete_target(self, target):
        self.setup.delete_target(target)
        self.setup.remove_reduce_to(target)
        self.setup.reduce_to
        self.set_reduce_to()
        self.canvas.refresh_target_observations()

    def delete_sideshot(self, sideshot):
        self.setup.delete_sideshot(sideshot)
        self.canvas.refresh_target_observations()


    def _display_setup_info(self):
        self.setup_info_frame = SetupInfoFrame(self, self.setup)
        self.setup_info_frame.grid(column=0, row=0, sticky="W")

    def observation_line_frame(self):
        """Returns an observation frame based on the 
        settings file"""
        if self.survey_processor.settings.angular_unit == 'GONS':
            return GonObservationsFrame
        elif self.survey_processor.settings.angular_unit == 'DMS':
            return DegObservationsFrame
    
    def mean_observation_line_frame(self):
        """returns the mean observation frame based on the 
        settings file"""
        if self.survey_processor.settings.angular_unit == 'GONS':
            return GonMeanObFrame
        elif self.survey_processor.settings.angular_unit == 'DMS':
            return DegMeanObFrame


class SetupInfoFrame(ttk.Frame):
    def __init__(self, controller, setup, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.controller = controller
        self.setup = setup
        self.apply_scale_factor = tk.BooleanVar(
            value=self.controller.survey_processor.settings.apply_scale_factor)
        s = ttk.Style()
        s.configure('Setup.TLabel', font=('Sans', '11', 'bold'))
        self.setup_name = tk.StringVar(value=self.setup.name)
        self.ih = tk.StringVar(value=f'{self.setup.instrument_height:.3f}')
        self.sf = tk.StringVar(value=f'{self.setup.scale_factor:.8f}')
        self.atmos_ppm = tk.StringVar(value=f'{self.setup.atmospheric_ppm:.1f}')
        ttk.Label(self, text='Setup ID:', style='Setup.TLabel').grid(column=0, row=0, sticky="W", padx=(5,3))
        ttk.Label(self, textvariable=self.setup_name, style='Setup.TLabel').grid(column=1, row=0, sticky="W")
        ttk.Label(self, text='IH:', style='Setup.TLabel').grid(column=2, row=0, sticky="W", padx=(20,3))
        ttk.Label(self, textvariable=self.ih, style='Setup.TLabel').grid(column=3, row=0, sticky="W")
        ttk.Label(self, text='Atmos. PPM', style='Setup.TLabel').grid(column=4, row=0, sticky='W', padx=(20,3))
        self.atmos_ppm_label = ttk.Label(self, textvariable=self.atmos_ppm, style='Setup.TLabel')
        self.atmos_ppm_label.grid(column=5, row=0, sticky='W')
        ttk.Label(self, text="SF:", style='Setup.TLabel').grid(column=6, row=0, sticky="W", padx=(20,3))
        self.sf_label = ttk.Label(self, textvariable=self.sf, style='Setup.TLabel')
        self.sf_label.grid(column=7, row=0, sticky="W")
        self.sf_cb = ttk.Checkbutton(self, text="Scale Hori. D", variable=self.apply_scale_factor,
            onvalue=True, offvalue=False, 
            command=self.apply_scale_factor_toggle)
        self.sf_cb.grid(column=8, row=0, sticky="W", padx=(20,0))

        self.setup_instrument_type = tk.StringVar(value=self.setup.instrument_type)
        inst_type_combo = ttk.Combobox(self, textvariable=self.setup_instrument_type,
            values=self.controller.survey_processor.settings.instrument_types)
        inst_type_combo.grid(column=9, row=0, sticky='W', padx=6)
        inst_type_combo.bind('<<ComboboxSelected>>', self.update_setup_instrument_type)

        
        ttk.Button(self, text="Edit", command=self.display_edit_setup_frame
            ).grid(column=10, row=0, sticky='W', padx=(5,5))
        ttk.Button(self, text='Delete', command=self.delete_setup).grid(column=11, row=0, sticky='W', padx=(5,5))

    def delete_setup(self):
        """Asks user for confirmation to delete a setup, 
        if confirmed, setup will be deleted"""
        answer = askyesno(title=f'Delete Setup {self.setup.name}',
            message=f'Confirm Deletion')
        if answer:
            self.controller.delete_setup()
               
    def update_setup_instrument_type(self, *arg):
        """event binder that updates the setup instrument type"""
        self.setup.instrument_type = self.setup_instrument_type.get()
    
    def update_setup_info(self, name, ih, sf, atmos_ppm):
        self.setup_name.set(name)
        self.ih.set(f'{ih:.3f}')
        self.sf.set(f'{sf:.8f}')
        self.atmos_ppm.set(f'{atmos_ppm:.1f}')

    
    def apply_scale_factor_toggle(self):
        """Apply scale factor toggle and reload the 
        setup display to reflect new scale factor"""
        self.controller.survey_processor.settings.apply_scale_factor_toggle()
        self.controller.controller.update_current_setup_frame()
        
    def display_edit_setup_frame(self):
        """Loads the SetupEditFrame top level"""
        edit_setup = SetupEditFrame(self, self.controller, 
            self.setup)
        edit_setup.grab_set()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
class TargetsObservationsCanvas(tk.Canvas):
    def __init__(self, container, controller, setup,*args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.controller = controller 
        self.setup = setup
        self.survey_obs_frame = ttk.Frame(container)
        self.survey_obs_frame.grid(column=0, row=0)
        self.survey_obs_frame.columnconfigure(0, weight=1)

        self.scrollable_window = self.create_window((0, 0), window=self.survey_obs_frame,
            anchor="nw")

        self.bind("<Configure>", self._configure_window_size)
        self.survey_obs_frame.bind("<Configure>", self._configure_scroll_region)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.configure(yscrollcommand=scrollbar.set)
        self.yview_moveto(1.0)

        # display target observations
        self.display_observations()
     
    def _configure_scroll_region(self, event):
            self.configure(scrollregion=self.bbox("all"))

    def _configure_window_size(self, event):
            self.itemconfig(self.scrollable_window, width=self.winfo_width())

    def _on_mousewheel(self, event):
        self.yview_scroll(-int(event.delta/120), "units")
####################################################################################################################
    def refresh_target_observations(self):
        for child in self.survey_obs_frame.winfo_children():
            child.destroy()
        self.display_observations()

    def display_observations(self):
        # display target obs
        row = 0
        for target in self.setup.target_observations.values():
            self.display_target_observation(target, row)
            row += 1 
        # display side shots
        for target in self.setup.side_shot_observations.values():
            self.display_side_shot_observation(target, row)
            row += 1 

    def display_side_shot_observation(self, target, row):
        """Displays a single side shot target observation,
        requires a target and a row"""
        SideShotObservationsFrame(self.survey_obs_frame,
            self.controller, target, self.setup).grid(
                column=0, row=row, sticky="NSEW", pady=10)
 
    def display_target_observation(self, target, row):
        """Displays a single target observation, requires a target 
        and a row"""
        TargetObservationsFrame(self.survey_obs_frame,
            self.controller, target, self.setup).grid(
                column=0, row=row, sticky="NSEW", pady=10, padx=(0,10))


class TargetObservationsFrame(ttk.Frame):
    """Class used to display a target observation"""
    TARGET_INFO_ROW = 0
    SEPERATORS_ROW = (5, 7)
    TARGET_OB_ROW = 4
    TARGET_MEAN_ROW = 6 

    def __init__(self, container, controller, target,
        setup, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.container = container 
        self.controller = controller 
        self.target = target 
        self.setup = setup

        self.columnconfigure(0, weight=1)
    
        #display target info frame
        self.target_info_frame = self.get_info_frame()
        self.target_info_frame.grid(column=0, row=self.TARGET_INFO_ROW, sticky='W')

        # display canvas 
        obs_canvas_frame = ttk.Frame(self)
        obs_canvas_frame.grid(column=0, row=self.TARGET_OB_ROW, sticky='NSEW')
        obs_canvas_frame.columnconfigure(0, weight=1)
        self.obs_canvas = ObservationsCanvas(obs_canvas_frame, 
            self.controller, self, self.target)
        self.obs_canvas.grid(column=0, row=0, sticky='NSEW')
   
        # display mean ob
        self.mean_ob_frame = MeanObFrame(self, self.controller, self.target)
        self.mean_ob_frame.grid(column=0, row=self.TARGET_MEAN_ROW, sticky='W')
        self.update_mean_frame()

        # display seperators
        self._display_target_seperators()

    def get_info_frame(self):
        return TargetInfoFrame(
            self, self.controller, self.target, self.setup)

    @property
    def mean_ob(self):
        return self.target.mean_target_observation(
                self.controller.survey_processor.ob_reducer, 
                self.controller.survey_processor.settings.apply_scale_factor)

    def update_mean_frame(self):
        """Updates the mean ob"""
        if self.mean_ob:
            self.mean_ob_frame.update_mean_labels(self.mean_ob)

    def _display_target_seperators(self):
        for row in self.SEPERATORS_ROW:
            ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0,
                row=row, columnspan=2, sticky='ew')


class SideShotObservationsFrame(TargetObservationsFrame):
    def get_info_frame(self):
        return SideShotInfoFrame(
            self, self.controller, self.target, self.setup)

class MeanLabelProcessorFactory:
    """Factory that returns the correct mean observation label
    processor based on the angular settings unit"""
    PROCESSOR_CODE = ('GONS', 'DMS')
    PROCESSOR_TABLES = (GonMeanLabelProcessor, DMSMeanLabelProcessor) 

    @classmethod
    def label_processor(cls, processor_code):
        if processor_code in cls.PROCESSOR_CODE:
            for processor in cls.PROCESSOR_TABLES:
                if processor.CODE == processor_code:
                    return processor


class MeanObFrame(ttk.Frame):
    def __init__(self, container, controller, target, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        MEAN_PROCESSOR = MeanLabelProcessorFactory.label_processor(
            controller.survey_processor.settings.angular_unit
        )
        self.label_processor = MEAN_PROCESSOR(self, controller.survey_processor, target)
        
        self.label_processor.heading_label.grid(column=0, row=0, sticky='W')
        self.label_processor.hz_label.grid(column=1, row=0, stick='W')
        self.label_processor.v_label.grid(column=2, row=0, sticky='W')
        self.label_processor.sd_label.grid(column=3, row=0, sticky='W')
        self.label_processor.hd_label.grid(column=4, row=0, sticky='W')

    def update_mean_labels(self, mean_ob):
        """updates the mean labels"""
        self.label_processor.update_mean_labels(mean_ob)
  

class TargetInfoFrame(ttk.Frame):
    TARGET_ID_STRING = 'Target'
    TARGET_OPTIONS = ['TARGET', 'SPIGOT']
    def __init__(self, container, controller, target, setup,
        *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.container = container
        self.controller = controller
        self.target = target 
        self.setup = setup
        s = ttk.Style()
        s.configure('Target.TLabel', font=('Sans', '11', 'bold'), padding=(0,6))
        self.target_name_var = tk.StringVar(value=target.name)
        self.target_height_var = tk.StringVar(value=f'{target.target_height:.3f}')
        self.target_pc_var = tk.StringVar(value=f'{target.prism_constant:.1f}')

        #
        ttk.Label(self, text='Target Type: ', style='Target.TLabel').grid(column=0, row=0, sticky='W')
        # setting the target type
        self.target_type = tk.StringVar(value=self.TARGET_ID_STRING)
        target_type_combo = ttk.Combobox(self, textvariable=self.target_type,
            values=self.TARGET_OPTIONS)
        target_type_combo.grid(
                column=1, row=0, sticky='W', padx=(5,3))
        target_type_combo.bind('<<ComboboxSelected>>', self.change_target)
        
        ttk.Label(self, textvariable=self.target_name_var, style='Target.TLabel').grid(column=2, row=0, sticky="W", padx=(5,0))

        ttk.Label(self, text='TH:', style='Target.TLabel').grid(column=3, row=0, sticky="W", padx=(10,3))
        ttk.Label(self, textvariable=self.target_height_var, style='Target.TLabel').grid(column=4, row=0, sticky="W")
        ttk.Label(self, text='PC:', style='Target.TLabel').grid(column=5, row=0, sticky='W', padx=(10,3))
        ttk.Label(self, textvariable=self.target_pc_var, style='Target.TLabel').grid(column=6, row=0, sticky='W')

        # need to define a control dict holding the set to zero variables
        self.set_to_zero_frame()

        ttk.Button(self, text="Edit", command=self.display_edit_target_frame
            ).grid(column=8, row=0, padx=3)
        
        ttk.Button(self, text='Delete', command=self.delete_target).grid(column=9, row=0, padx=3)


    def change_target(self, *args):
        """Changes the target type of a target"""
        self.controller.survey_processor.move_target(self.setup,
            self.target.name, self.target_type.get())
        self.controller.canvas.refresh_target_observations()

    def set_to_zero_frame(self):
        self.set_to_zero = ttk.Radiobutton(self, text='Set to 0"', 
            variable=self.controller.reduce_to_target, 
                value=self.target.name, command=self.set_zero_to)
        self.set_to_zero.grid(column=7, row=0, padx=10, sticky="W")
    
    def delete_target(self):
        answer = askyesno(title=f'Delete Target {self.target.name}',
            message=f'Confirm Deletion')
        if answer:
            self.controller.delete_target(self.target)
    
    
    def display_edit_target_frame(self):
        """Loads the SetupEditFrame top level"""
        edit_target = TargetEditFrame(self, self.controller, 
            self.target)
        edit_target.grab_set()

    def update_target_info(self, target_name, target_height, target_pc):
        # update the target 
        self.controller.survey_processor.update_target(self.setup,
            self.target, target_name, target_height, target_pc
        )
        # update the target labels
        self.target_name_var.set(target_name)
        self.target_height_var.set(f'{self.target.target_height:.3f}')
        self.target_pc_var.set(f'{self.target.prism_constant:.1f}')

        # update observations 
        self.controller.canvas.refresh_target_observations()

    def set_zero_to(self):
        self.controller.survey_processor.update_setup_reduce_to(
            self.setup, self.target
        )

class SideShotInfoFrame(TargetInfoFrame):
    TARGET_ID_STRING = 'Spigot'

    def delete_target(self):
        answer = askyesno(title=f'Delete Target {self.target.name}',
            message=f'Confirm Deletion')
        if answer:
            self.controller.delete_sideshot(self.target)


    def set_to_zero_frame(self):
        """No set to zero frame implmentation for a side shot"""
        pass 


class ObservationsCanvas(tk.Canvas):
    HEADING_ROW = 0
    OBS_ROW = 2 
    # Column Numbers
    def __init__(self, container, controller, target_ob_frame, target, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.target_ob_frame = target_ob_frame
        self.controller = controller
        self.target = target

        obs_style = ttk.Style()
        obs_style.configure('Obs_frame.TFrame')
        self.main_window = ttk.Frame(container, style='Obs_frame.TFrame')
        self.main_window.grid(column=0, row=0)
    
        self.scrollable_window = self.create_window((0, 0), window=self.main_window,
            anchor="nw")

        self.bind("<Configure>", self._configure_window_size)
        self.main_window.bind("<Configure>", self._configure_scroll_region)

        

        # get requied obs table based on settings
        self.obs_table = ObservationTableFrameFactory.observation_table(
            self.controller.survey_processor.settings.angular_unit)
        
        self.obs_window = self.obs_table(self.main_window, self.controller,
        self.target_ob_frame, self.target)
        self.obs_window.grid(column=0, row=0, sticky='NSEW')
       
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.configure(yscrollcommand=scrollbar.set)
        self.yview_moveto(1.0)

    def _configure_scroll_region(self, event):
            self.configure(scrollregion=self.bbox("all"))

    def _configure_window_size(self, event):
            self.itemconfig(self.scrollable_window, width=self.winfo_width())


class ObservationsTableFrame(ttk.Frame):
    HEADING_ROW = 1 
    TABLE_ROW = 3 
    SEPERATOR_COLS = (7, 11, 15)

    def __init__(self, container, controller, target_ob_frame, target, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.target_ob_frame = target_ob_frame
        self.target = target
        self.stat_reducer = controller.survey_processor.stat_reducer
        self.ob_reducer = controller.survey_processor.ob_reducer
        self.controller = controller 
        # create label processors
        self.set_ob_label_processors()  
        self.display_observation_table()

    def display_observation_table(self):
        self.display_ob_table_heading()
        # loop through the ob processors
        if self.target.observations:       
            for row, label_processor in enumerate(self.ob_label_processors):
                # loop through the labels
                col = 0 
                for ob_label in label_processor.ob_labels + label_processor.hz_stat_labels + \
                    label_processor.v_stat_labels + label_processor.linear_stat_labels:
                    # skip col 7, 11, 15 for seprator 
                    if col in self.SEPERATOR_COLS:
                        col +=1
                    ob_label.grid(column=col, row=row+self.TABLE_ROW, sticky='E')
                    col += 1 
                # insert the delete label 
                label_processor.delete_observation_label().grid(column=col, row=row+self.TABLE_ROW, sticky='E')

                # update the labels with mean ob if not None
                if self.target.mean_target_observation:
                    label_processor.update_labels(self.target.mean_target_observation(
                        self.ob_reducer, self.controller.survey_processor.settings.apply_scale_factor))
            # place seperator 
            for col in self.SEPERATOR_COLS:
                # avoid bad row span 0 error if only 1 item
                if row == 0:
                    row = self.TABLE_ROW + 1 
                ttk.Separator(self, orient='vertical').grid(column=col, row=self.HEADING_ROW, rowspan=row+self.TABLE_ROW, sticky='ns',
                padx=10)

    def refresh_observation_table(self):
        """Refreshes the observation table"""
        for child in self.winfo_children():
            child.destroy()    
        self.set_ob_label_processors()
        self.display_observation_table()

    def update_hz_stats(self):
        if self.target_ob_frame.mean_ob:
            for label_processor in self.ob_label_processors:
                label_processor.update_hz_stat_labels(self.target_ob_frame.mean_ob)

    def update_v_stats(self):
        for label_processor in self.ob_label_processors:
            label_processor.update_v_stat_labels(self.target_ob_frame.mean_ob)
       
    def update_linear_stats(self):
        for label_processor in self.ob_label_processors:
            label_processor.update_linear_stat_labels(self.target_ob_frame.mean_ob)
    
    def display_ob_details(self, ob):
        """displays the details of an observation"""
        DETAILS_FRAME = self.get_observation_details_frame() 
        details = DETAILS_FRAME(self, self.controller, ob)
        details.grab_set()

    def get_observation_details_frame(self):
        """returns the Observation class according to the 
        angular unit in the settings"""
        if self.controller.survey_processor.settings.angular_unit =='GONS':
            return ObservationDetailsFrame
        elif self.controller.survey_processor.settings.angular_unit == 'DMS':
            return DMSObservationTableFrame
    
    def delete_observation(self, ob):
        """Deletes the observation from the Target"""
        # If observation is deleted, then referesh observation frame and update mean
        if self.delete_observation_confirmation():
            if self.target.delete_observation(ob):
                if self.target.observations:
                    self.refresh_observation_table()
                    self.target_ob_frame.update_mean_frame()
                else:
                    # no observations left so remove target from the setup
                    self.controller.delete_target(self.target)

    def delete_observation_confirmation(self):
        return tk.messagebox.askyesno(title='Delete Observation ',
            message='Do you wish to Delete?')
    
    def active_hz_toggle(self, ob):
        #if self.ob_reducer.one_hz_angle():
        #    if ob.hz_angle_on:
        #        self.min_observation_warning()
        #        return
        ob.hz_angle_on_toggle()
        self.update_hz_stats()
        self.target_ob_frame.update_mean_frame()

    def active_v_toggle(self, ob):
        #if self.ob_reducer.one_za_angle():
        #    if ob.za_angle_on:
        #        self.min_observation_warning()
        #        return
        ob.za_angle_on_toggle()
        self.update_v_stats()
        self.target_ob_frame.update_mean_frame()
       
    def active_linear_toggle(self, ob):
        #if self.ob_reducer.one_slope_dist():
        #    if ob.slope_distance_on:
         #       self.min_observation_warning()
         #       return
        ob.slope_distance_on_toggle()
        self.update_linear_stats()
        self.target_ob_frame.update_mean_frame()

    def _allowed_to_toggle(self, state):
        """Returns a boolean if the active buttons can toggle. 
        Based on there being at least one active observation"""
        if not self.ob_reducer.check_active_observation_present():
            return state == False 
        return True
     
    def min_observation_warning(self):
        """displays a warning that a minium of one 
        complete observation if required"""
        tk.messagebox.showwarning(title='Observation Warning',
        message='A minimum of 1 complete obervation is required')
     
class GonObservationsTableFrame(ObservationsTableFrame):
    CODE = 'GONS'
    def display_ob_table_heading(self):
        heading_style = ttk.Style()
        heading_style.configure('Heading.TLabel', font=('Sans', '10', 'bold'), padding=(5,5))
        
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0,
                row=self.HEADING_ROW-1, columnspan=20, sticky='ew')
        ttk.Label(self, text='Ob No.', style='Heading.TLabel').grid(column=1, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='Hz', style='Heading.TLabel').grid(column=2, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='V', style='Heading.TLabel').grid(column=3, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='SD', style='Heading.TLabel').grid(column=4, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='HD', style='Heading.TLabel').grid(column=5, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='Face', style='Heading.TLabel').grid(column=6, row=self.HEADING_ROW, sticky='EW') 
        ttk.Label(self, text=u'\u0394 Hz', style='Heading.TLabel').grid(column=8, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='mm/HD', style='Heading.TLabel').grid(column=9, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='Act.', style='Heading.TLabel').grid(column=10, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text=u'\u0394 V', style='Heading.TLabel').grid(column=12, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='mm/HD', style='Heading.TLabel').grid(column=13, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='Act.', style='Heading.TLabel').grid(column=14, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text=u'\u0394 Slop. D', style='Heading.TLabel').grid(column=16, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text=u'\u0394 Hori. D', style='Heading.TLabel').grid(column=17, row=self.HEADING_ROW, sticky='EW')
        ttk.Label(self, text='Act.', style='Heading.TLabel').grid(column=18, row=self.HEADING_ROW, sticky='EW')
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0,
                row=self.HEADING_ROW+1, columnspan=20, sticky='ew')

    def set_ob_label_processors(self):
        LabelProcessor = ObservationLabelProcessorFactory.label_processor(
            self.controller.survey_processor.settings.angular_unit
        )
        if LabelProcessor:
            self.ob_label_processors = [LabelProcessor(self, ob, ob_num+1,
                    self.controller.survey_processor) 
                    for ob_num, ob in enumerate(self.target.observations)]


class DMSObservationTableFrame(GonObservationsTableFrame):
    CODE = 'DMS'
    # No implmentation as of yet
    pass 


class ObservationLabelProcessorFactory:
    """Factory that returns the correct observation label
    processor based on the angular settings unit"""
    PROCESSOR_CODE = ('GONS', 'DMS')
    PROCESSOR_TABLES = (GonObservationLabelProcessor, DMSObservationLabelProcessor) 

    @classmethod
    def label_processor(cls, processor_code):
        if processor_code in cls.PROCESSOR_CODE:
            for processor in cls.PROCESSOR_TABLES:
                if processor.CODE == processor_code:
                    return processor


class ObservationTableFrameFactory:
    """Factory than returns the correct observation table 
    based on the angular settings unit"""
    TABLE_CODE = ('GONS', 'DMS')
    OB_TABLES =  (GonObservationsTableFrame, DMSObservationTableFrame)

    @classmethod
    def observation_table(cls, table_code):
        if table_code in cls.TABLE_CODE:
            for table in cls.OB_TABLES:
                if table.CODE == table_code:
                    return table 


    
class ObservationDetailsFrame(tk.Toplevel):
    def __init__(self, container, controller, observation, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.title('Observation Details')
        self.resizable(False, False)
        self.linear_precision = controller.survey_processor.settings.linear_precision
        self.angular_precision = controller.survey_processor.settings.angular_precision
        self.ob = observation
        self.pop_up_frame = ttk.Frame(self)
        self.pop_up_frame.grid(column=0, row=0, padx=10, pady=10,
            sticky='NESW')

        self.display_attribute_name()
        self.display_attribute()

    def convert_angle(self, gons_angle, precesion):
        return self._precision_format(gons_angle, precesion)


    def display_attribute_name(self):
        ttk.Label(self.pop_up_frame, text='Target Name:').grid(column=0, row=0, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Target Height:').grid(column=0, row=1, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Hz:').grid(column=0, row=2, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='V:').grid(column=0, row=3, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Slope Distane:').grid(column=0, row=4, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Horizontal Distance:').grid(column=0, row=5, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Horizontal Distance Scaled:').grid(column=0, row=6, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Prism Constant:').grid(column=0, row=7, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='ATR:').grid(column=0, row=8, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Face:').grid(column=0, row=9, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Date Time:').grid(column=0, row=10, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Instrument Level:').grid(column=0, row=11, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Scale Factor:').grid(column=0, row=12, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Geometric PPM:').grid(column=0, row=13, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Atmospheric PPM:').grid(column=0, row=14, sticky='W', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text='Code:').grid(column=0, row=15, sticky='W', padx=2, pady=2)

    def display_attribute(self):
        ttk.Label(self.pop_up_frame, text=self.ob.target_name).grid(column=1, row=0, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=f'{self.ob.target_height:.3f}').grid(column=1, row=1, sticky='E', padx=2, pady=2)
        
        # HZ
        ttk.Label(self.pop_up_frame, text=self.convert_angle(
                self.ob.hz_angle, self.angular_precision)).grid(column=1, row=2, sticky='E', padx=2, pady=2)
        
        #V
        ttk.Label(self.pop_up_frame, text=self.convert_angle(
                self.ob.za_angle, self.angular_precision)).grid(column=1, row=3, sticky='E', padx=2, pady=2)
        
        ttk.Label(self.pop_up_frame, text=self._precision_format(
                self.ob.slope_distance, self.linear_precision)).grid(column=1, row=4, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=self._precision_format(
                self.ob.no_scale_hor_dist, self.linear_precision)).grid(column=1, row=5, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=self._precision_format(
                self.ob.scale_hor_dist, self.linear_precision)).grid(column=1, row=6, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=f'{self.ob.prism_constant:.1f}').grid(column=1, row=7, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=self.ob.atr_status()).grid(column=1, row=8, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=self.ob.face).grid(column=1, row=9, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=self.ob.date_time).grid(column=1, row=10, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=str(self.ob.instrument_level())).grid(column=1, row=11, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=self.ob.scale_factor).grid(column=1, row=12, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=self.ob.geometric_ppm).grid(column=1, row=13, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=self.ob.atmos_ppm).grid(column=1, row=14, sticky='E', padx=2, pady=2)
        ttk.Label(self.pop_up_frame, text=self.ob.code).grid(column=1, row=15, sticky='E', padx=2, pady=2)

    @staticmethod
    def _precision_format(measurement, places):
        """Returns the string format for an angle based on 
        the decimal places"""
        return '{m:.{places}f}'.format(m=measurement, places=places)


class DMSObservationTableFrame(ObservationDetailsFrame):
    def convert_angle(self, gons_angle, precesion):
        """returns a gon angle to a dms string"""
        return dms_to_str(gons_to_dms(gons_angle))

      


