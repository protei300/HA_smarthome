import appdaemon.plugins.hass.hassapi as hass
import datetime, time



class DB_Correction(hass.Hass):
    
    def initialize(self):
        self.run_every(self.db_correction, datetime.datetime.now(), 60*10)
        #self.call_service("recorder/purge", keep_days=10)
        #self.run_daily(self.purge_db, runtime)
        for i in range(1,5):
                self.call_service(
                                'mqtt/publish',
                                topic = f"Sonoff-Pow-{i}/cmnd/EnergyReset1",
                                payload = 0
                )
                print(f"Clearing daily consum on pow-{i}")
            
        
    def db_correction(self, kwargs):
        self.log("Checking state")
      
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
    
    
    
    def purge_db(self, kwargs):
        self.call_service("recorder/purge", keep_days=30)
        
        
        