class ErrorDistance:
    @classmethod
    def display_error(cls):
        return "Distance is out of tolerance between faces"

class ErrorHorizontalAngle:
    @classmethod
    def display_error(cls):
        return "Horizontal angle is out of tolerance between faces"

class ErrorZenithAngle:
    @classmethod 
    def display_error(cls):
        return "Zenith angle is out of tolerance between faces"


class DecimalReducedObservationChecker:
    """Checks if a reduced decimal observation is within tolerance"""
    def __init__(self, fl_observation, fr_observation):
        self.fl_observation = fl_observation
        self.fr_observation = fr_observation
        
        # define params of a circle for degrees
        self.half_circle = 180
        self.circle = 360

    def check_observation(self):
        """Returns a list of error classes associated with the 
        checked face left and face right observation"""
        errors = []
        if not self.distance_check():
            errors.append(ErrorDistance)
            
        if not self.horizontal_angle_check():
            errors.append(ErrorHorizontalAngle)

        if not self.zenith_angle_check():
            errors.append(ErrorZenithAngle)
            
        return errors

    def distance_check(self, tolerance):
        """Returns true is horizontal distance between faces 
        is within the tolerance defined in the settings file"""
        return abs(self.fr_observation.horizontal_distance - self.fl_observation.horizontal_distance) \
                <= tolerance
                 
    def horizontal_angle_check(self, tolerance):
        """Returns true if the horizontal angle between faces 
        is within the tolerance defined in the settings file"""
        fr_reduced = self.fr_observation.horizontal_angle - self.half_circle
        if fr_reduced < 0:
            fr_reduced + self.circle 
        return abs(fr_reduced - self.fl_observation.horizontal_angle) <= \
            tolerance

    def zenith_angle_check(self, tolerance):
        """Returns true if the zenith angle between faces is 
        within the tolerance defined in the settings file""" 
        total_zenith = self.fl_observation.zenith_angle + \
            self.fr_observation.zenith_angle
        return abs(total_zenith - self.circle) <= tolerance


class GonReducedObservationChecker(DecimalReducedObservationChecker):
    """Checks if a reduced gons observation is within tolerance"""
    def __init__(self, fl_observation, fr_observation):
        super().__init__(fl_observation, fr_observation)
        # define params of a circle for gons
        self.half_circle = 200 
        self.circle = 400


class SetupsChecker:
    @staticmethod
    def no_target_obs(setups):
        """returns a list of setups with 
        no target obs within it"""
        return [setup for setup in setups if setup.total_target_observations == 0]


