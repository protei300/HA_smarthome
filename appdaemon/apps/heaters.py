import appdaemon.plugins.hass.hassapi as hass
import time
#
# Hellow World App
#
# Args:
#




class Set_heating_type(hass.Hass):

    def initialize(self):
        self.log("Heating type automation in work")
        self.settings = self.get_app("settings")
        self.ASICS_DELTA_1 = self.settings.asics_main
        self.ASICS_DELTA_2 = self.settings.asics_main_2
        
        #self.listen_state(self.change_heater_mode, "input_boolean.thermostat_to_use")
        self.listen_state(self.winter_mode, 'input_boolean.winter_mode')
        self.listen_state(self.main_asics_switch, 'input_boolean.asics_main_demand')
        self.listen_state(self.main_asics_switch_2, 'input_boolean.asics_main_demand_2')
        self.listen_state(self.support_asics_switch, 'input_boolean.asics_support_demand')
        
        
        ####### Следим за состоянием требования включения котла #################
        self.listen_state(self.heater_switch, 'input_boolean.heater_on')
        
        #Управление насосами масла и антифриза
        self.listen_state(self.oil_pump_switch, self.settings.oil_sensor)
        self.listen_state(self.antifreeze_pump_switch, self.settings.antifreeze_sensor)
         
         
        
        ###### Выставляем начальные значения исполняющего климата на котле ################
        
        if self.get_state('input_boolean.heater_on') == 'on':
            self.call_service('climate/turn_on', entity_id = 'climate.heater_preserve_antifreeze')
        elif self.get_state('input_boolean.heater_on') == 'off':
            self.call_service('climate/turn_off', entity_id = 'climate.heater_preserve_antifreeze')
        
        
        ###### Выставляем начальные значения исполняющего климата на асиках ################
        
        if self.get_state('input_boolean.asics_support_demand') == 'on':
            self.call_service('climate/turn_on', entity_id = self.settings.asics_thermostat_support)
        elif self.get_state('input_boolean.asics_support_demand') == 'off' and self.get_state('input_boolean.winter_mode') == 'off': 
            self.call_service('climate/turn_off', entity_id = self.settings.asics_thermostat_support)
        
        if self.get_state('input_boolean.asics_main_demand') == 'on':
            self.call_service('climate/turn_on', entity_id = self.settings.asics_thermostat_main)
        elif self.get_state('input_boolean.asics_main_demand') == 'off':#  and self.get_state('input_boolean.winter_mode') == 'off':
            self.call_service('climate/turn_off', entity_id = self.settings.asics_thermostat_main)
        
        if self.get_state('input_boolean.asics_main_demand_2') == 'on':
            self.call_service('climate/turn_on', entity_id = self.settings.asics_thermostat_main_2)
        elif self.get_state('input_boolean.asics_main_demand_2') == 'off':
            self.call_service('climate/turn_off', entity_id = self.settings.asics_thermostat_main_2)
        
        ##### Set ASICS TEMP in dependnce with support asics #################3
        self.listen_state(self.change_asics_temp, self.settings.asics_thermostat_support, attribute='temperature')
           
        #self.listen_state(self.set_heater_thermostat, "climate.heater_thermostat", new = 'heat')
        #self.listen_state(self.set_heater_preserve_antifreeze, "climate.heater_preserve_antifreeze", new = 'heat')
    
    def oil_pump_switch(self, entity, attribute, old, new, kwargs):
  
      if float(new) >= float(self.get_state('input_number.slider_oil_pump')) and self.get_state(self.settings.oil_pump_switch)=='off':
          self.log(f"turning on because {new} >= {self.get_state('input_number.slider_oil_pump')}")
          self.turn_on(self.settings.oil_pump_switch)
      elif float(new) < float(self.get_state('input_number.slider_oil_pump')) - 4 and self.get_state(self.settings.oil_pump_switch) == 'on':
          self.turn_off(self.settings.oil_pump_switch)
  
    def antifreeze_pump_switch(self, entity, attribute, old, new, kwargs):
        
        if new.lower() in ['unavailable', 'unknown']: 
            self.turn_on(self.settings.antifreeze_pump_switch)
            
        elif (self.get_state(self.settings.heater_switch) in ['on', 'unavailable'] \
        or self.get_state(self.settings.oil_pump_switch) == 'on') \
        and self.get_state(self.settings.antifreeze_pump_switch)=='off':
            self.turn_on(self.settings.antifreeze_pump_switch)
        
        elif ( self.get_state(self.settings.oil_pump_switch) =='off' \
        and self.get_state('switch.sonoff_basic_1') == 'off' \
        and float(new) < float(self.get_state('input_number.slider_temp_pump'))) \
        and self.get_state(self.settings.antifreeze_pump_switch) == 'on':
            self.turn_off(self.settings.antifreeze_pump_switch)       
 
 
    def change_heater_mode(self, entity, attribute, old ,new, kwargs):
      self.log(f"Heater mode has changed to {self.get_state('input_boolean.thermostat_to_use')}")
      thermostat_to_use = self.get_state('input_boolean.thermostat_to_use')
      if thermostat_to_use == 'on':

          self.call_service('climate/turn_off', entity_id = 'climate.heater_thermostat')
          self.call_service('climate/turn_on', entity_id = 'climate.heater_preserve_antifreeze')
      else:
          self.call_service('climate/turn_on', entity_id = 'climate.heater_thermostat')
          self.call_service('climate/turn_off', entity_id = 'climate.heater_preserve_antifreeze')

     
    def winter_mode(self,entity, attribute, old, new, kwargs):
        if self.get_state(entity) == 'on':
          self.log('winter mode is on')
          self.call_service('climate/set_temperature', entity_id = 'climate.heater_thermostat', temperature=4 )
          self.call_service('climate/turn_on', entity_id = 'climate.heater_thermostat')
          self.call_service('climate/turn_on', entity_id = self.settings.asics_thermostat_support)
          
        else:
          self.log('winter mode is off')
          self.call_service('climate/turn_off', entity_id = 'climate.heater_thermostat')
          self.call_service('climate/turn_off', entity_id = self.settings.asics_thermostat_support)



