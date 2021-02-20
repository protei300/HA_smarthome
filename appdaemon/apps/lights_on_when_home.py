import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
#
# Hellow World App
#
# Args:
#

class Lights_on_when_home(hass.Hass):
  
  def initialize(self):
     self.settings = self.get_app("settings")
     if self.get_state('group.who_in_home') == 'home':
         self.status_at_home = True
     else:
         self.status_at_home = False
     self.log("Module detection of owners is ready to work")
     self.log(f"sun now is {self.sun_down()} and group_in_home is {self.get_state('group.who_in_home')}, status_at_home = {self.status_at_home}")
     self.log(f"Sunset at {self.sunset()}")
     self.log(f"Sunrise at {self.sunrise()}")
     self.listen_state(self.we_are_home, "group.who_in_home", new = "home")
     self.listen_state(self.we_are_away, "group.who_in_home", new = "not_home",
                        duration = 2*60*60)
     self.run_at_sunrise(self.auto_lights_perimeter_off, offset = 30*60)
     self.run_at_sunset(self.auto_lights_perimeter_on, offset = 0)
     
  def we_are_home(self,entity, attribute, old, new, kwargs):
      self.log(f"Owner at home at time {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} status_at_home = {self.status_at_home}")
      if self.status_at_home is False:
          if self.sun_down():
              light_group = self.args['switch']
              for switches in light_group:
                self.turn_on(switches)
          if self.get_state(self.settings.boiler_switch) == 'off':
              self.turn_on(self.settings.boiler_switch)
          self.turn_on('switch.sonoff_t1_2')
          self.notify("Добро пожаловать на Дачу", title = "*Дача*", name = "telegram")
          self.status_at_home = True
  
  def we_are_away(self, entity, attribute, old, new, kwargs):
      #self.notify("Хорошей дороги!!!, Нагреватель воды выключен", title = "Дача", name = "pushbullet_notify")
      if self.get_state(self.get_app("settings").boiler_switch) == 'on':
          self.notify(f"Нагреватель воды выключен в {datetime.now().strftime('%Y-%m-%d %H:%m')}", name = "telegram")
          self.turn_off(self.settings.boiler_switch)
      self.turn_off('switch.sonoff_t1_2')
      light_group = self.args['switch']
      for switches in light_group:
          self.turn_off(switches)
      self.status_at_home = False
  
  def auto_lights_perimeter_off(self, kwargs):
      if self.get_state("group.outside_light") == "on":
          light_group = self.args['switch']
          for switches in light_group:
              self.turn_off(switches)
        
  def auto_lights_perimeter_on(self, kwargs):
      self.log (f"Switch on Perimeter Lights, because someone at {self.get_state('group.who_in_home')}")
      if self.status_at_home == True:
          light_group = self.args['switch']
          for switches in light_group:
              self.turn_on(switches)