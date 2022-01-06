from decimal import Decimal, DecimalException
from datetime import datetime

from starnet_formatter.surveyModels import GonObservation, DecimalObservation, Setup, \
    StarnetMeasurement, StarnetSetup
from starnet_formatter.extractors import FormatFileObservationElementsExtractor, FormatFileSetupElementsExtractor
from starnet_formatter.writters import *
from starnet_formatter import errors


class FormatLineBuilder:
    def convert_decimal(self, element):
        try:
            return Decimal(element)  

        except (ValueError, DecimalException):
            return 

    def convert_date_time_format(self, element):
        try:
            return datetime.strptime(
            element, '%d/%m/%y/%H:%M:%S')    
        except ValueError:
            return


class FormatFileSetupLineBuilder(FormatLineBuilder):
    """Checks that a format file setup line is correct format"""
    LINE_LENGTH = 6
    FORMAT_CODE = 'SU'
    def __init__(self, setup_line, line_number):
        self.setup_extractor = FormatFileSetupElementsExtractor()
        self.errors = []
        self.setup_line = setup_line
        self.line_number = line_number
       
        # check for errors 
        self.check_for_errors()

    def check_for_errors(self):
        """Returns the errors associated with a setup line"""
        # check length of line is good before proceeding other checks
        if self.line_length_good():
            self.instrument_height()
            self.date_time()
            self.atmospheric_ppm()
            self.scale_factor()
    
    def build(self):
        # check for errors before building the setup
        if not self.errors:
            return Setup(
                self.setup_extractor.extract_setup_name(self.setup_line),
                self.ih,
                self.date_time, 
                self.atmos_ppm,
                self.sf
            )

    def line_length_good(self):
        if len(self.setup_line) != FormatFileSetupLineBuilder.LINE_LENGTH:
            self.errors.append(errors.FormatSetupLineLengthError(self.line_number))
            return False 
        return True 
        
    def instrument_height(self):
        ih_str = self.setup_extractor.extract_instrument_height(self.setup_line)
        self.ih = self.convert_decimal(ih_str)
        if self.ih is None:
            self.errors.append(errors.FormatInstrumentHeightError(self.line_number))
   
    def date_time(self):
        date_time_str = self.setup_extractor.extract_date_time(self.setup_line)
        self.date_time = self.convert_date_time_format(date_time_str)
        if self.date_time is None:
            self.errors.append(errors.FormatDateTimeError(self.line_number))
 
    def atmospheric_ppm(self):
        atmos_ppm_str = self.setup_extractor.extract_atmospheric_ppm(self.setup_line)
        self.atmos_ppm = self.convert_decimal(atmos_ppm_str)
        if self.atmos_ppm is None:
            self.errors.append(errors.FormatAtmosphericPPMError(self.line_number))
    
    def scale_factor(self):
        sf_str = self.setup_extractor.extract_scale_factor(self.setup_line)
        self.sf = self.convert_decimal(sf_str)
        if self.sf is None:
            self.errors.append(errors.FormatScaleFactorError(self.line_number))
        
    
    def __str__(self):
        return 'Setup Builder'
  

