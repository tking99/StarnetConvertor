from tkinter import ttk 

from starnet_formatter.convertors import gons_to_dms_str, gons_to_degress


class ObservationLabelStyles:
    def __init__(self):
        self.MEAN_STYLE = 'Mean.TLabel'
        mean_style = ttk.Style()
        mean_style.configure(self.MEAN_STYLE, font=('Sans', '11', 'bold'), padding=(5,5))

        self.STANDARD_STYLE = 'Standard.TLabel'
        standard_style = ttk.Style()
        standard_style.configure(self.STANDARD_STYLE, font=('Sans', '11'), padding=(5,5))

        self.OUTTOLERANCE_STYLE = 'OutTolerance.TLabel'    
        out_tolerance_style = ttk.Style()
        out_tolerance_style.configure(self.OUTTOLERANCE_STYLE, font=('Sans', 11), foreground='red', padding=(5,5))

        self.ACTIVE_ON_STYLE = 'ActiveOn.TLabel'
        active_on_style = ttk.Style()
        active_on_style.configure(self.ACTIVE_ON_STYLE, font=('Sans', '11'),
            foreground='green', sticky='E', padding=(5,5))

        self.ACTIVE_OFF_STYLE = 'ActiveOff.TLabel'
        active_off_style = ttk.Style()
        active_off_style.configure(self.ACTIVE_OFF_STYLE, font=('Sans', '11'),
            foreground='red', sticky='E', padding=(5,5))

        self.DELETE_OB_STYLE = 'Delete.TLabel'
        delete_style = ttk.Style()
        delete_style.configure(self.DELETE_OB_STYLE, font=('Sans', '11'),
            foreground='red', sticky='E', padding=(20,5))

    def stat_style(self, bol):
        """returns the required style based on the boolean past in
        if False, then stanard style is returned, else retruns outtolerance
        style"""
        if bol:
            return self.OUTTOLERANCE_STYLE
        return self.STANDARD_STYLE 
    
    def active_style(self, bol):
        """returns the required style based on the boolean past in
        if true, then active on style is returned, else reutrns active off
        style"""
        if bol:
            return self.ACTIVE_ON_STYLE
        return self.ACTIVE_OFF_STYLE


class LabelProcessor:
    def __init__(self, container):
        self.container = container
        self.labels = ObservationLabelStyles() 

    @staticmethod
    def _precision_format(measurement, places):
        """Returns the string format for an angle based on 
        the decimal places"""
        return '{m:.{places}f}'.format(m=measurement, places=places)


class ObservationLabelProcessor(LabelProcessor):
    def __init__(self, container, observation, ob_number, 
        survey_processor):
        super().__init__(container)
        self.observation = observation 
        self.ob_number = ob_number
        self.stat_reducer = survey_processor.stat_reducer
        self.settings = survey_processor.settings
        
        # create blank labels 
        self.ob_labels = tuple(ttk.Label(self.container, style=self.labels.STANDARD_STYLE) 
            for _ in range(7))
        self.hz_stat_labels = tuple(ttk.Label(self.container) for _ in range(3))
        self.v_stat_labels = tuple(ttk.Label(self.container) for _ in range(3))
        self.linear_stat_labels = tuple(ttk.Label(self.container) for _ in range(3))
    
    def update_labels(self, mean_ob):
        # set hor dist()
        self.set_hor_dist()
        self.update_ob_labels()
        self.update_hz_stat_labels(mean_ob)
        self.update_v_stat_labels(mean_ob)
        self.update_linear_stat_labels(mean_ob)

    def update_linear_stat_labels(self, mean_ob):
        """Updates the linear stat labels (SD, HD, Active)"""
        sd_delta = self.stat_reducer.delta_slope_dist(self.observation, mean_ob)
        style_name = self.labels.stat_style(abs(sd_delta) > self.settings.distance_tolerance)
        self.linear_stat_labels[0]['text'] = self._precision_format(sd_delta, self.settings.linear_precision)
        self.linear_stat_labels[0].configure(style=style_name)

        hd_delta = self.stat_reducer.delta_hor_dist(self.observation, mean_ob)
        style_name = self.labels.stat_style(abs(hd_delta) > self.settings.distance_tolerance)
        self.linear_stat_labels[1]['text'] = self._precision_format(hd_delta, self.settings.linear_precision)
        self.linear_stat_labels[1].configure(style=style_name)

        self.linear_stat_labels[2]['text'] = self.active_button_str(
                self.observation.slope_distance_on)
        self.linear_stat_labels[2].configure(style=self.labels.active_style(
            self.observation.slope_distance_on))
        self.linear_stat_labels[2].bind("<Button-1>", lambda e, ob=self.observation:
            self.container.active_linear_toggle(ob))

    def delete_observation_label(self):
        delete_label = ttk.Label(self.container, text='x', style=self.labels.DELETE_OB_STYLE,
            cursor='hand2')
        delete_label.bind("<Button-1>", lambda e, ob=self.observation:
            self.container.delete_observation(ob))
        return delete_label

    def set_hor_dist(self):
        """sets the horizontal distance for the labels"""
        self.hor_dist = self.observation.no_scale_hor_dist 
        if self.settings.apply_scale_factor:
            self.hor_dist = self.observation.scale_hor_dist
           
    def active_button_str(self, boolean):
        if boolean:
            return 'On'
        return 'Off'


