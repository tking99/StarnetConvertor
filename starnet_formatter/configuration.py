from decimal import Decimal

class Settings:
    ALLOWED_TOLERANCE = (0.00000, 1.0)
    ALLOWED_ANGULAR_UNIT = ('GONS', 'DMS')

    def __init__(self):
        # Assign Default Values within the settings
        self._distance_tolerance = 0.0017
        self._hz_angle_tolerance = 0.0010
        self._za_angle_tolerance = 0.0010
        self._angular_unit = Settings.ALLOWED_ANGULAR_UNIT[1]
        self._linear_precision = 4 # decimal places
        self._angular_precision = 5 # decimal places
        self.apply_scale_factor = False
        self.capature_side_shots = True
        self.side_shot_prefix = 'SS'
        # create a export settings object
        self.export_settings = ExportSettings()
    @property 
    def angular_unit(self):
        return self._angular_unit

    @angular_unit.setter 
    def angular_unit(self, unit):
        if unit in self.ALLOWED_ANGULAR_UNIT:
            self._angular_unit = unit

    @property
    def distance_tolerance(self):
        return self._distance_tolerance 

    @distance_tolerance.setter
    def distance_tolerance(self, tolerance):
        if self.check_distance_tolerance(tolerance):
            self._distance_tolerance = Decimal(tolerance)

    @property 
    def hz_angle_tolerance(self):
        return self._hz_angle_tolerance 

    @hz_angle_tolerance.setter 
    def hz_angle_tolerance(self, tolerance):
        if self.check_distance_tolerance(tolerance):
            self._hz_angle_tolerance = Decimal(tolerance)

    @property
    def za_angle_tolerance(self):
        return self._za_angle_tolerance
    
    @za_angle_tolerance.setter
    def za_angle_tolerance(self, tolerance):
        if self.check_distance_tolerance(tolerance):
            self._za_angle_tolerance = Decimal(tolerance)

    def check_distance_tolerance(self, tolerance):
        """Checks if the passed in tolerance is allowed"""
        try:
            tol = float(tolerance)
            if tol >= Settings.ALLOWED_TOLERANCE[0] and \
             tol <= Settings.ALLOWED_TOLERANCE[1]:
                return True
            return False

        except ValueError:
            return False  

    @property 
    def linear_precision(self):
        return self._linear_precision

    @linear_precision.setter 
    def linear_precision(self, unit):
        if unit >=0 and unit <= 10:
            self._linear_precision = unit 

    @property 
    def angular_precision(self):
        return self._angular_precision

    @angular_precision.setter 
    def angular_precision(self, unit):
        if unit >=0  and unit <= 10:
            self._angular_precision = unit 

    def apply_scale_factor_toggle(self):
        self.apply_scale_factor = not self.apply_scale_factor

    def apply_capature_side_shots_toggle(self):
        self.capature_side_shots = not self.capature_side_shots
    

class ExportSettings:
    ALLOWED_STATION_ORDER = ('AT-FROM-TO', 'FROM-AT-TO')
    ALLOWED_MEASUREMENT_FORMAT = ('SD/V', 'HD/E')
    ALLOWED_LINEAR_UNITS = ('METERS',)
    ALLOWED_ANGULAR_UNIT = ('GONS', 'DMS')
    ALLOWD_EXPORT_FILES = ('')
    ALLOWED_SIDE_SHOT_PROCESSING_CODE = ('M', 'SS')

    def __init__(self):
        #Setting Default Values 
        self._station_order = self.ALLOWED_STATION_ORDER[0]
        self._angular_unit = self.ALLOWED_ANGULAR_UNIT[1]
        self._measurement_format = self.ALLOWED_MEASUREMENT_FORMAT[0]
        self._linear_unit = self.ALLOWED_LINEAR_UNITS[0]
        self.export2d = False 
        self.export3d = False
        self.export_spigot = True
        self.setup_scale_factor = False 
        self.remove_side_shots = False
        self._side_shot_processing_code = self.ALLOWED_SIDE_SHOT_PROCESSING_CODE[0]
        self.comments = CommentSettings()
        self.file_2D_path = None
        self.file_3D_path = None
      

    @property
    def side_shot_processing_code(self):
        return self._side_shot_processing_code

    @side_shot_processing_code.setter
    def side_shot_processing_code(self, code):
        if code in self.ALLOWED_SIDE_SHOT_PROCESSING_CODE:
            self._side_shot_processing_code = code  

    @property 
    def station_order(self):
        return self._station_order 

    @station_order.setter 
    def station_order(self, station_order):
        if station_order in self.ALLOWED_STATION_ORDER:
            self._station_order = station_order 

    @property 
    def angular_unit(self):
        return self._angular_unit

    @angular_unit.setter 
    def angular_unit(self, unit):
        if unit in self.ALLOWED_ANGULAR_UNIT:
            self._angular_unit = unit
    
    @property 
    def linear_unit(self):
        return self._linear_unit

    @linear_unit.setter 
    def linear_unit(self, unit):
        if unit in self.ALLOWED_LINEAR_UNITS:
            self._linear_unit = unit

    @property 
    def measurement_format(self):
        return self._measurement_format

    @measurement_format.setter 
    def measurement_format(self, meas_format):
        if meas_format in self.ALLOWED_MEASUREMENT_FORMAT:
            self._measurement_format = meas_format
            
    def apply_export_2d_toggle(self):
        self.export2d = not self.export2d

    def apply_export_3d_toggle(self):
        self.export3d = not self.export3d

    def apply_comments_toggle(self):
        self.apply_comments = not self.apply_comments

    def apply_setup_scale_factor_toggle(self):
        self.setup_scale_factor = not self.setup_scale_factor

    def apply_remove_side_shots_toggle(self):
       self.remove_side_shots = not self.remove_side_shots


class CommentSettings:
    def __init__(self):
        # Setting default comment settings
        self.apply_comments = True
        self.atmospheric_ppm = True
        self.scale_factor = False
        self.date_time = True 
        self.code = False 

    def turn_off_all(self):
        """turns all the attribute bools off"""
        self._turn_all(False) 

    def turn_on_all(self):
        """turns all the attributes bools on"""
        self._turn_all(True)

    def _turn_all(self, status):
        """turns on/off the attribute bools based 
        on the bool passed in"""
        self.atmospheric_ppm = status 
        self.scale_factor = status 
        self.date_time = status
        self.code = status

    def apply_comments_toggle(self):
        self.apply_comments = not self.apply_comments
    
    def atmospheric_ppm_toggle(self):
        self.atmospheric_ppm = not self.atmospheric_ppm

    def scale_factor_toggle(self):
        self.scale_factor = not self.scale_factor 

    def date_time_toggle(self):
        self.date_time = not self.date_time
    
    def code_toggle(self):
        self.code = not self.code 

        






            


      