class FormatFileObLineBuilder(FormatLineBuilder):
    """Checks that a format file obs line is correct format"""
    LINE_LENGTH = 19
    FORMAT_CODE = 'OB'
    def __init__(self, obs_line, line_number):
       self.ob_element_extractor = FormatFileObservationElementsExtractor()
       self.errors = []
       self.obs_line = obs_line
       self.line_number = line_number

       self.check_for_errors()
    
    def check_for_errors(self):
        """Returns a list of errors associated to the obs line"""
        if self.line_length_good():
            self.hz_angle()
            self.za_angle()
            self.slope_distance()
            self.target_height()
            self.prism_constant()
            self.atr_status()
            self.face_status()
            self.date_time()
            self.inclin_long()
            self.inclin_trav()
            self.scale_factor()
            self.geometric_ppm()
            self.atmospheric_ppm()
    
    def line_length_good(self):
        """Checks the format line is correct length"""
        if len(self.obs_line) != FormatFileObLineBuilder.LINE_LENGTH:
            self.errors.append(errors.FormatObservationLineLengthError(self.line_number))
            return False 
        return True

    def hz_angle(self):
        hz_angle_str = self.ob_element_extractor.extract_horizontal_angle(self.obs_line)
        self.hz_angle = self.convert_decimal(hz_angle_str)
        if self.hz_angle is None:
            self.errors.append(errors.FormatHZAngleError(self.line_number))

    def za_angle(self):
        za_angle_str = self.ob_element_extractor.extract_zenith_angle(self.obs_line)
        self.za_angle = self.convert_decimal(za_angle_str)
        if self.za_angle is None:
            self.errors.append(errors.FormatZAAngleError(self.line_number))

    def slope_distance(self):
        sd_str = self.ob_element_extractor.extract_slope_distance(self.obs_line)
        self.sd = self.convert_decimal(sd_str)
        if self.sd is None:
            self.errors.append(errors.FormatSlopeDistanceError(self.line_number))
        
    def target_height(self):
        th_str = self.ob_element_extractor.extract_target_height(self.obs_line)
        self.th = self.convert_decimal(th_str)
        if self.th is None:
            self.errors.append(errors.FormatTargetHeightError(self.line_number))

    def prism_constant(self):
        pc_str = self.ob_element_extractor.extract_prism_constant(self.obs_line)
        self.pc = self.convert_decimal(pc_str)
        if self.pc is None:
            self.errors.append(errors.FormatPrismConstantError(self.line_number))

    def atr_status(self):
        atr_status_str = self.ob_element_extractor.extract_atr_on(self.obs_line)
        if atr_status_str not in ('On', 'Off'):
            self.errors.append(errors.FormatAtrStatusError(self.line_number))
            self.atr_on = None 
        else:
            self.atr_on = atr_status_str == 'On'
    
    def face_status(self):
        face_str = self.ob_element_extractor.extract_face(self.obs_line)
        if face_str not in ('1', '2', '3'):
            self.errors.append(errors.FormatFaceError(self.line_number))
            self.face = None 
        else:
            self.face = face_str 
        
    def date_time(self):
        date_time_str = self.ob_element_extractor.extract_date_time(self.obs_line)
        self.date_time = self.convert_date_time_format(date_time_str)
        if self.date_time is None:
            self.errors.append(errors.FormatDateTimeError(self.line_number))

    def inclin_long(self):
        inclin_long_str = self.ob_element_extractor.extract_inclin_long(self.obs_line)
        self.inclin_long = self.convert_decimal(inclin_long_str)
        if self.inclin_long is None:
            self.errors.append(errors.FormatInclinLongError(self.line_number))

    def inclin_trav(self):
        inclin_trav_str = self.ob_element_extractor.extract_inclin_trav(self.obs_line)
        self.inclin_trav = self.convert_decimal(inclin_trav_str)
        if self.inclin_trav is None:
            self.errors.append(errors.FormatInclinTravError(self.line_number))
    
    def scale_factor(self):
        scale_factor_str = self.ob_element_extractor.extract_scale_factor(self.obs_line)
        self.scale_factor = self.convert_decimal(scale_factor_str)
        if self.scale_factor is None:
            self.errors.append(errors.FormatScaleFactorError(self.line_number))
    
    def geometric_ppm(self):
        geo_ppm_str = self.ob_element_extractor.extract_geometric_ppm(self.obs_line)
        self.geo_ppm = self.convert_decimal(geo_ppm_str)
        if self.geo_ppm is None:
            self.errors.append(errors.FormatGeometricPPMError(self.line_number))

    def atmospheric_ppm(self):
        atmos_ppm_str = self.ob_element_extractor.extract_atmospheric_ppm(self.obs_line)
        self.atmos_ppm = self.convert_decimal(atmos_ppm_str)
        if self.atmos_ppm is None:
            self.errors.append(errors.FormatAtmosphericPPMError(self.line_number))
        
    def add_no_setup_error(self):
        """Adds a no setup error to the list of errors as 
        can't assign observation to a setup"""
        self.errors.append(errors.FormatNoSetupForObservationError(
            self.line_number
        ))
    
    def __str__(self):
        return 'Observation Builder'
       

class FormatFileGonObLineBuilder(FormatFileObLineBuilder):
    CODE = 'GONS'
    def build(self):
            if not self.errors:
                return GonObservation(
                    self.ob_element_extractor.extract_target_name(self.obs_line),
                    self.hz_angle,
                    self.za_angle,
                    self.sd, 
                    self.th,
                    self.pc,
                    self.atr_on,
                    self.face, 
                    self.date_time,
                    self.inclin_long,
                    self.inclin_trav,
                    self.scale_factor,
                    self.geo_ppm,
                    self.atmos_ppm,
                    self.ob_element_extractor.extract_code(self.obs_line)
                )

class FormatFileDecimalObLineBuilder(FormatFileObLineBuilder):
    CODE = 'DMS'
    def build(self):
            if not self.errors:
                return DecimalObservation(
                    self.ob_element_extractor.extract_target_name(self.obs_line),
                    self.hz_angle,
                    self.za_angle,
                    self.sd, 
                    self.th,
                    self.pc,
                    self.atr_on,
                    self.face, 
                    self.date_time,
                    self.inclin_long,
                    self.inclin_trav,
                    self.scale_factor,
                    self.geo_ppm,
                    self.atmos_ppm,
                    self.ob_element_extractor.extract_code(self.obs_line)
                )