class GonObservationLabelProcessor(ObservationLabelProcessor):
    CODE = 'GONS'
    def update_hz_stat_labels(self, mean_ob):
        """Update the Hz stat labels (Delta Hz, Hz/HD, Active)"""
        hz_delta = self.stat_reducer.delta_hz_angle(self.observation, mean_ob)
        style_name = self.labels.stat_style(abs(hz_delta) > self.settings.hz_angle_tolerance)
        
        self.hz_stat_labels[0]['text'] = self._precision_format(hz_delta, self.settings.angular_precision)
        self.hz_stat_labels[0].configure(style=style_name)

        hz_mm = self.stat_reducer.angle_mm_hd(hz_delta, self.hor_dist)
        style_name = self.labels.stat_style(abs(hz_mm) > self.settings.distance_tolerance)
            
        self.hz_stat_labels[1]['text'] = self._precision_format(hz_mm, self.settings.linear_precision)
        self.hz_stat_labels[1].configure(style=style_name)

        self.hz_stat_labels[2]['text'] = self.active_button_str(
                self.observation.hz_angle_on)
        self.hz_stat_labels[2].configure(style=self.labels.active_style(
            self.observation.hz_angle_on))
        self.hz_stat_labels[2].bind("<Button-1>", lambda e, ob=self.observation:
            self.container.active_hz_toggle(ob))
        
    def update_v_stat_labels(self, mean_ob):
        """Update the V stat labels (Delta V, V/HD, Active)"""
        za_delta = self.stat_reducer.delta_za_angle(self.observation, mean_ob)
        style_name = self.labels.stat_style(abs(za_delta) > self.settings.za_angle_tolerance)
        self.v_stat_labels[0]['text'] = self._precision_format(za_delta, self.settings.angular_precision)
        self.v_stat_labels[0].configure(style=style_name)

        za_mm = self.stat_reducer.angle_mm_hd(za_delta, self.hor_dist)
        style_name = self.labels.stat_style(abs(za_mm) > self.settings.distance_tolerance)
        
        self.v_stat_labels[1]['text'] = self._precision_format(za_mm, self.settings.linear_precision)
        self.v_stat_labels[1].configure(style=style_name)

        self.v_stat_labels[2]['text'] = self.active_button_str(
                self.observation.za_angle_on)
        self.v_stat_labels[2].configure(style=self.labels.active_style(
            self.observation.za_angle_on))
        self.v_stat_labels[2].bind("<Button-1>", lambda e, ob=self.observation:
            self.container.active_v_toggle(ob))


    def update_ob_labels(self):
        """updates the ob labels"""
        self.ob_labels[0]['text'] = '+'
        self.ob_labels[0]['cursor'] = 'hand2'
        self.ob_labels[0].bind("<Button-1>", lambda e, ob=self.observation:
            self.container.display_ob_details(ob))
        self.ob_labels[1]['text'] = self.ob_number
        self.ob_labels[2]['text'] = self._precision_format(self.observation.hz_angle,
            self.settings.angular_precision) 
        self.ob_labels[3]['text'] = self._precision_format(self.observation.za_angle,
            self.settings.angular_precision)
        self.ob_labels[4]['text'] = self._precision_format(self.observation.slope_distance,
            self.settings.linear_precision)
        self.ob_labels[5]['text'] = self._precision_format(self.hor_dist, self.settings.linear_precision)
        self.ob_labels[6]['text'] = self.observation.face


