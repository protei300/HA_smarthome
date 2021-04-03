import appdaemon.plugins.hass.hassapi as hass
import datetime, time



class Daily_reporter(hass.Hass):
    
    def initialize(self):
        
        
        self.notify(f'Система успешно запустилась в {datetime.datetime.now().strftime("%y-%m-%d %H:%M")}', name = 'telegram')
        groupitem = self.get_state('group.sensor_batteries_alert', attribute = "all");
        entity_list = groupitem['attributes']['entity_id']
        self.settings = self.get_app("settings")
        self.run_daily(self.status_report, datetime.time(18,0,0))
        self.listen_state(self.update_report, 'binary_sensor.updater', new='on')
#        for i in entity_list:
#	        self.log('Subscribing to state change for ' + i );
#	        self.listen_state(self.battery_report, i);
        
    def status_report(self, kwargs):
        
        msg = f"Время: {datetime.datetime.now().strftime(format='%Y-%m-%d %H:%M')}\n\n"
        msg += f"Температура на улице {self.settings.outside_t}\n\n"
        msg += f"Температура в бильярдной {self.get_state(self.settings.billyard_t)}\n\n"
        msg += f"Температура в гостинной {self.settings.living_room_t}\n"
        msg += f"Температура в детской {self.settings.child_room_t}\n"
        msg += f"Температура в родительской {self.settings.parents_room_t}\n"
        msg += f"Температура в гостевой {self.settings.guest_room_t}\n"
        msg += f"Температура в туалете {self.settings.toilet_t}\n"
        msg += f"Температура у фильтров {self.settings.basement_t}\n"
        msg += f"Темперутару у гаражной двери {self.settings.basement_door_t}\n\n"
        msg += f"Котел потребил электричества сегодня {self.get_state('sensor.heater_power_consum_1_day_report')} КВт-ч\n"
        msg += f"Бойлер потребил электричества сегодня {self.get_state('sensor.sonoff_pow_1_energy_today')} КВт-ч\n"
        msg += f"Асики потребили электричества сегодня {round(float(self.get_state('sensor.sonoff_pow_2_energy_today')) + float(self.get_state('sensor.sonoff_pow_3_energy_today')) + float(self.get_state('sensor.sonoff_pow_4_energy_today')),2)} КВт-ч"
        self.notify(msg, name = "telegram")
        
    def battery_report(self, entity, attribute, old, new, kwargs):
        text_message = self.get_state(entity, attribute="friendly_name")
        if float(self.get_state(entity))<15:
            self.notify(f"Замените батарею в датчике: {text_message}", name= 'telegram')
        
    
    def update_report(self, entity, attribute, old, new, kwargs):
        
        ver = self.get_state('binary_sensor.updater', attribute = 'newest_version')
        msg = f'Доступно обновление системы до версии {ver}'
        self.notify(msg, name="telegram")
        

import appdaemon.appapi as appapi

class Telegram_bot(hass.Hass):



    def initialize(self):
        """Listen to Telegram Bot events of interest."""
        #self.listen_event(self.receive_telegram_text, 'telegram_text')
        self.settings = self.get_app("settings")
        self.listen_event(self.receive_telegram_command, 'telegram_command')
        self.listen_event(self.receive_telegram_callback, 'telegram_callback')
    
################# Универсальная функция включения чего-либо ###########################    
    def switch_on_off(self, command, entity, user_id, message, good_state_message, keyboard=None):
        self.call_service(command, entity_id = entity)
        time.sleep(1.5)
        if str(self.get_state(entity)).lower() == good_state_message:
            msg = f'{datetime.datetime.today().strftime("%y-%m-%d %H:%M")}: {message[0]}'
        else:
            msg = f'{datetime.datetime.today().strftime("%y-%m-%d %H:%M")}: {message[1]}'
        self.call_service('telegram_bot/send_message',
                          target = user_id,
                          message=msg,
                          disable_notification=True,
                          inline_keyboard=keyboard)
    
    
    
    def receive_telegram_text(self, event_id, payload_event, *args):
        """Text repeater."""
        self.log(event_id)
        assert event_id == 'telegram_text'
        user_id = payload_event['user_id']
        self.log('You said: ``` %s ```' % payload_event['text'])
        if payload_event['text'].lower() == 'status':
            keyboard = [[("Статус датчиков", "/temp_msg"),
                        ("Remove this button", "/remove button")]]
            self.call_service('telegram_bot/send_message',
                              title='*Статус датчиков*',
                              target=user_id,
                              message='',
                              disable_notification=True,
                              inline_keyboard=keyboard)

