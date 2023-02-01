import tkinter as tk 
from tkinter import ttk
from tkinter.filedialog import asksaveasfile, askopenfile


class ExportSettingsDisplay(tk.Toplevel):
    def __init__(self, container, settings, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.container = container
        self.settings = settings 
        self.export_settings = settings.export_settings
        self.title('Export Settings')
        self.resizable(False, False)
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(column=0, row=0, sticky='NSEW')
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Format Section
        left_container = ttk.Frame(self.main_frame)
        left_container.grid(column=0, row=0, padx=10, pady=10)
        
        stn_order_container = ttk.Frame(left_container)
        stn_order_container.grid(column=0, row=0, sticky='NW')

        ttk.Label(stn_order_container, text='Station Order').grid(column=0, row=0, pady=2, padx=3, sticky='EW')
        self.station_order = tk.StringVar(value=self.export_settings.station_order)
        ttk.Radiobutton(stn_order_container, text='At-From-To', variable=self.station_order,
            value='AT-FROM-TO', command=self.update_station_order).grid(column=0, row=1, pady=2, padx=3, sticky='E')
        ttk.Radiobutton(stn_order_container, text='From-At-To', variable=self.station_order,
            value='FROM-AT-TO', command=self.update_station_order).grid(column=0, row=2, pady=2, padx=3, sticky='E')

        # define Distance / Vertical Type 
        meas_format_container = ttk.Frame(left_container)
        meas_format_container.grid(column=0, row=1, sticky='NW', pady=(30,0))
    
        ttk.Label(meas_format_container, text='Distance / Vertical Data Type'
            ).grid(column=0, row=0, pady=2, padx=3, sticky='EW')
        self.measurement_format = tk.StringVar(value=self.export_settings.measurement_format)
        ttk.Radiobutton(meas_format_container, text='Slope Dist / Zenith', variable=self.measurement_format,
            value='SD/V', command=self.update_measurement_format).grid(column=0, row=1, pady=2, padx=3, sticky='W')
        ttk.Radiobutton(meas_format_container, text='Horiz Dist / Elev Diff', variable=self.measurement_format,
            value='HD/E', command=self.update_measurement_format).grid(column=0, row=2, pady=2, padx=3, sticky='W')

        # Setup Scale Factor 
        setup_sf_container = ttk.Frame(left_container)
        setup_sf_container.grid(column=0, row=2, sticky='NW', pady=(10,0), padx=(5,0))
        ttk.Label(setup_sf_container, text='Setup Inline Scale Factor').grid(
            column=0, row=0, pady=2, padx=3, sticky='EW'
        )

        self.apply_setup_sf = tk.BooleanVar(value=self.export_settings.setup_scale_factor)
        # If measurements already scaled then disable option
        state = self._get_label_state(not settings.apply_scale_factor)
        ttk.Checkbutton(setup_sf_container, text='Add Setup Inline Scale Factor', variable=self.apply_setup_sf,
            onvalue=True, offvalue=False, 
            command=self.export_settings.apply_setup_scale_factor_toggle,
                state=state).grid(column=0, row=1)

        # Setup Instrument settings 
        setup_inst_container = ttk.Frame(left_container)
        setup_inst_container.grid(column=0, row=3, sticky='NW', pady=(10,0), padx=(5,0))
        ttk.Label(setup_inst_container, text='Setup Inline Instrument Settings').grid(
            column=0, row=0, pady=2, padx=3, sticky='EW'
        )
        self.apply_setup_inst = tk.BooleanVar(value=self.export_settings.setup_instrument_type)
        state = self._get_label_state(bool(self.settings.instrument_types))
        ttk.Checkbutton(setup_inst_container, text='Add Setup Inline Instrument Settings', variable=self.apply_setup_inst,
            command=self.export_settings.apply_setup_instrument_toggle, state=state).grid(column=0, row=1)
        
        # 2D Export
        self.export_files_2D_container = ttk.Frame(left_container)
        self.export_files_2D_container.grid(column=0, row=4, pady=(50,0), sticky='NW')
        self.export_2D_buttons = ttk.Frame(self.export_files_2D_container)
        self.export_2D_buttons.grid(column=0, row=0, sticky='NW')
        self.export_2d = tk.BooleanVar(value=self.export_settings.export2d)
        self.combine_2d = tk.BooleanVar(value=self.export_settings.combine_2D_file)
        ttk.Checkbutton(self.export_2D_buttons, text=' Export 2D', variable=self.export_2d,
            command=self.export_2D_toggle, onvalue=True, offvalue=False).grid(
            column=0, row=0, sticky='NW', pady=2, padx=3)
        ttk.Checkbutton(self.export_2D_buttons, text='Combine 2D', variable=self.combine_2d,
            command=self.combine_2D_toggle, onvalue=True, offvalue=False).grid(
            column=1, row=0, sticky='NW', pady=2, padx=3)
        self.load_2D_file_label()
        
        # Units Section
        right_contaner = ttk.Frame(self.main_frame)
        right_contaner.grid(column=1, row=0, padx=10, pady=10, sticky='NW')
        units_container = ttk.Frame(right_contaner)
        units_container.grid(column=0, row=0, sticky='NW')
        ttk.Label(units_container, text='Units').grid(column=0, row=0, sticky='NW')
        ttk.Label(units_container, text='Linear').grid(column=0, row=1, sticky='NW')
        self.linear_unit = tk.StringVar(value=self.export_settings.linear_unit)
        linear_combo = ttk.Combobox(units_container, textvariable=self.linear_unit,
            values=self.export_settings.ALLOWED_LINEAR_UNITS)
        linear_combo.grid(
                column=1, row=1, sticky='NW')
        linear_combo.current(0)
        linear_combo.bind('<<ComboboxSelected>>', self.update_linear_unit)

        ttk.Label(units_container, text='Angular').grid(column=0, row=2, sticky='NW')
        self.angular_unit = tk.StringVar(value=self.export_settings.angular_unit)
        ttk.Radiobutton(units_container, text='GONS', variable=self.angular_unit,
            value='GONS', command=self.update_angular_unit).grid(column=1, row=2, pady=2, padx=3, sticky='W')
        ttk.Radiobutton(units_container, text='DMS', variable=self.angular_unit,
            value='DMS', command=self.update_angular_unit).grid(column=1, row=3, pady=2, padx=3, sticky='W')

        # Comments Section
        comments_container = ttk.Frame(right_contaner)
        comments_container.grid(column=0, row=1, sticky='NW', pady=10)
        self.apply_comments = tk.BooleanVar(value=self.export_settings.comments.apply_comments)
        
        comments_label_container = ttk.Frame(comments_container)
        comments_label_container.grid(column=0, row=0, sticky='NW')
        ttk.Label(comments_label_container, text='Comments').grid(column=0, row=0, sticky='NW')
        ttk.Checkbutton(comments_label_container, command=self.comments_toggle,
            variable=self.apply_comments, text='add comments',
            onvalue=True, offvalue=False).grid(column=1, row=0, sticky='NW',
                padx=10)

        # Comment options 
        self.atmospheric_ppm = tk.BooleanVar(value=self.export_settings.comments.atmospheric_ppm)
        self.scale_factor = tk.BooleanVar(value=self.export_settings.comments.scale_factor)
        self.date_time = tk.BooleanVar(value=self.export_settings.comments.date_time)
        self.code = tk.BooleanVar(value=self.export_settings.comments.code)
        self.comment_options_container = ttk.Frame(comments_container)
        self.comment_options_container.grid(column=0, row=2, stick='NW')
       
        self.atmos_lb = ttk.Checkbutton(self.comment_options_container, command=self.export_settings.comments.atmospheric_ppm_toggle,
            variable= self.atmospheric_ppm, text='Atmospheric PPM',
            onvalue=True, offvalue=False)
        self.atmos_lb.grid(column=0, row=0, sticky='NW')
        
        self.sf_lb = ttk.Checkbutton(self.comment_options_container, command=self.export_settings.comments.scale_factor_toggle,
            variable=self.scale_factor, text='Scale Factor',
            onvalue=True, offvalue=False)
        self.sf_lb.grid(column=0, row=1, sticky='NW')
        
        self.date_lb = ttk.Checkbutton(self.comment_options_container, command=self.export_settings.comments.date_time_toggle,
            variable=self.date_time, text='Date/Time',
            onvalue=True, offvalue=False)
        self.date_lb.grid(column=1, row=0, sticky='NW')
        
        self.code_lb = ttk.Checkbutton(self.comment_options_container, command=self.export_settings.comments.code_toggle,
            variable=self.code, text='Code',
            onvalue=True, offvalue=False)
        self.code_lb.grid(column=1, row=1, sticky='NW')

        self.survey_frame = ttk.Frame(comments_container)
        self.survey_frame.grid(column=0, row=3, pady=(10,10))
        
        self.surveyor = tk.StringVar(value=self.export_settings.comments.surveyor)
        ttk.Label(self.survey_frame, text='Surveyor:').grid(column=0, row=0)
        surveyor_box = ttk.Entry(self.survey_frame, textvariable=self.surveyor)
        surveyor_box.grid(column=1, row=0, sticky='NW', padx=(5,0))


        # display the comments if checked
        self.display_comments(self.export_settings.comments.apply_comments)
        
        # Sigot Measurements
        self.spigot_container = ttk.Frame(right_contaner)
        self.spigot_container.grid(column=0, row=2, sticky='NW', pady=(10,))
        self.process_target_obs = tk.BooleanVar(value=self.export_settings.process_target_obs)
    
        ttk.Label(self.spigot_container, text='Target / Side Shot Processing').grid(column=0, row=0, sticky='NW', pady=2, padx=3)
        ttk.Checkbutton(self.spigot_container, variable=self.process_target_obs, command=self.export_settings.apply_process_target_obs_toggle,
            text='Process Target Obs.', onvalue=True, offvalue=False).grid(column=0, row=1, sticky='NW', pady=2, padx=3)
        
        self.process_side_shots = tk.BooleanVar(value=self.export_settings.process_side_shot_obs)
        ttk.Checkbutton(self.spigot_container, variable=self.process_side_shots, command=self.apply_process_side_shot_obs_toggle, 
            text='Process Side Shot Obs.', onvalue=True, offvalue=False).grid(column=0, row=3, sticky='NW', pady=2, padx=3)
            
        self.side_shot_code_frame = ttk.Frame(self.spigot_container)
        self.side_shot_code_frame.grid(column=0, row=4, sticky='NW')
        self.side_shot_code = tk.StringVar(value=self.export_settings.side_shot_processing_code)
        ttk.Label(self.side_shot_code_frame, text='Side Shot Type').grid(column=0, row=0, sticky='NW', pady=2, padx=3)
        
        ttk.Radiobutton(self.side_shot_code_frame, text="'M'", variable=self.side_shot_code,
            value='M', command=self.update_side_shot_processing_code).grid(
            column=1, row=0, sticky='NW', pady=2, padx=3)
        ttk.Radiobutton(self.side_shot_code_frame, text="'SS'", variable=self.side_shot_code,
            value='SS', command=self.update_side_shot_processing_code).grid(
            column=2, row=0, sticky='NW', pady=2, padx=3)


        # 3D Export
        self.export_files_3D_container = ttk.Frame(right_contaner)
        self.export_files_3D_container.grid(column=0, row=4, sticky='NW')
        self.export_3D_buttons = ttk.Frame(self.export_files_3D_container)
        self.export_3D_buttons.grid(column=0, row=0, sticky='NW')
        self.export_3d = tk.BooleanVar(value=self.export_settings.export3d)
        self.combine_3d = tk.BooleanVar(value=self.export_settings.combine_3D_file)
        ttk.Checkbutton(self.export_3D_buttons, text='Export 3D', variable=self.export_3d,
            command=self.export_3D_toggle, onvalue=True, offvalue=False).grid(
            column=0, row=0, sticky='NW', pady=2, padx=3)
        ttk.Checkbutton(self.export_3D_buttons, text='Combine 3D', variable=self.combine_3d,
            command=self.combine_3D_toggle, onvalue=True, offvalue=False).grid(
                column=1, row=0, stick='NW', pady=2, padx=3)
        self.load_3D_file_label()

        # Preview Buttons 
        self.main_buttons = ttk.Frame(self.main_frame)
        self.main_buttons.grid(column=1, row=1, pady=(10,10), sticky='NE')

        ttk.Button(self.main_buttons, text='Back',
            command=self.destroy).grid(column=0, row=0, sticky='E', padx=5)
        self.export_button = ttk.Button(self.main_buttons, text='Export',
            command=self.export)
        self.export_button.grid(column=1, row=0, sticky='E',
            padx=5)

    def export(self):
        # Save surveyor name
        self.export_settings.comments.surveyor = self.surveyor.get()
        # create dat files
        result_2D, result_3D = self.container.survey_processor.create_dat_files()
        if result_2D or result_3D:
            self.destroy()
            # load success message
            self.container.display_success_export(result_2D, result_3D)

    def update_station_order(self):
        self.export_settings.station_order = self.station_order.get()

    def update_angular_unit(self):
        self.export_settings.angular_unit = self.angular_unit.get() 

    def update_measurement_format(self):
        self.export_settings.measurement_format = self.measurement_format.get()

    def update_linear_unit(self, *args):
        self.export_settings.linear_unit = self.linear_unit.get()
      
    def export_2D_toggle(self):
        """Toggle for export2d and updates 2D label state"""
        self.export_settings.apply_export_2d_toggle()
        self.refresh_2D_file_label()

    def combine_2D_toggle(self):
        """Toggle for combine2d"""
        self.export_settings.apply_combine_2D_toggle()
    
    def export_3D_toggle(self):
        """Toggle for export3d and updates 3D label state"""
        self.export_settings.apply_export_3d_toggle()
        self.refresh_3D_file_label()
    
    def combine_3D_toggle(self):
        """Toggle for combined3D"""
        self.export_settings.apply_combine_3D_toggle()

    def export_spigot_toggle(self):
        """Toggle for export spigot and updates spigot label state"""
        self.export_settings.apply_export_spigot_toggle()
        self.refresh_spigot_file_label()

    def refresh_2D_file_label(self):
        self._destory_children(self.export_frame_2D)
        self.load_2D_file_label()
    
    def refresh_3D_file_label(self):
        self._destory_children(self.export_frame_3D)
        self.load_3D_file_label()
    
    def refresh_spigot_file_label(self):
        self._destory_children(self.export_frame_spigot)
        self.load_spigot_file_label()
        
    def load_2D_file_label(self):
        self.export_frame_2D = ttk.Frame(self.export_files_2D_container)
        self.export_frame_2D.grid(column=0, row=1, sticky='NW')
        export_box = self._create_export_file_box(self.export_frame_2D)
        label = ttk.Label(export_box, text=self.export_settings.file_2D_path)
        label.grid(column=0, row=0, sticky='NW')
        button = ttk.Button(self.export_frame_2D, text='Browse..', command=self.set_export_2D_path)
        button.grid(column=1, row=0)
        state = self._get_label_state(self.export_settings.export2d)
        button.configure(state=state)
        label.configure(state=state)

    def load_3D_file_label(self):
        self.export_frame_3D = ttk.Frame(self.export_files_3D_container)
        self.export_frame_3D.grid(column=0, row=1, sticky='NW', pady=(2,0))
        export_box = self._create_export_file_box(self.export_frame_3D)
        label = ttk.Label(export_box, text=self.export_settings.file_3D_path)
        label.grid(column=0, row=0, sticky='NW')
        button = ttk.Button(self.export_frame_3D, text='Browse..', command=self.set_export_3D_path)
        button.grid(column=1, row=0)
        state = self._get_label_state(self.export_settings.export3d)
        button.configure(state=state)
        label.configure(state=state)

    def load_spigot_file_label(self):
        self.export_frame_spigot = ttk.Frame(self.spigot_container)
        self.export_frame_spigot.grid(column=0, row=3, sticky='NW', pady=(5,0))
        export_box = self._create_export_file_box(self.export_frame_spigot)
        label = ttk.Label(export_box, text=self.export_settings.file_spigots_path)
        label.grid(column=0, row=0, sticky='NW')
        button = ttk.Button(self.export_frame_spigot, text='Browse..', command=self.set_export_spigot_path)
        button.grid(column=1, row=0)
        state = self._get_label_state(self.export_settings.export_spigot)
        button.configure(state=state)
        label.configure(state=state)

    def _create_export_file_box(self, container):
        """Creates an export container"""
        container = ttk.Frame(container, width=150, height=20, borderwidth=1, relief='solid')
        container.grid(column=0, row=0)
        container.grid_propagate(False)
        return container 

    def _get_label_state(self, boolean):
        if boolean:
            return 'normal'
        return 'disabled'

    def set_export_2D_path(self):
        file = self.get_dat_file(self.export_settings.combine_2D_file)
        if file: 
            self.export_settings.file_2D_path = file.name
            self.refresh_2D_file_label()
           
    def set_export_3D_path(self):
        file = self.get_dat_file(self.export_settings.combine_3D_file)
        if file:
            self.export_settings.file_3D_path = file.name
            self.refresh_3D_file_label()

    def comments_toggle(self):
        """Toggle between comment options on and 
        off"""
        self.export_settings.comments.apply_comments_toggle()
        self.display_comments(self.apply_comments.get())
    
    def display_comments(self, boolean):
        """Activate the comments if boolean, else 
        will disable them"""
        if boolean:
            self._activate_children(self.comment_options_container)
        else:
            self._disable_children(self.comment_options_container)

    def update_side_shot_processing_code(self):
        """sets the sdie side shot processing code"""
        self.export_settings.side_shot_processing_code = self.side_shot_code.get()
       
    def apply_process_side_shot_obs_toggle(self):
        """toggles between the side shot processing code being active 
        or disabled when processing side shots"""
        self.export_settings.apply_process_side_shot_obs_toggle()
        if self.export_settings.process_side_shot_obs:
            self._activate_children(self.side_shot_code_frame)
        else:
            self._disable_children(self.side_shot_code_frame)

    def _disable_children(self, frame):
        """Disable the comment options if not selected"""
        for child in frame.winfo_children():
            child.configure(state='disabled')
       
    def _activate_children(self, frame):
        """activates comments"""
        for child in frame.winfo_children():
            child.configure(state='normal')

    def get_dat_file(self, merge):
        if merge:
            return self._get_open_dat_file()
        return self._get_save_dat_file()


    def _get_save_dat_file(self):
        files = [('Dat Files', '.dat')]
        return asksaveasfile(filetypes=files, defaultextension=files[0][1])

    def _get_open_dat_file(self):
        files = [('Dat Files', '.dat')]
        return askopenfile(filetypes=files, defaultextension=files[0][1])
    
    def _destory_children(self, container):
        for child in container.winfo_children():
            child.destroy()
        

        

















