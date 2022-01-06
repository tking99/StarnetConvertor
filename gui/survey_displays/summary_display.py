import tkinter as tk 
from tkinter import ttk 


class SummaryDisplay(ttk.Frame):
    def __init__(self, container, format_file_processor, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.container = container 
        self.ffp = format_file_processor
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(column=0, row=0, sticky='NSEW', pady=5)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        self.reduction_summary = ttk.Frame(self)
        self.reduction_summary.grid(column=0, row=0, sticky='NSEW')
        ttk.Label(self.reduction_summary, text='Reduction Summary').grid(
            column=0, row=0, sticky='EW')
        ttk.Separator(self.reduction_summary, orient=tk.HORIZONTAL).grid(
            column=0, row=1, columnspan=2, sticky='EW')

        self.reduction_info = ttk.Frame(self.reduction_summary)
        self.reduction_info.grid(column=0, row=2, sticky='NSEW')

        self.total_setups = tk.StringVar(self.reduction_info, value=self.ffp.total_imported_setups)
        ttk.Label(self.reduction_info, text='Total Setups:').grid(
            column=0, row=0, padx=(3,0), pady=3, sticky='W')
        ttk.Label(self.reduction_info, textvariable=self.total_setups).grid(
            column=1, row=0, pady=3, sticky='W')
        self.total_target_obs = tk.StringVar(self.reduction_info, value=self.ffp.total_imported_target_obs)
        ttk.Label(self.reduction_info, text='Total Target Obs:').grid(
            column=0, row=1, padx=(3,0), pady=3, sticky='W')
        ttk.Label(self.reduction_info, textvariable=self.total_target_obs).grid(
            column=1, row=1, pady=3, sticky='W')

        self.total_spigot_obs = tk.StringVar(self.reduction_info, value=self.ffp.total_imported_side_shot_obs)
        ttk.Label(self.reduction_info, text='Total Spigot Obs:').grid(
            column=0, row=2, padx=(3,0), pady=3, sticky='W')
        ttk.Label(self.reduction_info, textvariable=self.total_spigot_obs).grid(
            column=1, row=2, pady=3, sticky='W')

        self.error_summary = ttk.Frame(self)
        self.error_summary.grid(column=0, row=1, sticky='NSEW')
        ttk.Label(self.error_summary, text='Reduction Errors').grid(
            column=0, row=0, sticky='EW', pady=5)
        ttk.Separator(self.error_summary, orient=tk.HORIZONTAL).grid(
            column=0, row=1, columnspan=2, sticky='EW')
        self.error_info = ttk.Frame(self.error_summary)
        self.error_info.grid(column=0, row=2, sticky='NSEW')
        self.total_errors = tk.StringVar(self.error_info, value=self.ffp.total_errors)
        ttk.Label(self.error_info, text='Total Errors:').grid(
            column=0, row=0, padx=(3,0), pady=3, sticky='W')
        ttk.Label(self.error_info, textvariable=self.total_errors).grid(
            column=1, row=0, pady=3, sticky='W')
        if self.ffp.errors_exist:
            hyper_style = ttk.Style()
            hyper_style.configure('Hyper.TLabel',
                foreground='blue')
            error_display_link = ttk.Label(self.error_info, 
                text='Display Error Log', style='Hyper.TLabel', cursor='hand2')
            error_display_link.bind('<Button-1>', self.display_error_log)
            error_display_link.grid(column=0, row=1, sticky='W', padx=(3,0),
                pady=3)
                

    def display_error_log(self, event):
        error_log_display = ErrorLogDisplay(self, 
            self.ffp.format_errors())
        error_log_display.grab_set()

            
class ErrorLogDisplay(tk.Toplevel):
    def __init__(self, container, format_errors, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.format_errors = format_errors
        self.title('Error Log')
        self.geometry('500x500')
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(column=0, row=0, sticky='NSEW')
        row = 0 
        for format_error in format_errors:
            ttk.Label(self.main_frame, text=f" File Name: '{format_error.file_name}'").grid(
                column=0, row=row, sticky='W', pady=2)
            row += 1 
            error_list = ttk.Frame(self.main_frame)
            error_list.grid(column=0, row=row, sticky='W', padx=(12,0), pady=3)
            r = 0
            row += 1 
            ttk.Separator(self.main_frame, orient=tk.HORIZONTAL).grid(
                column=0, row=row, sticky='EW', columnspan=2, pady=5)
            row += 1 
            for error in format_error.line_errors:
                ttk.Label(error_list, text=f'ERROR [Line: {error.line_number}] {error.error_statement}').grid(
                    column=0, row=r, sticky='W')
                r += 1 
        