############################## Разные отчеты #####################################

    def receive_telegram_command(self, event_id, payload_event, *args):

        self.log(event_id)
        assert event_id == 'telegram_command'
        user_id = payload_event['user_id']
        callback_id = payload_event['id']
        args = payload_event['args']
        self.log('You said: ``` %s ```' % payload_event['command'])

####################### Различные отчеты ##################################

        if payload_event['command'] == '/status':
            #keyboard = [[("Статус датчиков температуры", "/temp_report")]]
            
            msg = f"Время: {datetime.datetime.today().strftime(format='%Y-%m-%d %H:%M')}\n"
            msg += "Температура:\n"
            msg += f"- На улице {self.settings.outside_t}\n"
            msg += f"- В гостинной {self.settings.living_room_t}\n"
            msg += f"- В детской {self.settings.child_room_t}\n"
            msg += f"- В родительской {self.settings.parents_room_t}\n"
            msg += f"- В гостевой {self.settings.guest_room_t}\n"
            msg += f"- В туалете {self.settings.toilet_t}\n"
            msg += f"- У фильтров {self.settings.basement_t}\n"
            msg += f"- У гаражной двери {self.settings.basement_door_t}\n\n"
            msg += "Бильярдная:\n"
            msg += f"- Температура в бильярдной {self.get_state(self.settings.billyard_t)}\n\n"
            msg += "Температуры жидкостей:\n"
            msg += f"- Температура антирфиза текущая: {self.settings.antifreeze_t}\n"
            msg += f"- Температура масла текущая: {self.settings.oil_t}\n\n"
            msg += "Целевые значения на котле и асиках:\n"
            msg += f"- Температура на асиках: {self.settings.asics_base_current_temp}\n"
            msg += f"- Температура на котле: {self.settings.heater_current_temp}\n\n"
            msg += "Текущая мощность на асиках:\n"
            msg += f"- Текущая мощность на асиках фаза 1: {self.get_state('sensor.sonoff_pow_2_energy_power')} Вт-ч\n"
            msg += f"- Текущая мощность на асиках фаза 2: {self.get_state('sensor.sonoff_pow_3_energy_power')} Вт-ч\n"
            msg += f"- Текущая мощность на асиках фаза 3: {self.get_state('sensor.sonoff_pow_4_energy_power')} Вт-ч\n\n"
            msg += "Потребленное электричество:\n"
            msg += f"-  Котел потребил электричества сегодня {self.get_state('sensor.heater_power_consum_today')} КВт-ч\n"
            msg += f"-  Бойлер потребил электричества сегодня {self.get_state('sensor.sonoff_pow_1_energy_today')} КВт-ч\n"
            msg += f"-  Асики-1 потребили электричества сегодня {self.get_state('sensor.sonoff_pow_2_energy_today')} КВт-ч\n"
            msg += f"-  Асики-2 потребили электричества сегодня {self.get_state('sensor.sonoff_pow_3_energy_today')} КВт-ч\n"
            msg += f"-  Асики-3 потребили электричества сегодня {self.get_state('sensor.sonoff_pow_4_energy_today')} КВт-ч"
            self.call_service('telegram_bot/send_message',
                              title='*Меню отчетов*',
                              target=user_id,
                              message=msg,
                              disable_notification=True,
                              inline_keyboard=None)    

