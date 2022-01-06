from starnet_formatter.convertors import gons_to_dms_str

class StarnetWritter:
    def __init__(self, setup_writter, measurement_writter,
        comment_writter):
        self.setup_writter = setup_writter
        self.measurement_writter = measurement_writter
        self.comment_writter = comment_writter
        self.longest_station_name = 0

    def export(self, dat_file, starnet_setups):
        with open(dat_file, 'w') as export_file:
            # get the lonest station format length so columns can be in line
            lsf = self.len_longest_station_format(starnet_setups)
            for setup in starnet_setups:
                export_file.write(self.setup_writter.write_setup(setup) + '\n')
                export_file.write(self.comment_writter.write_comment(setup) + '\n')
                for measurement in setup.starnet_measurements_all_sorted():
                    export_file.write(self.measurement_writter.write_measurement(measurement, lsf) + '\n')


    def len_longest_station_format(self, starnet_setups):
        """returns the station format with the longest characters"""
        return max((len(max(setup.starnet_measurements_all_sorted(), key=lambda m: len(m.station_id+m.backsight_id+m.target_id))) 
            for setup in starnet_setups))
        
class SetupWritterNoScale:
    @classmethod
    def write_setup(cls, setup):
        return (f'############################################## \n'
                f'#SETUP {setup.name} \n' 
                '##############################################')
         
class SetupWritterScale:
    @classmethod
    def write_setup(cls, setup):
        return (f'\n.SCALE {setup.scale_factor} \n' 
                '############################################## \n'
                f'#SETUP {setup.name} \n'
                '##############################################')


class CommentWritter:
    def __init__(self, writters):
        self.writters = writters 

    def write_comment(self, starnet_setup):
        if self.writters:
            comment = '# '

            for Writter in self.writters:
                comment += Writter.write_comment(starnet_setup)
                if Writter is not self.writters[-1]:
                    comment += ', '
            return comment 


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






