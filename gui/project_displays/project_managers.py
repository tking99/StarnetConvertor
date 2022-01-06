import tkinter as tk 
from tkinter import ttk 
from tkinter.filedialog import asksaveasfile, askopenfile

from starnet_formatter.file_models import StarnetFormatterProject
from starnet_formatter.pickler import ProjectPickler


class ProjectDisplayManager:    
    @classmethod 
    def new_project(self):
        """Creates a new project"""
        project_path = asksaveasfile(filetypes=StarnetFormatterProject.FILETYPE,
            defaultextension=StarnetFormatterProject.FILETYPE[0][1])
        if project_path:
            project = StarnetFormatterProject(project_path.name)
            # dump the project 
            ProjectPickler.dump_project(project)
            return project

    @classmethod 
    def open_project(cls):
        """Opens an existing project"""
        project_path = askopenfile(filetypes=StarnetFormatterProject.FILETYPE,
            defaultextension=StarnetFormatterProject.FILETYPE[0][1])
        if project_path:
            return ProjectPickler.load_project(project_path.name)

    @classmethod
    def save_project(cls, project):
        """Saves an existing project"""
        ProjectPickler.dump_project(project)

    @classmethod 
    def save_as_project(cls, project):
        """Saves as an existing project"""
        project_path = asksaveasfile(filetypes=StarnetFormatterProject.FILETYPE,
            defaultextension=StarnetFormatterProject.FILETYPE[0][1])
        if project_path:
            project.project_path = project_path.name
            ProjectPickler.dump_project(project)