########################## Потребление электричества ####################################
        elif payload_event['command'] == '/consumption':
            msg = f"Время: {datetime.datetime.today().strftime(format='%Y-%m-%d %H:%M')}\n"
            msg += "- В этом месяце потребление:\n"
            msg += f"--  Нагревательный котел: {self.get_state('sensor.heater_power_consum')} кВт-ч\n"
            msg += f"--  Бак горячей воды: {round(float(self.get_state('sensor.boiler_monthly')),2)} кВт-ч\n"
            msg += f"--  Асик фаза 1: {round(float(self.get_state('sensor.asics1_monthly')),2)} кВт-ч\n"
            msg += f"--  Асик фаза 2: {round(float(self.get_state('sensor.asics2_monthly')),2)} кВт-ч\n"
            msg += f"--  Асик фаза 3: {round(float(self.get_state('sensor.asics3_monthly')),2)} кВт-ч\n"
            msg += f"--  Асики всего: {round(float(self.get_state('sensor.asics1_monthly')) + float(self.get_state('sensor.asics2_monthly')) + float(self.get_state('sensor.asics3_monthly')),2)} кВт-ч\n\n"
            msg += "- В прошлом месяце потребление:\n"
            msg += f"--  Нагревательный котел: {self.get_state('sensor.heater_power_consum_ago')} кВт-ч\n"
            #msg += f"--  Бак горячей воды: {round(float(self.get_state('sensor.boiler_monthly')),2)} кВт-ч\n"
            msg += f"--  Асик фаза 1: {round(float(self.get_state('sensor.asics1_monthly_ago')),2)} кВт-ч\n"
            msg += f"--  Асик фаза 2: {round(float(self.get_state('sensor.asics2_monthly_ago')),2)} кВт-ч\n"
            msg += f"--  Асик фаза 3: {round(float(self.get_state('sensor.asics3_monthly_ago')),2)} кВт-ч\n"
            msg += f"--  Асики всего: {round(float(self.get_state('sensor.asics1_monthly_ago')) + float(self.get_state('sensor.asics2_monthly_ago')) + float(self.get_state('sensor.asics3_monthly_ago')),2)} кВт-ч"
            self.call_service('telegram_bot/send_message',
                              title='*Отчет о потреблении*',
                              target=user_id,
                              message=msg,
                              disable_notification=True,
                              inline_keyboard=None)    



########################### Управление водой ############################################

        elif payload_event['command'] == '/water':
            if str(self.get_state('switch.sonoff_pow_1')).lower() == 'on':
                msg_hot_water = 'включен'
            else:
                msg_hot_water = 'выключен'
            if str(self.get_state('switch.sonoff_th16_1')).lower() == 'on':
                msg_pump = 'включен'
            else:
                msg_pump = 'выключен'
            keyboard = [[("Вкл нагреватель", "/boiler_on"),
                         ("Выкл нагреватель","/boiler_off")],
                         [("Вкл насос", "/pump_on")
                         ,("Выкл насос","/pump_off")]]
            
            msg = f"Нагреватель воды {msg_hot_water}\n"
            msg += f"Водяной насос {msg_pump}"
            self.call_service('telegram_bot/send_message',
                              title='*Меню нагревателя воды*',
                              target=user_id,
                              message=msg,
                              disable_notification=True,
                              inline_keyboard=keyboard
                              )    



