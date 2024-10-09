import os 
from pathlib import Path

from starnet_formatter.importer_processors import FormatFileProcessor
from starnet_formatter.survey_processors import SurveyProccesor
from starnet_formatter.configuration  import Settings, ExportSettings 


class StarnetFormatterProject:
    FILETYPE = [('Starnet Convertor Project', '.scpj')]
    def __init__(self, path_str):
        self._project_path = Path(path_str)
        self.settings = Settings()
        self.survey_processor = None 
        self.format_file_processor = None
        self.import_file_org = ImportedFileOrgainser()
      
    def has_active_setups(self):
        """returns a boolean if the project has 
        setups"""
        if self.survey_processor:
            return len(self.survey_processor.setups) > 0
        return False 
    
    def process_files(self):
        """Processes files within a project"""
        self.format_file_processor = FormatFileProcessor(self.settings, self.import_file_org)
        self.survey_processor = SurveyProccesor(self.settings)
        self.format_file_processor.process_files()
        self.survey_processor.add_setups(self.format_file_processor.setups())

    @property 
    def project_path(self):
        return self._project_path 

    @project_path.setter
    def project_path(self, path_str):
        """Accepts a string path and coverts to Path 
        object befor assigning it to project path"""
        try:
            self._project_path = Path(path_str)
        except TypeError:
            pass 

    def __str__(self):
        if self.project_path and self.project_path.exists():
            return os.path.basename(self.project_path)
        return ''

class ImportedFileOrgainser: 
    ALLOWED_FILE_TYPES = ('csv', 'txt', 'dat')
    def __init__(self):
        # holds a list of paths 
        self.imported_files = []

    def is_empty(self):
        """Returns a boolean if the imported 
        file orgainser is empty"""
        return len(self.imported_files) == 0 

    def add_files(self, file_paths):
        """returns a list of imported files"""
        return [self.add_file(f) for f in file_paths]
      
    def add_file(self, file_path):
        """returns a single imported file"""
        if self.check_file_type_allowed(file_path) and \
                not self.check_path_exists(file_path):
            imported_file = ImportedFile(file_path)
            self.imported_files.append(imported_file)
            return imported_file
        return file_path

    def remove_non_active_files(self):
        self.imported_files = [f for f in self.imported_files 
            if not f.file_active]
        
    def remove_file(self, file_path):
        if self.check_path_exists(file_path):
            self.imported_files.remove(file_path)

    def check_file_type_allowed(self, file_path):
        """checks the format file is an allowed type before import"""
        return file_path.split('.')[-1].lower() in self.ALLOWED_FILE_TYPES
      
    def check_path_exists(self, file_path):
        for f in self.imported_files:
            if os.path.normpath(file_path) == f.normpath:
                return True 
        return False

    def __iter__(self):
        for f in self.imported_files:
            yield f

    def __len__(self):
        return len(self.imported_files)

          
class ImportedFile:
    def __init__(self, file_path):
        self.path = Path(file_path)
        self.file_active = True 

    @property 
    def exists(self):
        return self.path.exists()
  
    @property
    def file_name(self):
        """returns the file name of the imported file
        if the path exists"""
        if self.exists:
            return os.path.basename(self.path)
    
    @property
    def normpath(self):
        return os.path.normpath(self.path)

    @property 
    def directory(self):
        """returns the directory path of the imported file
        if the path exists"""
        if self.exists:
           return os.path.dirname(self.path)

    def file_active_toggle(self):
        """toggles the state of file active"""
        self.file_active = not self.file_active

    def file_type(self):
        """returns the file path"""
        ft = os.path.splitext(self.path)
        if ft:
            return ft[-1]

    def __str__(self):
        return self.file_name 

    def __repr__(self):
        return self.file_name

    