import re 

from starnet_formatter.survey_processors import SurveyProccesor
from starnet_formatter.factories import FormatObLineBuilderFactory
from starnet_formatter.builders import FormatFileSetupLineBuilder, FormatFileObLineBuilder, FormatFileJobLineBuilder
from starnet_formatter.surveyModels import Setup, Observation, Job


class FormatFileProcessor:
    def __init__(self, settings, imported_file_org):
        self.settings = settings
        self.imported_files = imported_file_org
      
    def process_files(self):  
        self.format_lines_processors = []
        for imported_file in self.imported_files:
            #check if the file exists and is active before processing
            if imported_file.exists and imported_file.file_active:
                # process file and add format_lines process to the list
                self.format_lines_processors.append(self._process_file(imported_file))

    def _process_file(self, imported_file):
        """Processes a file and returns a format lines processor"""
        format_lines_processor = FormatLinesProcessor(self.settings, imported_file)
        with open(imported_file.path, 'r') as reader:
            format_lines = reader.readlines()
            format_lines_processor.process_format_lines(format_lines)
        return format_lines_processor 

    @property
    def total_imported_setups(self):
        return len(self.setups())
    
    @property
    def total_imported_target_obs(self):
        if self.setups:
            return sum((setup.total_target_observations for setup in self.setups()))

    @property 
    def total_imported_side_shot_obs(self):
        if self.setups:
            return sum((setup.total_side_shot_observations for setup in self.setups()))
            
    def setups(self):
        """returns a list of setups"""
        return [setup for flp in self.format_lines_processors for 
            setup in flp.setups]

    def format_errors(self):
        """returns a list of format errors 
        associated to the process"""
        return [flp.format_errors for flp in self.format_lines_processors if flp.errors_exist()]
    
    @property
    def total_errors(self):
        return sum((len(flp.errors) for flp in self.format_lines_processors))
    
    @property
    def errors_exist(self):
        return self.total_errors > 0


    
class FormatLinesProcessor:
    def __init__(self, settings, file_name):
        self.file_name = file_name
        self.settings = settings
        self._setups = []
        self._current_setup = None
        self.format_errors = FormatLinesProcessorErrors(file_name)
        # get the right ob line builder based on the settings passed in
        self.builders = (FormatObLineBuilderFactory.builder(self.settings.angular_unit), 
            FormatFileSetupLineBuilder, FormatFileJobLineBuilder)

    @property
    def errors(self):
        """Returns the line errors associated to the 
        format lines processor"""
        return self.format_errors.line_errors
    
    def errors_exist(self):
        """returns a boolean depending on if errors 
        exist"""
        return self.format_errors.errors_exist()
    
    @property
    def setups(self):
        """finishes the build and returns the setups"""
        self._finish_build()
        return self._setups

    def process_format_lines(self, format_lines):
        """Proccesses format_lines"""
        for line_number, format_line in enumerate(format_lines):
            line_number += 1
            format_line_split = format_line.split()
            if format_line_split:
                self._process_format_line(line_number, format_line_split)

    def _process_format_line(self, line_number, format_line):
        format_code = self._get_format_code(format_line)
        # get builder class
        Builder = self._get_builder(format_code)
        if Builder:
            # instantainte builder object
            builder = Builder(format_line, line_number)
            # add errors 
            self.format_errors.add_errors(builder)
            # build the object
            build = builder.build()
            # process the build 
            self._process_build(build)
        # if not builder than  not compatiable with survey processor
    
    def _finish_build(self):
        """Checks if there is a current setup, if so adds 
        to the list of setups and sets to None again"""
        if self._current_setup is not None:
            # if setup has no observation, don't add to the list of setups
            total_obs = self._current_setup.total_target_observations + self._current_setup.total_side_shot_observations
            if total_obs > 0:
                self._setups.append(self._current_setup)
            self._current_setup = None 

    def _process_build(self, build):
        if isinstance(build, Setup):
            # Setup built
            # set setup instrument type to default from settings file
            build.instrument_type = self.settings.instrument_type
            if self._current_setup:
                self._setups.append(self._current_setup)
            self._current_setup = build 
        
        elif isinstance(build, Observation):
            # Observation built
            if self._current_setup:
                # check if side shot or target ob
                if self._check_side_shot(build):
                    # extract prefix 
                    self._extract_side_shot_prefix(build)
                    self._current_setup.add_side_shot_observation(build)
                else:
                    self._current_setup.add_observation(build)
            else:
                # not current_setup to assign observation - log error
                build.add_no_setup_error()
                self.format_errors.add_errors(build)
        
        elif isinstance(build, Job):
            """set the comment surveyor to the saved surveyor name from
            the job"""
            self.settings.export_settings.comments.surveyor = build.surveyor


    def _check_side_shot(self, observation):
        """Checks if the observation is a side shot based 
        on checking the prefix to the observation name"""
        if self.settings.capature_side_shots:
            return re.match(f'^{self.settings.side_shot_prefix}',
                observation.target_name) is not None 

    def _extract_side_shot_prefix(self, observation):
        """extracts the prefix from the observation name"""
        try:
            observation.target_name = observation.target_name[len(self.settings.side_shot_prefix):]
        except IndexError:
            pass 
           
    def _get_builder(self, format_code):
        for builder in self.builders:
            if builder.FORMAT_CODE == format_code:
                return builder 

    def _get_format_code(self, format_line):
        """Gets the format code from the format_line"""
        return format_line[0]


class FormatLinesProcessorErrors:
    def __init__(self, file_name):
        self.file_name = file_name
        self.line_errors = []

    def errors_exist(self):
        """returns a boolean if errors exist"""
        return len(self.line_errors) > 0
            
    def add_errors(self, builder):
        """Adds the errors to the correct list based on the builder type"""
        if builder.errors:
            self.line_errors.extend(builder.errors)


class CompanyDefFileProcessor:
    """Reads and processes a Star*net company def file to 
    extract instrument specifications""" 

    @classmethod 
    def extract_instrument_types(cls, def_file):
        """returns a tuple of the different instrument types 
        from a star*net company def file"""
        with open(def_file, 'r') as f:
            lines = f.readlines()
            instrument_types = []
            for l in lines:
                splitted = l.split()
                if splitted and splitted[0] == 'instrument_name' and len(splitted) >=2: 
                    instrument_types.append(splitted[1])
        return instrument_types