class StarnetSetupBuilder:
    """Class is used to create StarnetSetups""" 
    def __init__(self, setup_reducer, setup):
        self.setup_reducer = setup_reducer 
        self.setup = setup 

    def create_starnet_setup(self, backsight_id, hz_angle=0):
        """creates a Starnet Setup and StarnetMeasurements based 
        on the setup and the backsight_id passed in"""
        return StarnetSetup(
            self.setup.name, 
            self.setup.date_time, 
            self.setup.atmospheric_ppm,
            self.setup.scale_factor, 
            [self.create_starnet_measurement(reduced_ob, backsight_id) 
                for reduced_ob in self.setup_reducer.create_reduced_observations(
                self.setup, backsight_id, hz_angle
            )]
        )
     
    def create_starnet_measurement(self, reduced_ob, backsight_id):
        """creates a StarnetMeasurement"""
        return StarnetMeasurement(
            self.setup.name,
            backsight_id, 
            reduced_ob.target_name, 
            reduced_ob.hz_angle,
            reduced_ob.za_angle,
            reduced_ob.slope_distance,
            reduced_ob.horizontal_distance,
            self.setup.instrument_height,
            reduced_ob.target_height
        )


class StarnetWritterBuilder:
    @classmethod
    def starnet_2D_writter(cls, settings):
        if settings.export_settings.setup_scale_factor:
            setup_writter = SetupWritterScale
        else:
            setup_writter = SetupWritterNoScale
        return StarnetWritter(
            setup_writter,
            MeasurementWritterBuilder.build_2D_writter(settings),
            CommentWritterBuilder.build_writter(settings.export_settings.comments)
        )
        
    @classmethod 
    def starnet_3D_writter(cls, settings):
        if settings.export_settings.setup_scale_factor:
            setup_writter = SetupWritterScale
        else:
            setup_writter = SetupWritterNoScale
        
        return StarnetWritter(
            setup_writter,
            MeasurementWritterBuilder.build_3D_writter(settings),
             CommentWritterBuilder.build_writter(settings.export_settings.comments)
        )


class MeasurementWritterBuilder:
    STATION_WRITTERS = (AtFromToStationWritter, FromAtToStationWritter)
    ANGLE_WRITTERS = (GonAngleMeasurementWritter, DegMinSecAngleMeasurementWritter)
    DISTANCE_WRITTERS = (MetricDistanceMeasurementWritter, ImpericalDistanceMeasurementWritter)
    MEASUREMENTWRITTERS3D = (SDV3DMeasurementWritter, HDE3DMEasurementWritter)
    MEASUREMENTWRITTERS2D = (SDV2DMeasurementWritter, )
   
    @classmethod
    def build_2D_writter(cls, settings):
        """Builds a 2D measurement writter based on export_settings 
        passed in"""
        # always return a SDV2D measurement writter
        return SDV2DMeasurementWritter(
            cls.station_format_writter(
            settings.export_settings.station_order),
            cls.angle_writter(
            settings.export_settings.angular_unit),
            cls.distance_writter(settings.export_settings.linear_unit),
            settings)
        
    @classmethod
    def build_3D_writter(cls, settings):
        """Builds a 3D measurement writter based on export_settings 
        passed in"""
        for Writter in cls.MEASUREMENTWRITTERS3D:
            if Writter.CODE == settings.export_settings.measurement_format:
                return Writter(
                    cls.station_format_writter(
                    settings.export_settings.station_order),
                    cls.angle_writter(
                    settings.export_settings.angular_unit),
                    cls.distance_writter(settings.export_settings.linear_unit),
                    settings
                )
        
    @classmethod
    def station_format_writter(cls, station_order):
        for Writter in cls.STATION_WRITTERS:
            if Writter.CODE == station_order:
                return Writter

    @classmethod
    def angle_writter(cls, angle_format):
        for Writter in cls.ANGLE_WRITTERS:
            if Writter.CODE == angle_format:
                return Writter

    @classmethod
    def distance_writter(cls, distance_format):
        for Writter in cls.DISTANCE_WRITTERS:
            if Writter.CODE == distance_format:
                return Writter


class CommentWritterBuilder:
    @classmethod 
    def build_writter(self, comment_settings):
        """Builds and returns a comment writter based on
        comment settings passed in"""
        writters = []
        if comment_settings.apply_comments:
            
            if comment_settings.date_time:
                writters.append(DateTimeWritter)
            
            if comment_settings.atmospheric_ppm:
                writters.append(AtmosPPMWritter)
                
            if comment_settings.scale_factor:
                writters.append(ScaleFactorWritter)
                
        return CommentWritter(writters)
