import appdaemon.plugins.hass.hassapi as hass



class Settings(hass.Hass):
    
    def initialize(self):
        asics_pass = self.args['asics_pass']

        
        self._living_room_t = 'sensor.ble_temperature_living_room'
        self._child_room_t = 'sensor.temperature_child'
        self._guest_room_t = 'sensor.temperature_guest'
        self._parents_room_t = 'sensor.temperature_parents'
        self._basement_t = 'sensor.temperature_square1'
        self._toilet_t = 'sensor.temperature_toilet'
        self._basement_door_t = 'sensor.sonoff1_temp'
        self._antifreeze_t = 'sensor.sonoff_th16_3_temp'
        self._oil_t = 'sensor.sonoff_th16_2_temp'
        self._outside_t = 'sensor.ble_temperature_outside'
        self.billyard_t = 'sensor.ble_temperature_billyard'
        
        
        self._heater_thermostat = 'climate.heater_thermostat'
        
        ####################### Контроллеры непосредственно асиками #############
        self.asics_switch_1 = 'switch.sonoff_pow_2'
        self.asics_switch_2 = 'switch.sonoff_pow_3'
        self.asics_switch_3 = 'switch.sonoff_pow_4'
        
        self.asics_thermostat_support = 'climate.asics_thermostat_temp'
        self.asics_thermostat_main_1 = 'climate.asics_thermostat_main_temp'
        self.asics_thermostat_main_2 = 'climate.asics_thermostat_main_temp_2'
        
        self.asics_climate_support = 'climate.asics_thermostat_support'
        self.asics_climate_main = 'climate.asics_thermostat_main'
        self.asics_climate_main_2 = 'climate.asics_thermostat_main_2'
        
        self.asics_main_1 = 0.1
        self.asics_main_2 = 0.2
        #######################################################################
        
        ####################### IP адреса асиков ###############################
        self.asic_ips = {
            self.asics_climate_support: [133, 137],
            self.asics_climate_main: [134, 138],
            self.asics_climate_main_2: [135],
        }
        
        self.asic_blades = {
            133: 3,
            134: 3,
            135: 2,
            136: 1,
            137: 3,
            138: 3,
        }
        
        self.asics_pwd = {
            133: asics_pass,
            134: asics_pass,
            135: asics_pass,
            136: asics_pass,
            137: asics_pass,
            138: asics_pass,
        }
        
        self.asics_power = {
            475: {
                    "voltage": 850,
                    "profile": 1,
                    "consumption": 850,
                },
            500: {
                    "voltage": 850,
                    "profile": 2,
                    "consumption": 950,
                },
            550: {
                    "voltage": 850,
                    "profile": 3,
                    "consumption": 880,
            },
            600: {
                    "voltage": 860,
                    "profile": 4,
                    "consumption": 1000,
            },
            631: {
                    "voltage": 860,
                    "profile": 5,
                    "consumption": 1050,
            },
            650: {
                    "voltage": 870,
                    "profile": 6,
                    "consumption": 1150,
            },
            675: {
                    "voltage": 870,
                    "profile": 7,
                    "consumption": 1200,
            },
            
            700: {
                    "voltage": 890,
                    "profile": 8,
                    "consumption": 1300,
            },
            750: {
                    "voltage": 890,
                    "profile": 10,
                    "consumption": 1500,
            },
            775: {
                    "voltage": 900,
                    "profile": 11,
                    "consumption": 1600,
            },
            
            
        }
        #######################################################################
        
        ######################### Выключители воды ###########################
        self.boiler_switch = 'switch.sonoff_pow_1'
        self.water_pump_switch = 'switch.sonoff_th16_1'
        ######################################################################
        
        ######################### Выключатели помп отопления###################
        self.oil_pump_switch = 'switch.sonoff_th16_2'
        self.antifreeze_pump_switch = 'switch.sonoff_th16_3'
        ########################################################################
        
        
        
    @property
    def outside_t(self):
        return self.get_state(self._outside_t)
    
    @property
    def living_room_t(self):
        return self.get_state(self._living_room_t)
    
    @property
    def child_room_t(self):
        return self.get_state(self._child_room_t)
    
    @property
    def guest_room_t(self):
        return self.get_state(self._guest_room_t)
    
    @property
    def parents_room_t(self):
        return self.get_state(self._parents_room_t)
    
    @property
    def basement_t(self):
        return self.get_state(self._basement_t)
    
    @property
    def toilet_t(self):
        return self.get_state(self._toilet_t)
    
    @property
    def basement_door_t(self):
        return self.get_state(self._basement_door_t)
        
    @property
    def basement_door_sensor(self):
        return self._basement_door_t
        
    @property
    def oil_t(self):
        return self.get_state(self._oil_t)
    
    @property   
    def oil_sensor(self):
        return self._oil_t
        

    @property
    def antifreeze_t(self):
        return self.get_state(self._antifreeze_t)
        
    @property
    def antifreeze_sensor(self):
        return self._antifreeze_t
        
    @property
    def asics_base_current_temp(self):
        return self.get_state(self.asics_thermostat_support, attribute = 'temperature')
        
    @property
    def heater_current_temp(self):
        return self.get_state(self._heater_thermostat, attribute = 'temperature')
        

        