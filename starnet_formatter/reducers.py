from statistics import mean
from math import sin, radians
from decimal import Decimal

from starnet_formatter.surveyModels import GonMeanObservation, DecimalMeanObservation


class TargetObReducer:
    FACE_LEFT = '1'
    FACE_RIGHT = '2'
    FACE_BOTH = '3'

    def _reset_totals(self):
        self.hz_fl_angles = []
        self.hz_fr_angles = []
        self.za_angles = []
        self.slope_dist = []
        self.hor_dist = []
       
       
class GonTargetObReducer(TargetObReducer):
    CODE = 'GONS'
    def create_mean_observation(self, observations, apply_scale=False):
        """Creates a mean observation from a list of observations"""
        self._reset_totals()
        for ob in observations:
            if ob.hz_angle_on:
                if ob.face == self.FACE_RIGHT:
                    # add to fr angles
                    self.hz_fr_angles.append(self.increment_angle(ob.hz_angle)) 
                else:
                    # fl or both add to fl angles
                    self.hz_fl_angles.append(self.increment_angle(ob.hz_angle))

            if ob.za_angle_on:
                #reduce za and add to list
                self.za_angles.append(self.reduce_za(ob))

            if ob.slope_distance_on:
                self.slope_dist.append(ob.slope_distance)
                if not apply_scale:
                    self.hor_dist.append(ob.no_scale_hor_dist)
                else:
                    self.hor_dist.append(ob.scale_hor_dist)   
        
        if self.check_active_observation_present():
            # check if there is at least one active observation before making mean      
            return GonMeanObservation(
                self.decrement_angle(self.mean_hz_angle()),
                mean(self.za_angles),
                mean(self.slope_dist),
                mean(self.hor_dist),
            )
        return 

    def _increment_fr_angles(self):
        adj_angle = 0
        if self.hz_fl_angles and self.hz_fr_angles:
            fl_mean_ang = mean(self.hz_fl_angles)  
            fr_mean_ang = mean(self.hz_fr_angles)

            if fl_mean_ang > fr_mean_ang:
                adj_angle = 200
            else:
                adj_angle = -200
        
        elif self.hz_fr_angles:
            fr_mean_ang = mean(self.hz_fr_angles)
            if fr_mean_ang > 200:
                adj_angle = -200
            else:
                adj_angle = 200
                
        self.hz_fr_angles = [angle+adj_angle for angle in self.hz_fr_angles]
    

    def mean_hz_angle(self):
        self._increment_fr_angles()
        return mean(self.hz_fl_angles+self.hz_fr_angles)
    
    def check_active_observation_present(self):
        return self.hz_fl_angles or self.hz_fr_angles\
         and self.za_angles and self.slope_dist and self.hor_dist

    def one_hz_angle(self):
        return len(self.hz_angles) == 1 
    
    def one_za_angle(self):
        return len(self.za_angles) == 1 

    def one_slope_dist(self):
        return len(self.slope_dist) == 1 

    @classmethod
    def reduce_hz_by_angle(cls, hz_angle, delta):
        """reduces a hz_angle by a passed in delta"""
        reduced_hz_angle = hz_angle - delta
        if reduced_hz_angle < 0:
            reduced_hz_angle += 400
        return cls.decrement_angle(reduced_hz_angle) 

    @classmethod
    def reduce_hz(cls, ob):
        # increment angle to avoid zero error
        angle = cls.increment_angle(ob.hz_angle)
        # reduce angle if face right
        if ob.face == cls.FACE_RIGHT:
            if angle < 200:
                angle += 200
            else:
                angle -= 200
        return angle 

    @classmethod
    def reduce_za(cls, ob):
        """Redces a face right za angle observation"""
        if ob.za_angle < 200:
            return ob.za_angle
        return 400 - ob.za_angle

    @classmethod
    def increment_angle(cls, angle):
        """increments the hz_angle by 400 to 
        avoid the 0 problem"""
        if angle >=0 and angle < 1:
            return angle + 400  
        return angle

    @classmethod
    def decrement_angle(cls, angle):
        """decrements a hz_angle by 400 untill
        its below 400"""
        while angle >= 400:
            angle -= 400
        return angle 
        

class DegTargetObReducer(GonTargetObReducer):
    CODE = 'DMS'
    pass 