from starnet_formatter.convertors import gons_to_dms_str


class StarnetWritter:
    def __init__(self, setup_writter, measurement_writter,
        comment_writter, inline_writter, export_settings):
        self.setup_writter = setup_writter
        self.measurement_writter = measurement_writter
        self.comment_writter = comment_writter
        self.inline_writter = inline_writter
        self.export_settings = export_settings
        self.longest_station_name = 0

    def export(self, dat_file, starnet_setups):
        with open(dat_file, 'w') as export_file:
            # get the lonest station format length so columns can be in line
            lsf = self.len_longest_station_format(starnet_setups)
            for setup in starnet_setups:
                obs = self._get_observations(setup) 
                if obs:
                    export_file.write(self.setup_writter.write_setup(setup) + '\n')
                    export_file.write(self.comment_writter.write_comment(setup, self.export_settings.comments.surveyor) + '\n')
                    export_file.write(self.inline_writter.write_inline(setup))

                    for measurement in obs:
                        export_file.write(self.measurement_writter.write_measurement(measurement, lsf) + '\n')

    def _get_observations(self, setup):
        """returns a list of observations"""
        # target ob and side shots
        obs = []
        if self.export_settings.process_target_obs and self.export_settings.process_side_shot_obs:
                    return setup.starnet_measurements_all_sorted()
        
        # target ob not side shots
        elif self.export_settings.process_target_obs and not self.export_settings.process_side_shot_obs:
                    return setup.starnet_measurements_sorted()

        # side shots and not target obs
        elif not self.export_settings.process_target_obs and self.export_settings.process_side_shot_obs:
                    return setup.starnet_side_shots_sorted()
        return obs
    
    def len_longest_station_format(self, starnet_setups):
        """returns the station format with the longest characters"""
        return max((len(max(setup.starnet_measurements_all_sorted(), key=lambda m: len(m.station_id+m.backsight_id+m.target_id))) 
            for setup in starnet_setups))


class StarnetWritterCombiner(StarnetWritter):
    """Combines the measurements to an existing star*net file"""
    SETUP_ID = '#SETUP'
    def __init__(self, setup_writter, measurement_writter,
        comment_writter, inline_writter, export_settings):
        super().__init__(setup_writter, measurement_writter, 
        comment_writter, inline_writter, export_settings)
        setup_line_numbers = []

    def export(self, dat_file, starnet_setups):
        self.lsf = self.len_longest_station_format(starnet_setups)
        for num, setup in enumerate(starnet_setups):
            self._export(dat_file, setup)
        
    def _export(self, dat_file, setup):
        with open(dat_file, 'r') as f:
            lines = f.readlines()
            sln= self.extract_setup_line_number(lines, setup.name)
            obs = self._get_observations(setup)
            if obs: 
                if sln:
                    lines.insert(sln+2, self.comment_writter.write_comment(setup, self.export_settings.comments.surveyor) + '\n')
                    lines.insert(sln+3, self.inline_writter.write_inline(setup))
                    for num, measurement in enumerate(obs):
                        lines.insert(sln+num+4, self.measurement_writter.write_measurement(measurement, self.lsf) + '\n')
                    lines.insert(sln+num+5, '\n')
                else:
                    lines.append(self.setup_writter.write_setup(setup) + '\n')
                    lines.append(self.comment_writter.write_comment(setup, self.export_settings.comments.surveyor) + '\n')
                    lines.append(self.inline_writter.write_inline(setup))
                    for measurement in obs:
                        lines.append(self.measurement_writter.write_measurement(measurement, self.lsf) + '\n')
                    lines.append('\n')
        
        with open(dat_file, 'w') as f:
            lines = "".join(lines)
            f.write(lines)
                   
    def extract_setup_line_number(self, lines, setup_id):
        """returns the line number were the setup is within the file
            else returns None"""
        for num, line in enumerate(lines):
            if f'{self.SETUP_ID} {setup_id}' in line:
                return num 


class SetupWritter:
    @classmethod
    def write_setup(cls, setup):
        return (f'############################################## \n'
                f'#SETUP {setup.name} \n' 
                '##############################################')


class InlineWritter:
    def __init__(self, writters):
        self.writters = writters 

    def write_inline(self, setup):
        inline = ''
        if self.writters:
            
            for Writter in self.writters:
                inline += Writter.write_comment(setup)
                inline += '\n'
        return inline
      

class ScaleFactorInline:
    @classmethod 
    def write_comment(cls, setup):
        return f'.SCALE {setup.scale_factor}'


class InstrumentInline:
    @classmethod 
    def write_comment(cls, setup):
        return f'.inst {setup.instrument_type}'


class CommentWritter:
    def __init__(self, writters):
        self.writters = writters 

    def write_comment(self, starnet_setup, surveyor):
        if self.writters:
            comment = '# '
            for Writter in self.writters:
                comment += Writter.write_comment(starnet_setup)
                if Writter is not self.writters[-1]:
                    comment += ', '
            comment += f', Surveyor: {surveyor}'
            return comment 


class SurveyorWritter:
    @classmethod
    def write_surveyor(cls, surveyor):
        return f' Survey: {surveyor}'


class AtmosPPMWritter:
    @classmethod
    def write_comment(cls, setup):
        return f'Atmos PPM: {setup.atmospheric_ppm}'


