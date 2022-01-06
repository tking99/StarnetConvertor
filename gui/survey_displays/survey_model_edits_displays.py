from decimal import Decimal
import tkinter as tk 
from tkinter import ttk


class SetupEditFrame(tk.Toplevel):
    def __init__(self, container, controller, setup, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.container = container
        self.setup = setup
        self.controller = controller
        self.station_name = tk.StringVar(value=self.setup.name)
        self.instrument_height = tk.StringVar(value=self.setup.instrument_height)
        self.atmos_ppm = tk.StringVar(value=self.setup.atmospheric_ppm)
        self.scale_factor = tk.StringVar(value=self.setup.scale_factor)
        
        self.title('Edit Setup')
        self.resizable(False, False)

        pop_up_frame = ttk.Frame(self)
        pop_up_frame.grid(column=0, row=0, padx=10, pady=10,
            sticky='NESW')

        s1 = ttk.Style()
        s1.configure('SetupEdit.TLabel', font=('Sans', '9', 'bold'),
            padding=(4,4,4,4))

        vcmd = (self.register(self.validate_num_entry))

        # setup name
        ttk.Label(pop_up_frame, text="Setup ID", style='SetupEdit.TLabel').grid(column=0, row=1, sticky="W")
        ttk.Entry(pop_up_frame, textvariable=self.station_name).grid(column=1, row=1)

        # instrument height 
        ttk.Label(pop_up_frame, text="Instrument Height (m)", style='SetupEdit.TLabel').grid(column=0, row=2,
            sticky="W")
        ttk.Entry(pop_up_frame, textvariable=self.instrument_height,
            validate='key', validatecommand=(vcmd, '%P')).grid(column=1, row=2, padx=4, pady=4)

        # atmos ppm
        ttk.Label(pop_up_frame, text="Atmos PPM", style='SetupEdit.TLabel').grid(column=0, row=3,
            sticky="W")
        atmos_ppm = ttk.Entry(pop_up_frame, textvariable=self.atmos_ppm,
            validate='key', validatecommand=(vcmd, '%P'))
        atmos_ppm.grid(column=1, row=3, padx=4, pady=4)

        # scale factor 
        ttk.Label(pop_up_frame, text="Scale Factor (m)", style='SetupEdit.TLabel').grid(column=0, row=4,
            sticky="W")
        scale_factor = ttk.Entry(pop_up_frame, textvariable=self.scale_factor,
            validate='key', validatecommand=(vcmd, '%P'))
        scale_factor.grid(column=1, row=4, padx=4, pady=4) 
        
        # buttons 
        ttk.Button(pop_up_frame, text="Apply", command=self.update_setup).grid(column=0,
            row=5, padx=6, pady=4, sticky="W")
        ttk.Button(pop_up_frame, text="Cancel", command=self.cancel).grid(column=1, row=5,
            padx=6, pady=4, sticky="W")
    
    def update_setup(self):
        """Updates a setup with latest values""" 
        # validate scale before continuing
        old_atmos = self.setup.atmospheric_ppm
        if self._validate_scale_factor(float(self.scale_factor.get())):
            name = self.station_name.get()
            ih = self.instrument_height.get()
            atmos_ppm = self.atmos_ppm.get()
            # check if atmos has chaned, if so setup frame needs to be refreshed
            atmos_changed = self.check_atmos_changed(atmos_ppm)
            sf = self.scale_factor.get()

            # update the setup object 
            self.controller.survey_processor.update_setup(
                self.setup, name,ih,atmos_ppm, sf)

            # update labels
            self.container.update_setup_info(self.setup.name, 
                self.setup.instrument_height, self.setup.scale_factor,
                self.setup.atmospheric_ppm)
        

            # Update setup tab with latest name
            self.controller.controller.current_setup_tab_frame.update_current_button(
                self.setup.name
            )
            self.destroy()

            # update the setup frame
            if atmos_changed:
                tk.messagebox.showinfo(title='Atmospheric PPM Adjustment',
                    message = f'Scaling distances by {self.setup.atmospheric_ppm-old_atmos} PPM')
                
                self.controller.controller.update_current_setup_frame()
        else:
            tk.messagebox.showerror(title='Incorrect Scale Factor',
            message='Scale factor needs to be a positive number')

    def check_atmos_changed(self, new_atmos): 
        return str(self.setup.atmospheric_ppm) != new_atmos
            
    
    
    def _validate_scale_factor(self, sf):
        """validates to check that the scale factor is a postive number"""
        return sf > 0

    
    def validate_num_entry(self, entry):
        """Check if the entry can be parsed to a float"""
        if entry != "" and entry != "-":
            try:
                float(entry)
            except ValueError:
                return False 
        return True 

    def cancel(self):
        """Doesnt set the changes to the setup and closes down the window"""
        self.destroy()


class TargetEditFrame(tk.Toplevel):
    TITLE_STRING = 'Edit Target'
    TARGET_ID_STRING = 'Target ID'
    TARGET_HEIGHT_STRING = 'Target Height (m)'
    TARGET_PC_STRING = 'Target Prism Constant (mm)'
    def __init__(self, container, controller, target, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.container = container
        self.controller = controller
        self.target = target
        self.target_name = tk.StringVar(value=target.name)
        self.target_height = tk.StringVar(value=target.target_height)
        self.target_pc = tk.StringVar(value=f'{target.prism_constant:.1f}')
        self.title(self.TITLE_STRING)
        self.resizable(False, False)

        vcmd = (self.register(self.validate_num_entry))

        pop_up_frame = ttk.Frame(self)
        pop_up_frame.grid(column=0, row=0, padx=10, pady=10,
            sticky='NESW')

        s1 = ttk.Style()
        s1.configure('TargetEdit.TLabel', font=('Sans', '9', 'bold'),
            padding=(4,4,4,4))

         # target name
        ttk.Label(pop_up_frame, text=self.TARGET_ID_STRING, style='TargetEdit.TLabel'
            ).grid(column=0, row=1, sticky="W")
        name = ttk.Entry(pop_up_frame, textvariable=self.target_name)
        name.grid(column=1, row=1, padx=4, pady=4)

        # target height 
        ttk.Label(pop_up_frame, text=self.TARGET_HEIGHT_STRING, style='TargetEdit.TLabel'
            ).grid(column=0, row=2,sticky="W")
        ih = ttk.Entry(pop_up_frame, textvariable=self.target_height,
            validate='key', validatecommand=(vcmd, '%P'))
        ih.grid(column=1, row=2, padx=6, pady=4)

        # prism constant 

        ttk.Label(pop_up_frame, text=self.TARGET_PC_STRING, style='TargetEdit.TLabel',
        ).grid(column=0, row=3, sticky='W')
        pc = ttk.Entry(pop_up_frame, textvariable=self.target_pc,
            validate='key', validatecommand=(vcmd, '%P'))
        pc.grid(column=1, row=3, padx=6, pady=4)

        # buttons 
        ttk.Button(pop_up_frame, text="Apply" , command=self.update_target).grid(
            column=0, row=4, padx=4, pady=4, sticky='W')
        ttk.Button(pop_up_frame, text="Cancel", command=self.cancel).grid(
            column=1, row=4, padx=6, pady=4, sticky='W')

    def update_target(self):
        """Updates a setup with latest values"""
        # check if PC is changed, if so ask user to check if they want confirm change
        new_pc = self.target_pc.get()
        if Decimal(new_pc) != self.target.prism_constant:
            tk.messagebox.showinfo(title='Prism Constant Adjustment',
                    message = f'Scaling observation distances by {self.target.prism_constant-Decimal(new_pc):.1f} mm.')

        self.container.update_target_info(self.target_name.get(),
            self.target_height.get(), self.target_pc.get())
        self.destroy()

    def validate_num_entry(self, entry):
        """Check if the entry can be parsed to a float"""
        if entry != "" and entry != "-":
            try:
                float(entry)
            except ValueError:
                return False 
        return True

    def cancel(self):
        """Doesnt set the changes to the target and closes down the window"""
        self.destroy()


class SideShotEditFrame(TargetEditFrame):
    TARGET_ID_STRING = 'Spigot ID'
    TARGET_HEIGHT_STRING = 'Spigot Height'
    TITLE_STRING = 'Edit Spigot'