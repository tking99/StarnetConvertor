from math import cos, sin, radians
from decimal import Decimal
from decimal import InvalidOperation

class Job:
    def __init__(self, surveyor=None):
        self.surveyor = surveyor
        
        
class Observation:
    def __init__(self, target_name, hz_angle, za_angle, 
        sd, th, pc, atr, face, date_time, inclin_long, inclin_trav,
        sf, geometric_ppm, atmos_ppm, code):
        self.target_name = target_name
        self.hz_angle = hz_angle
        self.za_angle = za_angle
        self.slope_distance = sd 
        self.target_height = th
        self.prism_constant = pc 
        self.atr_on = atr 
        self.face = face 
        self.date_time = date_time
        self.inclin_long = inclin_long 
        self.inclin_trav = inclin_trav
        self.scale_factor = sf 
        self.geometric_ppm = geometric_ppm
        self.atmos_ppm = atmos_ppm
        self.code = code 
        self.hz_angle_on = True
        self.za_angle_on = True 
        self.slope_distance_on = True 

    def hz_angle_on_toggle(self):
        self.hz_angle_on = not self.hz_angle_on
    
    def za_angle_on_toggle(self):
        self.za_angle_on = not self.za_angle_on

    def slope_distance_on_toggle(self):
        self.slope_distance_on = not self.slope_distance_on

    def atr_status(self):
        if self.atr_on:
            return 'ON'
        return 'OFF'

    def instrument_level(self):
        return True 
      
    def __str__(self):
        return self.target_name 
    
    def __repr__(self):
        return self.target_name


class GonObservation(Observation):
    @property
    def vertical_elevation(self):
        """returns the vertical elevation"""
        za_degrees = self.za_angle * Decimal(0.9000000000000)
        x = abs(Decimal(self.slope_distance) * Decimal(cos(radians(za_degrees))))
        y = abs(Decimal(self.slope_distance) * Decimal(sin(radians(za_degrees))))
        earth_cur = 6378000
        return x + Decimal(1/(2*earth_cur)) * (y**2)
       
    @property
    def no_scale_hor_dist(self):
        """returns the calculated hor 
        dist based on the sd and za and earth curv, excludes 
        scale factor"""
        za_degrees = self.za_angle * Decimal(0.9000000000000)
        y = abs(Decimal(self.slope_distance) * Decimal(sin(radians(za_degrees))))
        earth_cur = 6378000
        return y - Decimal((1/earth_cur)) * self.vertical_elevation * y
    
    @property
    def scale_hor_dist(self):
        """returns the calculated for dist
        based on the sd and za and passed in scale factor"""
        return self.no_scale_hor_dist * self.scale_factor


class DecimalObservation(GonObservation):
    pass 


class MeanObservation:
    def __init__(self, hz_angle, za_angle, sd, hd):
        self.hz_angle = hz_angle 
        self.za_angle = za_angle 
        self.slope_distance = sd 
        self.hor_distance = hd


class GonMeanObservation(MeanObservation):
    @property 
    def vertical_elevation(self):
        za_degrees = self.za_angle * Decimal(0.900000000000001)
        return abs(Decimal(self.slope_distance) * Decimal(cos(radians(za_degrees))))


class DecimalMeanObservation(MeanObservation):
    @property
    def vertical_elevation(self):
        """returns the vertical elevation"""
        return abs(Decimal(self.slope_distance) * Decimal(cos(radians(za_degrees))))