class ScaleFactorWritter:
    @classmethod
    def write_comment(cls, setup):
       return f'SF: {setup.scale_factor}'


class DateTimeWritter:
    @classmethod
    def write_comment(cls, setup):
        return f'Date Time: {setup.date_time}'
        

class MeasurementWritter:
    """Abstract class"""
    def __init__(self, station_writter, angle_writter,
        distance_writter, settings):
        self.station_writter = station_writter
        self.angle_writter = angle_writter
        self.distance_writter = distance_writter
        self.settings = settings

    def write_measurement(self, measurement, lsf):
        pass

    
class SDV2DMeasurementWritter(MeasurementWritter):
    CODE = 'SD/V'
    def write_measurement(self, measurement, lsf):
        spaces = ' ' * (lsf - len(measurement.station_id+measurement.backsight_id+measurement.target_id)) 
        if self.settings.export_settings.angular_unit == 'GONS':
            return f'{measurement.CODE} \
            {self.station_writter.station_format(measurement.station_id,measurement.backsight_id, measurement.target_id)}\
            {spaces}\t{self.angle_writter.angle(measurement.hz_angle):.{self.settings.angular_precision}f}\t\
            {self.distance_writter.distance(measurement.horizontal_distance)}\t'
        
        elif self.settings.export_settings.angular_unit == 'DMS':
            return f'{measurement.CODE} \
            {self.station_writter.station_format(measurement.station_id,measurement.backsight_id, measurement.target_id)}\
            {spaces}\t{self.angle_writter.angle(measurement.hz_angle)}\t\
            {self.distance_writter.distance(measurement.horizontal_distance)}\t'
    
   
class SDV3DMeasurementWritter(MeasurementWritter):
    CODE = 'SD/V'
    def write_measurement(self, measurement, lsf):
        spaces = ' ' * (lsf - len(measurement.station_id+measurement.backsight_id+measurement.target_id)) 
        if self.settings.export_settings.angular_unit == 'GONS':
            return f'{measurement.CODE} \
            {self.station_writter.station_format(measurement.station_id,measurement.backsight_id, measurement.target_id)} \
            {spaces}\t{self.angle_writter.angle(measurement.hz_angle):.{self.settings.angular_precision}f}\t\
                {self.distance_writter.distance(measurement.slope_distance)}\t\
                {self.angle_writter.angle(measurement.za_angle):.{self.settings.angular_precision}f}\t\
                {measurement.instrument_height}/{measurement.target_height}\t'
        
        elif self.settings.export_settings.angular_unit == 'DMS':
            return f'{measurement.CODE} \
            {self.station_writter.station_format(measurement.station_id,measurement.backsight_id, measurement.target_id)} \
            {spaces}\t{self.angle_writter.angle(measurement.hz_angle)}\t\
                {self.distance_writter.distance(measurement.slope_distance)}\t\
                {self.angle_writter.angle(measurement.za_angle)}\t\
                {measurement.instrument_height}/{measurement.target_height}\t'


class HDE3DMEasurementWritter(MeasurementWritter):
    CODE = 'HD/E'
    def write_measurement(self, measurement, spacing):
        spaces = ' ' * (lsf - len(measurement.station_id+measurement.backsight_id+measurement.target_id))
        if self.settings.export_settings.angular_unit == 'GONS':
            return f'{measurement.CODE} \
            {self.station_writter.station_format(measurement.station_id,measurement.backsight_id, measurement.target_id)} \
            {spaces}\t{self.angle_writter.angle(measurement.hz_angle):.{self.settings.angular_precision}f}\t\
                {self.angle_writter.angle(measurement.horizontal_distance)}\t\
                {measurement.vertical_elevation}\t\
                {measurement.instrument_height}/{measurement.target_height}\t'
       
        elif self.settings.export_settings.angular_unit == 'DMS':
            return f'{measurement.CODE} \
            {self.station_writter.station_format(measurement.station_id,measurement.backsight_id, measurement.target_id)} \
            {spaces}\t{self.angle_writter.angle(measurement.hz_angle)}\t\
                {self.angle_writter.angle(measurement.horizontal_distance)}\t\
                {measurement.vertical_elevation}\t\
                {measurement.instrument_height}/{measurement.target_height}\t'

        

class AtFromToStationWritter:
    CODE = 'AT-FROM-TO'
    @classmethod
    def station_format(cls, at_stn, from_stn, to_stn):
        return f'{at_stn}-{from_stn}-{to_stn}'


class FromAtToStationWritter:
    CODE = 'FROM-AT-TO'
    @classmethod
    def station_format(cls, at_stn, from_stn, to_stn):
        return f'{from_stn}-{at_stn}-{to_stn}'


class GonAngleMeasurementWritter:
    CODE = 'GONS'
    @classmethod
    def angle(cls, angle):
        return angle


class DegMinSecAngleMeasurementWritter:
    CODE = 'DMS'
    @classmethod
    def angle(cls, angle):
        return gons_to_dms_str(angle)


class MetricDistanceMeasurementWritter:
    CODE = 'METERS'
    @classmethod 
    def distance(cls, distance):
        return distance

class ImpericalDistanceMeasurementWritter:
    CODE = 'FEETUS'
    @classmethod 
    def distance(cls, distance):
        pass 