class DMSObservationLabelProcessor(GonObservationLabelProcessor):
    CODE = 'DMS'
    def update_ob_labels(self):
        self.ob_labels[0]['text'] = '+'
        self.ob_labels[0]['cursor'] = 'hand2'
        self.ob_labels[0].bind("<Button-1>", lambda e, ob=self.observation:
            self.container.display_ob_details(ob))
        self.ob_labels[1]['text'] = self.ob_number
        self.ob_labels[2]['text'] = gons_to_dms_str(self.observation.hz_angle)
        
        self.ob_labels[3]['text'] = gons_to_dms_str(self.observation.za_angle)
        self.ob_labels[4]['text'] = self._precision_format(self.observation.slope_distance,
            self.settings.linear_precision)
        self.ob_labels[5]['text'] = self._precision_format(self.hor_dist, self.settings.linear_precision)
        self.ob_labels[6]['text'] = self.observation.face

    def update_hz_stat_labels(self, mean_ob):
        """Update the Hz stat labels (Delta Hz, Hz/HD, Active)"""
        hz_delta = self.stat_reducer.delta_hz_angle(self.observation, mean_ob)
        style_name = self.labels.stat_style(abs(hz_delta) > self.settings.hz_angle_tolerance)
        
        self.hz_stat_labels[0]['text'] = self._precision_format(gons_to_degress(hz_delta), self.settings.angular_precision)
        self.hz_stat_labels[0].configure(style=style_name)

        hz_mm = self.stat_reducer.angle_mm_hd(hz_delta, self.hor_dist)
        style_name = self.labels.stat_style(abs(hz_mm) > self.settings.distance_tolerance)
            
        self.hz_stat_labels[1]['text'] = self._precision_format(hz_mm, self.settings.linear_precision)
        self.hz_stat_labels[1].configure(style=style_name)

        self.hz_stat_labels[2]['text'] = self.active_button_str(
                self.observation.hz_angle_on)
        self.hz_stat_labels[2].configure(style=self.labels.active_style(
            self.observation.hz_angle_on))
        self.hz_stat_labels[2].bind("<Button-1>", lambda e, ob=self.observation:
            self.container.active_hz_toggle(ob))
        
    def update_v_stat_labels(self, mean_ob):
        """Update the V stat labels (Delta V, V/HD, Active)"""
        za_delta = self.stat_reducer.delta_za_angle(self.observation, mean_ob)
        style_name = self.labels.stat_style(abs(za_delta) > self.settings.za_angle_tolerance)
        self.v_stat_labels[0]['text'] = self._precision_format(gons_to_degress(za_delta), self.settings.angular_precision)
        self.v_stat_labels[0].configure(style=style_name)

        za_mm = self.stat_reducer.angle_mm_hd(za_delta, self.hor_dist)
        style_name = self.labels.stat_style(abs(za_mm) > self.settings.distance_tolerance)
        
        self.v_stat_labels[1]['text'] = self._precision_format(za_mm, self.settings.linear_precision)
        self.v_stat_labels[1].configure(style=style_name)

        self.v_stat_labels[2]['text'] = self.active_button_str(
                self.observation.za_angle_on)
        self.v_stat_labels[2].configure(style=self.labels.active_style(
            self.observation.za_angle_on))
        self.v_stat_labels[2].bind("<Button-1>", lambda e, ob=self.observation:
            self.container.active_v_toggle(ob))



class MeanLabelProcessor(LabelProcessor):
    def __init__(self, container, survey_processor, target):
        super().__init__(container)
        self.survey_processor = survey_processor
        self.target = target 
        self.heading_label = ttk.Label(container, text='Mean: ', style=self.labels.MEAN_STYLE)
        self.hz_label = ttk.Label(container, style=self.labels.MEAN_STYLE)
        self.v_label = ttk.Label(container, style=self.labels.MEAN_STYLE)
        self.sd_label = ttk.Label(container, style=self.labels.MEAN_STYLE)
        self.hd_label = ttk.Label(container, style=self.labels.MEAN_STYLE)

        
class GonMeanLabelProcessor(MeanLabelProcessor):
    CODE = 'GONS'

    def update_mean_labels(self, mean_ob):
        """updates the mean label with the latest
        values"""
        angular_precision = self.survey_processor.settings.angular_precision
        linear_precision = self.survey_processor.settings.linear_precision
       
        self.hz_label['text'] = self._precision_format(
            mean_ob.hz_angle, angular_precision)
        self.v_label['text'] = self._precision_format(
            mean_ob.za_angle, angular_precision)
        self.sd_label['text'] = self._precision_format(
            mean_ob.slope_distance, linear_precision)
        self.hd_label['text'] = self._precision_format(
            mean_ob.hor_distance, linear_precision)

class DMSMeanLabelProcessor(MeanLabelProcessor):
    CODE = 'DMS'
    
    def update_mean_labels(self, mean_ob):
        """updates the mean label with the latest
        values"""
        angular_precision = self.survey_processor.settings.angular_precision
        linear_precision = self.survey_processor.settings.linear_precision
       
        self.hz_label['text'] = gons_to_dms_str(mean_ob.hz_angle)
        self.v_label['text'] = gons_to_dms_str(mean_ob.za_angle)
        self.sd_label['text'] = self._precision_format(
            mean_ob.slope_distance, linear_precision)
        self.hd_label['text'] = self._precision_format(
            mean_ob.hor_distance, linear_precision)




        

        