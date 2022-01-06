import re 
from decimal import Decimal

from starnet_formatter.builders import StarnetWritterBuilder
from starnet_formatter.factories import TargetObservationReducerFactory, \
        ObservationStatReducerFactory, StarnetSideShotFactory
from starnet_formatter.surveyModels import StarnetSetup, StarnetMeasurement

class SurveyProccesor:
    def __init__(self, settings):
        # if setups passed in init, then clean them before adding
        self.setups = list() 
        self.settings = settings

        # starnert processor 
        self.starnet_processor = StarnetSetupsProcessor(
            self
        )
        # boolean to control if measurments will be scaled
        self.scale_measurements = False
        
        # get thes target observation reducer from the factory
        self.ob_reducer = TargetObservationReducerFactory.reducer(
            self.settings.angular_unit)()

        self.stat_reducer = ObservationStatReducerFactory.reducer(
            self.settings.angular_unit
        )(self.ob_reducer, self.settings)

        self.mean_target_obs = dict()

    def has_setups(self):
        """Returns a boolean if the survey processor has setups"""
        return len(self.setups) > 0
    
    def reset(self):
        """resets the survey processor by removes all the setups"""
        self.setups.clear()

    def add_setups(self, setups):
        """appends cleaned setups to the 
        list of setups"""
        self.setups = [*self.setups, *setups]
       
    def _clean_setups(self, setups):
        """removes setups without any observations"""
        return [setup for setup in setups if setup.target_observations]
    
    def delete_setup(self, delete_setup):
        """Deletes a setup from the list of setups"""
        self.setups = [setup for setup in self.setups if setup != delete_setup]
    
    def total_imported_observations(self):
        """returns the number of imported 
        observations"""
        return sum((setup.total_observations for 
            setup in self.setups))

    def update_setup_reduce_to(self, setup, target):
        """sets the setup reduce to target object"""
        setup.reduce_to = target.name 
      
    def update_setup(self, setup, setup_name, instrument_height, 
        atmos_ppm, scale_factor):
        """Updates a setup with values from Setup Edit
        frame. Converts to Deciaml before storing"""

        setup.name = setup_name 
        setup.instrument_height = Decimal(instrument_height)
        setup.atmospheric_ppm = atmos_ppm
        setup.scale_factor = scale_factor

    def update_target(self, target, target_name, target_height,
        target_pc):
        """Updates a target with the latest values"""
        target.name = target_name 
        target.target_height = Decimal(target_height)
        target.change_prism_constant(Decimal(target_pc))

    def _create_starnet_setups(self):
        return self.starnet_processor.create_starnet_setups()

    def create_dat_files(self):
        """Creates a 2D ad 3D dat files for the export, returns a 
        succcess tuple if successfully exported"""
        # create starnet setups
        result_2D = False 
        starnet_setups = self._create_starnet_setups()
        # create 2D dat file
        if self.settings.export_settings.file_2D_path and \
            self.settings.export_settings.export2d:
            starnet_2D_writter = StarnetWritterBuilder.starnet_2D_writter(
            self.settings)
            starnet_2D_writter.export(self.settings.export_settings.file_2D_path,
                starnet_setups)
            result_2D = True 
        
        result_3D = False
        # create 3D dat file
        if self.settings.export_settings.file_3D_path and \
            self.settings.export_settings.export3d:
            starnet_3D_writter = StarnetWritterBuilder.starnet_3D_writter(
            self.settings)
            starnet_3D_writter.export(self.settings.export_settings.file_3D_path,
                starnet_setups)
            result_3D = True 
        return (result_2D, result_3D)


class StarnetSetupsProcessor:
    def __init__(self, survey_processor):
        self.survey_processor = survey_processor

    def reset_starnet_setups(self):
        self.starnet_setups = list()

    def create_starnet_setups(self):
        self.reset_starnet_setups()
        for setup in self.survey_processor.setups:
            self.create_starnet_setup(setup)
        return self.starnet_setups
    
    def create_starnet_setup(self, setup, set_to_zero=0):
        # create starnet setup
        starnet_setup = StarnetSetup(
            setup.name, 
            setup.date_time,
            setup.atmospheric_ppm,
            setup.scale_factor,
        )
        # calculate delta 
        if setup.target_observations:
            mean_reduce_to_ob = setup.reduce_to.mean_target_observation(
                self.survey_processor.ob_reducer, self.survey_processor.scale_measurements 
            )
            
            delta_angle = mean_reduce_to_ob.hz_angle - set_to_zero

            # create starnet measurements
            self.create_starnet_measurements(setup, starnet_setup, delta_angle)
            
            # create starnet side shots if not removed from export settings
            if not self.survey_processor.settings.export_settings.remove_side_shots:
                self.create_side_shot_measurements(setup, starnet_setup, delta_angle)

        # add to starnet setups 
        self.starnet_setups.append(starnet_setup)

    def create_starnet_measurements(self, setup, starnet_setup, delta_angle):
        """Creates starnet measurements and adds to the 
        starnet setup measurement list"""
        for target in setup.target_observations.values():
            mean_reduced_ob = target.reduced_mean_target_observation(
                self.survey_processor.ob_reducer, delta_angle, 
                self.survey_processor.settings.apply_scale_factor
            )
            starnet_setup.starnet_measurements.append(self.create_starnet_measurement(
                setup, target, mean_reduced_ob))

    def create_side_shot_measurements(self, setup, starnet_setup, delta_angle):
        """Creates the starnet side shots and adds to the 
        starnet setup side shots list"""
        for side_shot in setup.side_shot_observations.values():
            mean_reduced_ob = side_shot.reduced_mean_target_observation(
                self.survey_processor.ob_reducer, delta_angle, 
                self.survey_processor.settings.apply_scale_factor
            )
            starnet_setup.starnet_side_shots.append(self.create_side_shot_measurement(
                setup, side_shot, mean_reduced_ob))
        
    def create_starnet_measurement(self, setup, target, mean_reduced_ob):
        return StarnetMeasurement(
            setup.name,
                setup.reduce_to.name,
                target.name,
                round(mean_reduced_ob.hz_angle, self.survey_processor.settings.angular_precision),
                round(mean_reduced_ob.za_angle, self.survey_processor.settings.angular_precision),
                round(mean_reduced_ob.vertical_elevation, self.survey_processor.settings.linear_precision),
                round(mean_reduced_ob.slope_distance, self.survey_processor.settings.linear_precision),
                round(mean_reduced_ob.hor_distance, self.survey_processor.settings.linear_precision),
                round(setup.instrument_height, 3),
                round(target.target_height, 3))
    
    def create_side_shot_measurement(self, setup, target, mean_reduced_ob):
        SideShot = StarnetSideShotFactory.side_shot_measurement_class(
            self.survey_processor.settings.export_settings.side_shot_processing_code)
        return SideShot(
            setup.name,
            setup.reduce_to.name,
            target.name,
            round(mean_reduced_ob.hz_angle, self.survey_processor.settings.angular_precision),
            round(mean_reduced_ob.za_angle, self.survey_processor.settings.angular_precision),
            round(mean_reduced_ob.vertical_elevation, self.survey_processor.settings.linear_precision),
            round(mean_reduced_ob.slope_distance, self.survey_processor.settings.linear_precision),
            round(mean_reduced_ob.hor_distance, self.survey_processor.settings.linear_precision),
            round(setup.instrument_height, 3),
            round(target.target_height, 3))



        
    
