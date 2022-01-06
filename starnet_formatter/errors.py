class FormatError:
    def __init__(self, line_number):
        self.line_number = line_number

class FormatNoSetupForObservationError(FormatError):
    @property
    def error_statement(cls):
        return 'No prior Setup to allocate Observation too'


class FormatHZAngleError(FormatError):
    @property
    def error_statement(cls):
        return 'HZ Angle format is incorrect'


class FormatZAAngleError(FormatError):
    @property 
    def error_statement(cls):
        return 'ZA Angle format is incorrect'


class FormatSlopeDistanceError(FormatError):
    @property 
    def error_statement(cls):
        return 'Slope distance format is incorrect'
    

class FormatInstrumentHeightError(FormatError):
    @property 
    def error_statement(cls):
        return 'Instrument height format is incorrect'


class FormatTargetHeightError(FormatError):
    @property 
    def error_statement(cls):
        return 'Target height format is incorrect'


class FormatPrismConstantError(FormatError):
    @property 
    def error_statemnet(cls):
        return 'Prism constant format is incorrect'


class FormatAtrStatusError(FormatError):
    @property 
    def error_statement(cls):
        return 'Atr status format is incorrect'


class FormatFaceError(FormatError):
    @property 
    def error_statement(cls):
        return 'Face format is incorrect'


class FormatDateTimeError(FormatError):
    @property 
    def error_statement(cls):
        return 'Date time format is incorrect'

class FormatInclinLongError(FormatError):
    @property 
    def error_statement(cls):
        return 'Instrument Inclin Long format is incorrect'


class FormatInclinTravError(FormatError):
    @property
    def error_statement(cls):
        return 'Instrument Inclin Trav format is incorrect'


class FormatScaleFactorError(FormatError):
    @property 
    def error_statement(cls):
        return 'Scale Factor format is incorrect'


class FormatGeometricPPMError(FormatError):
    @property 
    def error_statement(cls):
        return 'Geometric PPM format is incorrect'


class FormatAtmosphericPPMError(FormatError):
    @property 
    def error_statement(cls):
        return 'Atmospheric PPM format is incorrect'


class FormatSetupLineLengthError(FormatError):
    @property 
    def error_statement(cls):
        return 'Incorrect number of Setup elements'


class FormatObservationLineLengthError(FormatError):
    @property 
    def error_statement(cls):
        return 'Incorrect number of observation elements'


