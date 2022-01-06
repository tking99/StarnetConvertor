class FormatFileObservationElementsExtractor:
    """Extracts obeservation data from a SOA format file"""
    CODE = 'OB'
    @staticmethod
    def extract_target_name(ob_line):
        return ob_line[1]

    @staticmethod
    def extract_horizontal_angle(ob_line):
        return ob_line[2]

    @staticmethod
    def extract_zenith_angle(ob_line):
        return ob_line[3]

    @staticmethod
    def extract_slope_distance(ob_line):
        return ob_line[4]
    
    @staticmethod
    def extract_target_height(ob_line):
        return ob_line[7]
    
    @staticmethod
    def extract_prism_constant(ob_line):
        return ob_line[8]

    @staticmethod
    def extract_atr_on(ob_line):
        return ob_line[9]

    @staticmethod 
    def extract_face(ob_line):
        return ob_line[10]

    @staticmethod 
    def extract_date_time(ob_line):
        return ob_line[11]

    @staticmethod
    def extract_inclin_long(ob_line):
        return ob_line[12]

    @staticmethod
    def extract_inclin_trav(ob_line):
        return ob_line[13]

    @staticmethod
    def extract_scale_factor(ob_line):
        return ob_line[14]

    @staticmethod 
    def extract_geometric_ppm(ob_line):
        return ob_line[15]
    
    @staticmethod 
    def extract_atmospheric_ppm(ob_line):
        return ob_line[16]

    @staticmethod
    def extract_code(ob_line):
        return ob_line[17]

    @staticmethod
    def extract_attribute(ob_line):
        return ob_line[18]


class FormatFileSetupElementsExtractor:
    """Extracts setup data from a SOA format file""" 
    CODE = 'SU'
    @staticmethod
    def extract_setup_name(setup_line):
        return setup_line[1] 

    @staticmethod
    def extract_instrument_height(setup_line):
        return setup_line[2]

    @staticmethod 
    def extract_date_time(setup_line):
        return setup_line[3]
        

    @staticmethod
    def extract_atmospheric_ppm(setup_line):
        return setup_line[4]
    
    @staticmethod
    def extract_scale_factor(setup_line):
        return setup_line[5]





 


        