class Setup:
    def __init__(self, name, instrument_height, date_time, 
        atmos_ppm, sf):
        self.name = name
        self.instrument_height = instrument_height
        self.date_time = date_time
        self._atmospheric_ppm = atmos_ppm 
        self._scale_factor = sf
        self.target_observations = {}
        self.side_shot_observations = {}
        self._reduce_to = None
        self.instrument_type = None
   
    @property
    def atmospheric_ppm(self):
        return self._atmospheric_ppm
    
    @atmospheric_ppm.setter
    def atmospheric_ppm(self, atmos_ppm):
        """Updates all the observations with the lastest 
        atmos ppm"""
        try:
            old_ppm = self._atmospheric_ppm
            self._atmospheric_ppm = Decimal(atmos_ppm)
            self._modify_atmospheric(self.target_observations, old_ppm,
                self._atmospheric_ppm)
            self._modify_atmospheric(self.side_shot_observations, old_ppm,
                self._atmospheric_ppm)
        except InvalidOperation:
            pass 

    def _modify_atmospheric(self, target_obs, old_ppm, new_ppm):
        """modifys the distances of the observations to refelct the new 
        atmospheric values"""
        for target_ob in target_obs.values():
            for ob in target_ob.observations: 
                ob.slope_distance += (ob.slope_distance * (1+(new_ppm / 1000000))) / (1+(
                    old_ppm / 1000000)) - ob.slope_distance
                                     
    @property 
    def scale_factor(self):
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, sf):
        """updates all the observations with the 
        latest scale factor"""
        try:
            self._scale_factor = Decimal(sf)
            # update all observations with the new scale factor 
            self._modify_scale(self.target_observations)
            self._modify_scale(self.side_shot_observations)

        except InvalidOperation:
            pass 

    def _modify_scale(self, target_obs):
        """modifys the scale factor for observations
        with a new setup scale factor"""
        for target_ob in target_obs.values():
            for ob in target_ob.observations:
                ob.scale_factor = self._scale_factor

    
    def remove_reduce_to(self, target):
        """Checks if the target is the reduce to target,
        if so sets it to None"""
        if target == self._reduce_to:
            self._reduce_to = None 
    
    @property 
    def reduce_to(self):
        """returns the setup reduce to target ob, 
        if None and target ob it defaults to first target ob 
        in dict"""
        if self._reduce_to is None and self.target_observations:
            self._reduce_to = self.target_observations[
                next(iter(self.target_observations))]
        return self._reduce_to


    @reduce_to.setter
    def reduce_to(self, target_ob_name):
        #check if target ob is in target_ob dictionary before setting
        if target_ob_name in self.target_observations:
            self._reduce_to = self.target_observations[target_ob_name]
       
    @property
    def total_target_observations(self):
        """returns the total numer of target 
        observations associated with the setup"""
        return sum((len(target_ob.observations) for target_ob in 
            self.target_observations.values()))

    @property 
    def total_side_shot_observations(self):
        return sum((len(side_shot.observations) for side_shot in 
            self.side_shot_observations.values()))

    def add_observation(self, observation):
        """Adds an observation to a target observation """
        target_obs = self._get_target_observations(observation, 
            self.target_observations)
        target_obs.observations.append(observation)

    def add_side_shot_observation(self, observation):
        """Adds a spigot observation to a spigot target 
        observation"""
        side_obs = self._get_target_observations(observation, 
            self.side_shot_observations)
        side_obs.observations.append(observation)

    def move_target_to_spigot(self, target_id):
        """moves a target to the side shot dictionary"""
        target = self.target_observations.get(target_id)
        if target: 
            self.side_shot_observations[target_id] = target 
            del self.target_observations[target_id]
            # remove target id to reduce to
            self.remove_reduce_to(target)
    
    def move_spigot_to_target(self, target_id):
        """moves a side shot to the target dictionary"""
        target = self.side_shot_observations.get(target_id)
        if target:
            self.target_observations[target_id] = target
            del self.side_shot_observations[target_id]

    def _get_target_observations(self, observation, target_obs_dict):
        """gets the target observation from the dictionary, 
        else creates a new target observation using the observation 
        name and target height"""
        return target_obs_dict.setdefault(
            observation.target_name, TargetObservation(
                observation.target_name, observation.target_height))

    def check_target_id_exists(self, target_id):
        """returns a boolean in the target ob exsits within the setup"""
        return target_id in self.target_observations

    def delete_target(self, target):
        """Deletes a target observation from a setup if present"""
        if target.name in self.target_observations:
            del self.target_observations[target.name]

    def delete_sideshot(self, sideshot):
        """Deleta a sideshot observation from a setup if present"""
        if sideshot.name in self.side_shot_observations:
            del self.side_shot_observations[sideshot.name]

    def __repr__(self):
        return self.name 
    
    def __str__(self):
        return self.name