###################### Включение и управление котлом нагрева ###########################
    
    
        elif payload_event['command'] == '/heater':
            if self.get_state('input_boolean.thermostat_to_use') == 'off':
                thermostat = 'climate.heater_thermostat'
                mode = 'Работа по комнатному датчику'
            else:
                thermostat = 'climate.heater_preserve_antifreeze'
                mode = 'Работа по температуре антифриза'
            if args == []:
                if self.get_state('input_boolean.thermostat_to_use') == 'off':
                    thermostat = 'climate.heater_thermostat'
                    mode = 'Работа по комнатному датчику'
                else:
                    thermostat = 'climate.heater_preserve_antifreeze'
                    mode = 'Работа по температуре антифриза'
                keyboard = [[('Изменить режим', '/heater_regime')]]
                msg = f"Для установки температуры наберите /heater [[значение желаемой температуры]]\n\n"
                msg += "Состояние:\n"
                msg += f"- Режим: {mode}\n"
                msg += f"- Состояние котла: {self.get_state(thermostat, attribute='hvac_action')}\n"
                msg += f"- Температура антифриза целевая: {self.get_state('climate.heater_preserve_antifreeze', attribute='temperature')}\n"
                msg += f"- Температура антирфиза текущая: {self.settings.antifreeze_t}\n"
                msg += f"- Температура в комнате целевая: {self.settings.heater_current_temp}\n"
                msg += f"- Температура в комнате текущая: {self.settings.living_room_t}\n"
                self.call_service('telegram_bot/send_message',
                              title='*Меню котла*',
                              target=user_id,
                              message=msg,
                              disable_notification=True,
                              inline_keyboard=keyboard
                              )     
            else:
                self.call_service('climate/set_temperature', 
                                    entity_id = 'climate.heater_thermostat',
                                    temperature = args[0])
                keyboard = [[('Изменить режим', '/heater_regime')]]
                self.call_service('telegram_bot/send_message',
                                  target=user_id,
                                  message=f'Значение целевой температуры успешно изменено на {args[0]}',
                                  disable_notification=True,
                                  inline_keyboard=keyboard
                                  )          

############################ АСИКИ ###########################################
        elif payload_event['command'] == '/asics':
            keyboard = [[('Фаза 1', '/asics_phase1_switch'),
                         ('Фаза 2', '/asics_phase2_switch'),
                         ('Фаза 3', '/asics_phase3_switch')
                        ],
                        [('Переключить масляный насос', '/asics_pump')]
                        ]
            asics = self.get_app("asics_lib")
            
            if args == []:
                miners_status = asics.get_all_miners_status()
             
                msg = f"Потребление Фазы 1: {self.get_state('sensor.sonoff_pow_2_energy_power')} Вт-ч\n"
                msg += f"Потребление Фазы 2: {self.get_state('sensor.sonoff_pow_3_energy_power')} Вт-ч\n"
                msg += f"Потребление Фазы 3: {self.get_state('sensor.sonoff_pow_4_energy_power')} Вт-ч\n"
                msg += f"Масляный насос: {self.get_state(self.settings.oil_pump_switch)}\n"
                msg += f"Целевая температура в комнате: {self.settings.asics_base_current_temp} C\n"
                msg += f"Текущая температура в комнате: {self.settings.living_room_t} C\n"
                msg += f"Максимальная температура масла: {self.get_state('climate.asics_thermostat_support', attribute='temperature')} C\n"
                msg += f"Текущая температура масла: {self.settings.oil_t} C\n\n"
                for key in miners_status.keys():
                    msg += f"Asic-{key}: Hash - {miners_status[key]['hash_rate']}, Blades - {miners_status[key]['blades']}\n"
                    msg += f"Chip T - {miners_status[key]['chip_t']}, Board T - {miners_status[key]['board_t']}\n"
                    
                
                self.call_service('telegram_bot/send_message',
                                      title='*Меню Асиков*',
                                      target=user_id,
                                      message=msg,
                                      disable_notification=True,
                                      inline_keyboard=keyboard)   
            
            elif args[0] == 's':
                if len(args) == 2:
                    miner_status = asics.get_miner_status(args[1])
                    msg = f"Asic-{args[1]}: Hash - {miner_status['hash_rate']}, Blades - {miner_status['blades']}\n"
                    msg += f"Chip T - {miner_status['chip_t']}, Board T - {miner_status['board_t']}\n"
                    for i in range (6,9):
                        msg += f"Board {i} - {miner_status[f'chips_{i}']} good chips\n"
                
                    self.call_service('telegram_bot/send_message',
                                      title='*Меню Асиков*',
                                      target=user_id,
                                      message=msg,
                                      disable_notification=True,
                                      inline_keyboard=keyboard)   
                    
            
            elif args[0] == 'k':
                if len(args) == 2:
                    
                    chip_stats = asics.get_kernel_log(int(args[1]))
                    msg = f"Состояние чипов Асик-{args[1]}\n\n"
                    
                    for i, blade_key in enumerate(chip_stats.keys()):
                        msg += f"Лезвие {i+1}: \n"
                        msg += f"Зеленые: {chip_stats[blade_key]['green']}\n"
                        msg += f"Оранжевые: {chip_stats[blade_key]['orange']}\n"
                        msg += f"Красные: {chip_stats[blade_key]['red']}\n\n"
                    self.call_service('telegram_bot/send_message',
                                       message=msg,
                                       target=user_id,)      
                    
                
            elif args[0] == 'r':
                if len(args) > 1:
                    if asics.reboot_miner(int(args[1])) == 1:
                        msg = f'Асик {args[1]} успешно перезагружен' + '\n'
                    else:
                        msg = f'Асик {args[1]} не был перезагружен' + '\n' 
                    
                    self.call_service('telegram_bot/send_message',
                               message=msg,
                               target=user_id)      
                           
                    
            elif args[0] == 'p':
                if len(args) >=3:
                    freq = int(args[2])
                    autodownscale = 'false'
                    if len(args) == 4:
                        autodownscale = args[3]
                    if asics.change_power(int(args[1]), freq, autodownscale) == 1:
                        msg = f'Асик {args[1]} успешно изменил мощность на {args[2]} Мгц' + '\n'
                    else:
                        msg = f'Асик {args[1]} не изменил мощность из-за ошибки' + '\n'  
                    self.call_service('telegram_bot/send_message',
                           message=msg,
                           target=user_id,
                           )                  
                   
            
            else:
                self.call_service('climate/set_temperature', 
                                    entity_id = 'climate.asics_thermostat_temp',
                                    temperature = args[0])
                self.call_service('telegram_bot/send_message',
                               message=f'Значение целевой температуры успешно изменено на {args[0]}',
                               target=user_id,
                               )
                
            

