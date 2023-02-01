import os
import pickle 

from starnet_formatter.configuration import ExportSettings

class ProjectPickler:
    @classmethod     
    def dump_project(cls, project):
        with open(project.project_path, 'wb') as f:
            pickle.dump(project, f)

    @classmethod
    def load_project(cls, project_path):
        """Checks if pickle is empty before attempting 
        to load, if empty returns None"""
        try:
            with open(project_path, 'rb') as f: 
                project = pickle.load(f)
                # check if settings is good, if not create new settings file
                if not hasattr(project.settings.export_settings, 'process_target_obs') or \
                    not hasattr(project.settings.export_settings.comments, 'surveyor'):
                    export_settings = ExportSettings()
                    project.settings.export_settings = export_settings
                return project
        except:
            return



    




 
        

  
    




   