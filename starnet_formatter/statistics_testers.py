from decimal import Decimal
from math import radians, sin


class StatisticTester:
    @classmethod 
    def delta_angle(cls, mean_angle, angle):
        """Returns the delta angle compared to the mean"""
        return angle - mean_angle

    @classmethod
    def delta_distance(cls, mean_distance, distance):
        """Returns the delta distance compared to the mean"""
        return distance - mean_distance 


class GONStatisticTester(StatisticTester):
    CODE = 'GONS'
    @classmethod 
    def angle_mm_hd(cls, delta_angle, hd):
        """Returns the mm/HD of the delta_hz_angle"""
        return sin(radians(GONStatisticTester.convert_gon_to_deg(
            delta_angle))) * hd

    @staticmethod
    def convert_gon_to_deg(angle):
        """Converts gon angle to degress"""
        return Decimal(angle) * Decimal(0.89999994954991)


class DecimalStatisticTester(StatisticTester):
    CODE = 'DEG'
    @classmethod
    def angle_mm_hd(cls, delta_angle, hd):
        """Returns the mm/HD of the delta_hz_angle"""
        return sin(radians(delta_angle)) * hd