############################ Системное меню ###################################
 
        elif payload_event['command'] == '/system':
            keyboard = [[('Перезагрузка', '/reset_system')]]
            message = "Системное меню\n"
            message += f"Свободно HDD: {self.get_state('sensor.disk_free')} Gb\n"
            message += f"Свободно ОЗУ: {self.get_state('sensor.memory_free')} Mb\n"
            message += f"IP: {self.get_state('sensor.ipv4_address_wlan0')}\n"
            message += f"Последняя загурзка: {self.get_state('sensor.last_boot').split('+')[0].replace('T',' ')}\n"
            self.call_service('telegram_bot/send_message',
                              title='*Меню отчетов*',
                              target=user_id,
                              message=message,
                              disable_notification=True,
                              inline_keyboard=keyboard)   

###### КОЛЛБЭКИ!!!!!!!!! 
        
        
    def receive_telegram_callback(self, event_id, payload_event, *args):
        """Event listener for Telegram callback queries."""
        assert event_id == 'telegram_callback'
        data_callback = payload_event['data']
        callback_id = payload_event['id']
        chat_id = payload_event['chat_id']
        user_id = payload_event['user_id']
        # keyboard = ["Edit message:/edit_msg, Don't:/do_nothing",
        #             "Remove this button:/remove button"]


 
######################################### КНОПКИ НАГРЕВАТЕЛЯ   ##########################################
        if data_callback == '/boiler_on':  # Only Answer to callback query
            msg = ['Нагреватель воды включен успешно', 'Нагреватель воды не включился']
            keyboard = [[("Вкл нагреватель", "/boiler_on"),("Выкл нагреватель","/boiler_off")],
                         [("Вкл насос", "/pump_on"),("Выкл насос","/pump_off")]] 
            self.switch_on_off('switch/turn_on',self.settings.boiler_switch, user_id, msg, 'on', keyboard=keyboard)
            
                              
        elif data_callback == '/boiler_off':  # Only Answer to callback query
            msg = ['Нагреватель воды выключен успешно', 'Нагреватель воды не выключился']
            keyboard = [[("Вкл нагреватель", "/boiler_on"),("Выкл нагреватель","/boiler_off")],
                         [("Вкл насос", "/pump_on"),("Выкл насос","/pump_off")]]
            self.switch_on_off('switch/turn_off',self.settings.boiler_switch, user_id, msg, 'off', keyboard=keyboard)
            

