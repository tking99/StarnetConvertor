import tkinter as tk 
from tkinter import ttk


class SettingsDisplay(tk.Toplevel):
    """Top level display that requires a settings instance"""
    def __init__(self, container, settings, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        pop_up_frame = ttk.Frame(self)
        pop_up_frame.grid(column=0, row=0, padx=10, pady=10,
            sticky='NSEW')

        self.title('Project Settings')
        self.resizable(False, False)

        self.settings = settings
        self.dist_value = tk.StringVar(value=self.settings.distance_tolerance)
        self.hz_value = tk.StringVar(value=self.settings.hz_angle_tolerance)
        self.za_value = tk.StringVar(value=self.settings.za_angle_tolerance)
        self.linear_precision = tk.StringVar(value=self.settings.linear_precision)
        self.angular_precision = tk.StringVar(value=self.settings.angular_precision)

        # Used for Entry tolerance validation
        vcmd = (self.register(self.validate_num_entry))

        vcmd2 = (self.register(self.validate_precision_entry))

        ttk.Label(pop_up_frame, text='Statistical Tolerances').grid(column=0, row=0, padx=3, sticky='W')
        ttk.Label(pop_up_frame, text='Distance Tol. (m)').grid(column=0, row=1, pady=6, padx=3, sticky='W')
        
        ttk.Entry(pop_up_frame, width=10, textvariable=self.dist_value,
            validate='key', validatecommand=(vcmd, '%P')).grid(column=1, row=1, pady=6, padx=3, sticky='W')
        
        ttk.Label(pop_up_frame, text='Hz Angle Tol. (gon)').grid(column=0, row=2, pady=6, padx=3, sticky='W')
        
        ttk.Entry(pop_up_frame, width=10, textvariable=self.hz_value,
            validate='key', validatecommand=(vcmd, '%P')).grid(column=1, row=2, pady=6, padx=3, sticky='W')

        ttk.Label(pop_up_frame, text='V Angle Tol. (gon)').grid(column=0, row=3, pady=6, padx=3, sticky='W')
        ttk.Entry(pop_up_frame, width=10, textvariable=self.za_value,
            validate='key', validatecommand=(vcmd, '%P')).grid(column=1, row=3, pady=6, padx=3, sticky='W')
        
        ttk.Label(pop_up_frame, text='Angular Unit').grid(column=0, row=4, pady=6, padx=3, sticky='W')
        self.angular_unit = tk.StringVar(value=self.settings.angular_unit)
        angular_radio_frame = ttk.Frame(pop_up_frame)
        angular_radio_frame.grid(column=1, row=4)
        ttk.Radiobutton(angular_radio_frame, text='GONS', variable=self.angular_unit,
            value='GONS').grid(column=0, row=0, pady=6, padx=3, sticky='W')
        ttk.Radiobutton(angular_radio_frame, text='DMS', variable=self.angular_unit,
            value='DMS').grid(column=1, row=0, pady=6, padx=3, sticky='W')
        
        self.capature_side_shots = tk.BooleanVar(value=self.settings.capature_side_shots)
        self.side_shot_prefix = tk.StringVar(value=self.settings.side_shot_prefix)

        ttk.Label(pop_up_frame, text='Capaute Side Shots').grid(column=0, row=5, pady=2, padx=3, sticky='W')
        ttk.Checkbutton(pop_up_frame, variable=self.capature_side_shots, onvalue=True,
            offvalue=False, command=self.capature_side_shots_toggle).grid(
                column=1, row=5, pady=6, padx=3, sticky='W')

        self.side_shot_label = ttk.Label(pop_up_frame, text='Side Shot Prefix')
        self.side_shot_label.grid(column=0, row=6, pady=2, padx=3, sticky='W')
        self.side_shot_entry = ttk.Entry(pop_up_frame, width=10, textvariable=self.side_shot_prefix)
        self.side_shot_entry.grid(column=1,row=6, pady=2, padx=3, sticky='W')

        linear_precision_label = ttk.Label(pop_up_frame, text='Linear Precision').grid(
            column=0, row=7, pady=2, padx=3, sticky='W')
        
        self.linear_precision_entry = ttk.Entry(pop_up_frame, width=10, textvariable=self.linear_precision,
            validate='key', validatecommand=(vcmd2, '%P'))
        self.linear_precision_entry.grid(column=1, row=7, pady=2, padx=3, sticky='W')

        angular_precision_label = ttk.Label(pop_up_frame, text='Angular Precision').grid(
            column=0, row=8, pady=2, padx=3, sticky='W')
        
        self.angular_precision_entry = ttk.Entry(pop_up_frame, width=10, textvariable=self.angular_precision,
            validate='key', validatecommand=(vcmd2, '%P'))
        self.angular_precision_entry.grid(column=1, row=8, pady=2, padx=3, sticky='W')



        ttk.Button(pop_up_frame, text='Apply', command=self.save_settings).grid(
            column=0, row=9, pady=3, padx=3, sticky='W'
        )
        ttk.Button(pop_up_frame, text='Cancel', command=self.destroy).grid(
            column=1, row=9, pady=3, padx=3,sticky='W'
        )
    
    def validate_num_entry(self, entry):
        """Excepts emptry string or within the tolerances defined 
        in settings range"""
        if entry == "" or self.settings.check_distance_tolerance(entry):
            return True 
        return False 
    
    def validate_precision_entry(self, entry):
        if entry == "":
            return True 
        try: 
            int(entry)
            return True 
        except ValueError:
            return False
        

    def capature_side_shots_toggle(self):
        """toggles the capature side shot checkbox and 
        apply state to the prefix label"""
        self.settings.apply_capature_side_shots_toggle()
        state = 'normal'
        if not self.settings.capature_side_shots:
            state='disabled'
        self.side_shot_label.configure(state=state)
        self.side_shot_entry.configure(state=state)
        

    def validate_tolerance(self, tolerance):
        """Validate function that check if the 
        passed in Entry tolerance can be accepted"""
        return self.settings.check_distance_tolerance(tolerance)
        
    def save_settings(self):
        """Saves the settings with the new values"""
        self.settings.distance_tolerance = self.dist_value.get()
        self.settings.hz_angle_tolerance = self.hz_value.get()
        self.settings.za_angle_tolerance = self.za_value.get()
        self.settings.angular_unit = self.angular_unit.get()
        self.settings.side_shot_prefix = self.side_shot_prefix.get()
        self.settings.angular_precision = int(self.angular_precision.get())
        self.settings.linear_precision = int(self.linear_precision.get())
        self.destroy()
        

  
    