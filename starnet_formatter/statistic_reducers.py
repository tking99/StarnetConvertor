from decimal import Decimal
from math import radians, sin

from starnet_formatter.convertors import gons_to_degress

class StatisticReducer:
    def __init__(self, target_reducer, settings):
        self.target_reducer = target_reducer
        self.settings = settings 

    def delta_hz_angle(self, ob, mean_ob):
        mean_ob_angle = self.target_reducer.increment_angle(mean_ob.hz_angle)
        ob_angle = self.target_reducer.increment_angle(ob.hz_angle)
        if ob.face == self.target_reducer.FACE_RIGHT:
            adj_angle = 200 if mean_ob_angle < 200 else -200
            ob_angle -= adj_angle
        return self.target_reducer.decrement_angle(ob_angle-mean_ob_angle)
  
    def delta_za_angle(self, ob, mean_ob):
        return self.target_reducer.reduce_za(ob) - mean_ob.za_angle

    def delta_slope_dist(self, ob, mean_ob):
        return ob.slope_distance - mean_ob.slope_distance

    def delta_hor_dist(self, ob, mean_ob, apply_scale=False):
        if not apply_scale:
            return ob.no_scale_hor_dist - mean_ob.hor_distance
        return ob.scale_hor_dist - mean_ob.hor_distance

    def hz_angle_within_tolerance(self, value):
        return abs(value) < self.settings.hz_angle_tolerance

    def za_angle_within_tolerance(self, value):
        return abs(value) < self.settings.za_angle_tolerance

    def linear_within_tolerance(self, value):
        return abs(value) < self.settings.distance_tolerance

    
class GonStatisticReducer(StatisticReducer):
    CODE = 'GONS'
    @classmethod 
    def angle_mm_hd(cls, delta_angle, hd):
        """Returns the mm/HD of the delta_angle"""
        return Decimal(sin(radians(gons_to_degress(
            delta_angle)))) * hd


class DegStatisticReducer(GonStatisticReducer):
    CODE = 'DMS'
   