####################################### КНОПКИ НАСОСА ВОДЫ ##############################################                              
        elif data_callback == '/pump_on':
            msg = ['Водяной насос включен успешно', 'Водяной насос не включился']
            keyboard = [[("Вкл нагреватель", "/boiler_on"),("Выкл нагреватель","/boiler_off")],
                         [("Вкл насос", "/pump_on"),("Выкл насос","/pump_off")]] 
            self.switch_on_off('switch/turn_on',self.settings.water_pump_switch, user_id, msg, 
                                'on', keyboard=keyboard)
        
        elif data_callback == '/pump_off':
            msg = ['Водяной выключен успешно', 'Водяной насос не выключился']
            keyboard = [[("Вкл нагреватель", "/boiler_on"),("Выкл нагреватель","/boiler_off")],
                         [("Вкл насос", "/pump_on"),("Выкл насос","/pump_off")]]
            self.switch_on_off('switch/turn_off',self.settings.water_pump_switch, user_id, msg, 
                                'off', keyboard=keyboard)
        
###################################### КНОПКИ КОТЛА #########################################################
        
        
        elif data_callback == '/heater_regime':
            msg = 'Выберите режим работы котла'
            new_keyboard = [[('Работа по комнатному датчику','/heater_manual'),
                            ('Работа по температуре антифриза','/heater_auto')]]
            self.call_service('telegram_bot/answer_callback_query',
                               message=msg,
                               callback_query_id=callback_id)
                               
            self.call_service('telegram_bot/edit_replymarkup',
                              chat_id=chat_id,
                              message_id='last',
                              inline_keyboard=new_keyboard)
          
        elif data_callback == '/heater_manual':
            keyboard = [[('Изменить режим', '/heater_regime')]]
            msg = 'Для установки температуры наберите /heater [[значение желаемой температуры]]'
            self.set_state('input_boolean.thermostat_to_use', state = 'off')
            '''self.call_service('climate/turn_on',
                              entity_id = 'climate.heater_thermostat')
            self.call_service('climate/turn_off',
                              entity_id = 'climate.heater_preserve_antifreeze')'''
            self.call_service('climate/set_temperature',
                              entity_id = 'climate.heater_thermostat',
                              temperature = 4)
            self.call_service('telegram_bot/answer_callback_query',
                               message='Котел переведен в ручной режим',
                               callback_query_id=callback_id)
            self.call_service('telegram_bot/send_message',
                              target=user_id,
                              message=msg,
                              disable_notification=True,
                              inline_keyboard=keyboard
                              )
        elif data_callback == '/heater_auto':
            keyboard = [[('Изменить режим', '/heater_regime')]]
            msg = 'Для установки температуры наберите /heater [[значение желаемой температуры]]'
            self.set_state('input_boolean.thermostat_to_use', state = 'on')
            self.set_state('input_number.slider_target_temp', state = 4)
            self.call_service('climate/set_temperature',
                              entity_id = 'climate.heater_thermostat',
                              temperature = 4)
            '''self.call_service('climate/turn_off',
                              entity_id = 'climate.heater_thermostat')
            self.call_service('climate/turn_on',
                              entity_id = 'climate.heater_preserve_antifreeze')'''
            self.call_service('telegram_bot/answer_callback_query',
                               message='Котел переведен в автоматический режим',
                               callback_query_id=callback_id)
            self.call_service('telegram_bot/send_message',
                              target=user_id,
                              message=msg,
                              disable_notification=True,
                              inline_keyboard=keyboard
                              )