class TargetObservation:
    def __init__(self, name, target_height):
        self.name = name 
        self.target_height = target_height
        self.observations = []
   
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

    @property 
    def prism_constant(self):
        """Assumes all observations have the same PC so returns the 
        PC of the first observation"""
        if self.observations:
            return self.observations[0].prism_constant


    def change_prism_constant(self, pc):
        """Changes the prism constant and updates the 
        observation distances and pc with the new constant"""
        if pc!= self.prism_constant:
            delta = self.prism_constant - pc
            for ob in self.observations:
                ob.slope_distance -= delta / 1000 # convert delta to m 
                ob.prism_constant = pc 
                   
    def mean_target_observation(self, ob_reducer, apply_scale=False):
        """Require a ob_reducer and optionally scale bool to create 
        a mean observaton"""
        return ob_reducer.create_mean_observation(
            self.observations, apply_scale
        )
    
    def reduced_mean_target_observation(self, ob_reducer, hz_delta, apply_scale=False):
        """Requires an ob_reducer and a delta hz_angle"""
        mean_observation = self.mean_target_observation(ob_reducer, apply_scale)
        mean_observation.hz_angle = ob_reducer.reduce_hz_by_angle(
            mean_observation.hz_angle, hz_delta
        )
        return mean_observation

    def delete_observation(self, ob):
        """removes and observation from the observation 
        list"""
        try:
            self.observations.remove(ob)
            return True
        except ValueError:
            return False


class StarnetSetup:
    def __init__(self, name, date_time, atmos_ppm, sf, instrument_type):
        self.name = name 
        self.date_time = date_time 
        self.atmospheric_ppm = atmos_ppm 
        self.scale_factor = sf 
        self.instrument_type = instrument_type
        self.starnet_measurements = []
        self.starnet_side_shots = []

    def starnet_measurements_all_sorted(self):
        """returns a sorted list of all measurements 
        and side shots"""
        combined_measurements = self.starnet_measurements + self.starnet_side_shots
        return sorted(combined_measurements, key=lambda measurement: measurement.hz_angle)

    def starnet_measurements_sorted(self):
        return sorted(self.starnet_measurements,
            key=lambda measurement: measurement.hz_angle)

    def starnet_side_shots_sorted(self):
        """returns a list of sorted side shots obs with the first target RO measurments"""
        l = sorted(self.starnet_side_shots, key=lambda measurement:measurement.hz_angle)
        if l:
            # add ro measurement 
            l.insert(0, self.starnet_measurements_sorted()[0])
        return l

class StarnetMeasurement:
    CODE = 'M'
    def __init__(self, station_id, backsight_id, target_id,
        hz_angle, za_angle, vertical_elevation, slope_distance, 
        horizontal_distance,  instrument_height, target_height):
        self.station_id = station_id 
        self.backsight_id = backsight_id 
        self.target_id = target_id 
        self.hz_angle = hz_angle
        self.za_angle = za_angle
        self.vertical_elevation = vertical_elevation 
        self.slope_distance = slope_distance
        self.horizontal_distance = horizontal_distance
        self.instrument_height = instrument_height 
        self.target_height = target_height

    def __len__(self):
        return len(self.station_id+self.backsight_id+self.target_id)
        

class StarnetSideShotMeasurementSS(StarnetMeasurement):
    CODE = 'SS'


class StarnetSideShotMeasurementM(StarnetMeasurement):
    CODE = 'M'


    
    


    

