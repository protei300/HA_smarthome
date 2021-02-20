import appdaemon.plugins.hass.hassapi as hass
import datetime




class sonoff_checker(hass.Hass):
    
    def name_splitter(self, name):
        splitted_name = name.split('.')[1].split('_')[:-1]
        splitted_name[0] = splitted_name[0].capitalize()
        splitted_name[1] = splitted_name[1].upper()
        return "-".join(splitted_name)
    
    def initialize(self):
        
        self.log("Starting Sonoff_checker module")
        
        self.settings = self.get_app("settings")
        self.temp_sensors = [self.settings.basement_door_sensor, self.settings.oil_sensor, self.settings.antifreeze_sensor]
        
        
        self.run_every(self.temp_checker, datetime.datetime.now(), 60*10)

        
        
    
        ############# Загружаем чекеры базы по потреблению электричества ############    
        #self.run_every(self.db_correction, datetime.datetime.now(), 60*10)
        for i in range(1,5):
                status = self.get_state(f"sensor.sonoff_pow_{i}_status", attribute="RestartReason")
                self.log(status)
                if status == "Power On":
                    self.call_service(
                                    'mqtt/publish',
                                    topic = f"Sonoff-Pow-{i}/cmnd/EnergyReset1",
                                    payload = 0
                    )
                    self.call_service(
                                    'mqtt/publish',
                                    topic = f"Sonoff-Pow-{i}/cmnd/Restart",
                                    payload = 1
                    )
                    self.log(f"Clearning Database for POW-{i}")
                
    
    
    ########## Проверяем загрузились ли все датчики температурные ################
    def temp_checker(self, kwargs):
        for entity in self.temp_sensors:
            if self.get_state(entity) == 'unknown':
                self.log(f"No temp sensor located. Restarting {entity}")
                if self.name_splitter(entity) == 'sonoff1':
                    mqtt_topic = "Sonoff1/cmnd/Restart"
                else:
                    mqtt_topic = f"cmnd/{self.name_splitter(entity)}/Restart"
                self.log(mqtt_topic)
                self.call_service("mqtt/publish", topic = mqtt_topic, payload='1')
                #cmnd/sonoff-th16-2/Restart
        
        
        
    def db_correction(self, kwargs):
        #self.log("Checking state")
        if (self.get_state('sensor.asic_1_current_month_max') > self.get_state('sensor.sonoff_pow_2_energy_total_2')):
            self.call_service(
                                'mqtt/publish',
                                topic = "Sonoff-Pow-2/cmnd/EnergyReset3",
                                payload = (float(self.get_state('sensor.asic_1_current_month_max'))-float(self.get_state('sensor.sonoff_pow_2_energy_today')))*1000
                )
        if (self.get_state('sensor.asic_2_current_month_max') > self.get_state('sensor.sonoff_pow_3_energy_total')):
            self.call_service(
                                'mqtt/publish',
                                topic = "Sonoff-Pow-3/cmnd/EnergyReset3",
                                payload = (float(self.get_state('sensor.asic_2_current_month_max'))-float(self.get_state('sensor.sonoff_pow_3_energy_today')))*1000
                )
        if (self.get_state('sensor.asic_3_current_month_max') > self.get_state('sensor.sonoff_pow_4_energy_total')):
            self.call_service(
                                'mqtt/publish',
                                topic = "Sonoff-Pow-4/cmnd/EnergyReset3",
                                payload = (float(self.get_state('sensor.asic_3_current_month_max'))-float(self.get_state('sensor.sonoff_pow_4_energy_today')))*1000
                )
    