############# Меню асиков ######################################
        # масляная помпа
        elif data_callback == '/asics_pump':
            keyboard = [[('Фаза 1', '/asics_phase1_switch'),
                         ('Фаза 2', '/asics_phase2_switch'),
                         ('Фаза 3', '/asics_phase3_switch')
                        ],
                        [('Переключить масляный насос', '/asics_pump')]
                        ]
            if self.get_state(self.settings.oil_pump_switch) == 'on':
                msg = ['Масляный насос выключен успешно', 'Масляный насос не выключился']
                self.switch_on_off('switch/turn_off',self.settings.oil_pump_switch, user_id, msg, 
                                'off', keyboard=keyboard)
            elif self.get_state('switch.sonoff_th16_2') == 'off':
                msg = ['Масляный насос включен успешно', 'Масляный насос не включился']
                self.switch_on_off('switch/turn_on',self.settings.oil_pump_switch, user_id, msg, 
                                'on', keyboard=keyboard)
        # Фаза 1    
        elif data_callback == '/asics_phase1_switch':
            keyboard = [[('Фаза 1', '/asics_phase1_switch'),
                         ('Фаза 2', '/asics_phase2_switch'),
                         ('Фаза 3', '/asics_phase3_switch')
                        ],
                        [('Переключить масляный насос', '/asics_pump')]
                        ]
            if self.get_state(self.settings.asics_switch_1) == 'on':
                msg = ['Асики на фазе 1 выключены успешно', 'Асики на фазе 1 не выключились']
                self.switch_on_off('climate/turn_off','climate.asics_thermostat_support', user_id, msg, 
                                'off', keyboard=keyboard)
            elif self.get_state(self.settings.asics_switch_1) == 'off':
                msg = ['Асики на фазе 1 включены успешно', 'Асики на фазе 1 не включились']
                self.switch_on_off('climate/turn_on','climate.asics_thermostat_support', user_id, msg, 
                                'heat', keyboard=keyboard)
        
        # Фаза 2    
        elif data_callback == '/asics_phase2_switch':
            keyboard = [[('Фаза 1', '/asics_phase1_switch'),
                         ('Фаза 2', '/asics_phase2_switch'),
                         ('Фаза 3', '/asics_phase3_switch')
                        ],
                        [('Переключить масляный насос', '/asics_pump')]
                        ]
            if self.get_state(self.settings.asics_switch_2) == 'on':
                msg = ['Асики на фазе 2 выключены успешно', 'Асики на фазе 2 не выключились']
                self.switch_on_off('climate/turn_off','climate.asics_thermostat_main', user_id, msg, 
                                'off', keyboard=keyboard)
            elif self.get_state(self.settings.asics_switch_2) == 'off':
                msg = ['Асики на фазе 2 включены успешно', 'Асики на фазе 2 не включились']
                self.switch_on_off('climate/turn_on','climate.asics_thermostat_main', user_id, msg, 
                                'heat', keyboard=keyboard)

        #### Фаза 3    
        elif data_callback == '/asics_phase3_switch':
            keyboard = [[('Фаза 1', '/asics_phase1_switch'),
                         ('Фаза 2', '/asics_phase2_switch'),
                         ('Фаза 3', '/asics_phase3_switch')
                        ],
                        [('Переключить масляный насос', '/asics_pump')]
                        ]
            if self.get_state(self.settings.asics_switch_3) == 'on':
                msg = ['Асики на фазе 3 выключены успешно', 'Асики на фазе 3 не выключились']
                self.switch_on_off('climate/turn_off','climate.asics_thermostat_main_2', user_id, msg, 
                                'off', keyboard=keyboard)
            elif self.get_state(self.settings.asics_switch_3) == 'off':
                msg = ['Асики на фазе 3 включены успешно', 'Асики на фазе 3 не включились']
                self.switch_on_off('climate/turn_on','climate.asics_thermostat_main_2', user_id, msg, 
                                'heat', keyboard=keyboard)




############# Системное меню ####################################
        elif data_callback == '/reset_system':
            self.call_service('telegram_bot/answer_callback_query',
                               message='Перезгаружаю систему',
                               callback_query_id=callback_id)
            self.call_service('homeassistant/restart')
            #self.call_service('telegram_bot/answer_callback_query',
            #                  message='OK, you said no!',
            #                  callback_query_id=callback_id)