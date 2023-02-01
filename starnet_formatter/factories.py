from tkinter import ttk 

from starnet_formatter.builders import FormatFileGonObLineBuilder, FormatFileDecimalObLineBuilder
from starnet_formatter.reducers import GonTargetObReducer, DegTargetObReducer
from starnet_formatter.statistic_reducers import GonStatisticReducer, DegStatisticReducer
from starnet_formatter.surveyModels import StarnetSideShotMeasurementM, StarnetSideShotMeasurementSS


class AngularFactory:
    ANGULAR_CODE = ('GONS', 'DMS')

class FormatObLineBuilderFactory(AngularFactory):
    """Returns the correct OB line builder based on the 
    builder code passed in"""
    BUILDERS = (FormatFileGonObLineBuilder, FormatFileDecimalObLineBuilder)

    @classmethod 
    def builder(cls, builder_code):
        if builder_code in cls.ANGULAR_CODE:
            for builder in cls.BUILDERS:
                if builder.CODE == builder_code:
                    return builder

class TargetObservationReducerFactory(AngularFactory):
    """Returns the correct Ob line reducer based on the 
    reducer code passed in"""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    OB_REDUCERS = (GonTargetObReducer, DegTargetObReducer)

    @classmethod 
    def reducer(cls, reducer_code):
        if reducer_code in cls.ANGULAR_CODE:
            for reducer in cls.OB_REDUCERS:
                if reducer.CODE == reducer_code:
                    return reducer

class ObservationStatReducerFactory(AngularFactory):
    """Returns the correct stat reducer based on the 
    reducer code passed in"""
    STAT_REDUCERS = (GonStatisticReducer, DegStatisticReducer)

    @classmethod 
    def reducer(cls, reducer_code):
        if reducer_code in cls.ANGULAR_CODE:
            for reducer in cls.STAT_REDUCERS:
                if reducer.CODE == reducer_code:
                    return reducer


class StarnetSideShotFactory:
    """Returns the Side shot Measurment class based on the 
    passed in side shot code"""
    STARNET_SIDE_SHOT_MEASUREMENTS = (StarnetSideShotMeasurementM, StarnetSideShotMeasurementSS)
    
    @classmethod 
    def side_shot_measurement_class(cls, code):
        for side_shot in cls.STARNET_SIDE_SHOT_MEASUREMENTS:
            if side_shot.CODE == code:
                return side_shot


    