#######  Включаем выключаем котел ###########
    def heater_switch(self, entity, attribute, old, new, kwargs):
        if new == 'on':
            self.call_service('climate/turn_on', entity_id = 'climate.heater_preserve_antifreeze')
        elif new == 'off':
            self.call_service('climate/turn_off', entity_id = 'climate.heater_preserve_antifreeze')


#######  Включаем\выключаем асики ########
  
    def support_asics_switch(self, entity, attribute, old, new, kwargs):
        if new=='on':
            self.call_service('climate/turn_on', entity_id = self.settings.asics_oil_support)
        elif new == 'off' and self.get_state('input_boolean.winter_mode') == 'off':
            self.call_service('climate/turn_off', entity_id = self.settings.asics_oil_support)
            
    def main_asics_switch(self, entity, attribute, old, new, kwargs):
        if new=='on':
            self.call_service('climate/turn_on', entity_id = self.settings.asics_oil_main)
        elif new == 'off': # and self.get_state('input_boolean.winter_mode') == 'off':
            self.call_service('climate/turn_off', entity_id = self.settings.asics_oil_main)

    def main_asics_switch_2(self, entity, attribute, old, new, kwargs):
        if new=='on':
            self.call_service('climate/turn_on', entity_id = self.settings.asics_oil_main_2)
        elif new == 'off':
            self.call_service('climate/turn_off', entity_id = self.settings.asics_oil_main_2)
            
####### Выставляем температуру в термостатах асиках #######

    def change_asics_temp(self, entity, attribute, old, new, kwargs):
        self.call_service('climate/set_temperature', 
                                    entity_id = self.settings.asics_thermostat_main,
                                    temperature = new-self.ASICS_DELTA_1)
        self.call_service('climate/set_temperature', 
                                    entity_id = self.settings.asics_thermostat_main_2,
                                    temperature = new-self.ASICS_DELTA_2)
                                    