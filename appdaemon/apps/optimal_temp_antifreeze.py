import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Hellow World App
#
# Args:
#






class Optimal_temp(hass.Hass):
  
  calculated_temp = 0
  K_sek = 120   ### Количество секций
  Qnom = K_sek*185   ### Номинальная мощность секций   185Вт для чугунины
  dTnom = 70 ### Значение теплового потока табличное
  Gnom = 360 ### Номинальный расход воды через секцию кг/час
  n = 0.3    ### Показатель нелинейности теплоотдачи от температуры
  p = 0.02   ### Показатель нелинейности теплоотдачи от расхода

  def initialize(self):
     self.log(f"Module optimal_temp_antifreeze is ready to work, {self.get_state('switch.sonoff_basic_1')}")
     
     
     time = datetime.datetime.now()
     self.run_every(self.weather_temp_changed, time, 60*10)

 
      
  def weather_temp_changed(self, kwargs):
      K=0.8
      try:
          outside_temp = float(self.get_state("sensor.dark_sky_temperature"))
          current_antifr_temp = float(self.get_state("sensor.sonoff_th16_3_temp"))
      except ValueError:
          self.log("No data from DarkSky")
      else:
          target_temp = self.get_state("climate.heater_thermostat", attribute = "temperature")
          #target_temp = float(self.get_state("input_number.slider_target_temp"))
          wind_speed = float(self.get_state("sensor.dark_sky_wind_speed"))
          alternative_count = 360*(target_temp-outside_temp)*K/860*1000
         
          if alternative_count > 0:
            antifr_temp = self.calculate_optimal_temp(target_temp, 2, alternative_count)
          else:
            antifr_temp = target_temp-1
          if (self.get_state("input_boolean.antifreeze_temp_auto_set") == "on" and 
          self.get_state("climate.heater_thermostat") == "off" and
          self.get_state("climate.heater_preserve_antifreeze", attribute='current_temperature') != antifr_temp):
            self.call_service("climate/set_temperature", 
                                entity_id = "climate.heater_preserve_antifreeze",
                                temperature = antifr_temp)
          self.set_state("sensor.counted_antifreeze_temp", state = antifr_temp)
          self.calculated_temp = -outside_temp + target_temp + wind_speed 
      #self.log(f"temperature_calculated = {antifr_temp}")
  
  def calculate_optimal_temp(self, Td, dT, Q):
      Tpod = round(Td + dT + self.dTnom*pow(Q/self.Qnom,self.n+1),1)
      return Tpod
      