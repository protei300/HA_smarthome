import appdaemon.plugins.hass.hassapi as hass
import time
import requests
import datetime,time
from requests.auth import HTTPDigestAuth
import re

#curl -H 'Authorization: Digest username="root", realm="antMiner Configuration", nonce="8308bd3ff24d2a2d815f98f7a34f9bcf", uri="/cgi-bin/get_miner_status.cgi", response="df4aee13722390f5730802a4942c3f4a", qop=auth, nc=00000191, cnonce="3de7a1474b60c649"' http://192.168.1.133/cgi-bin/get_miner_status.cgi
#Authorization: Digest username="root", realm="antMiner Configuration", nonce="c7969ae21769513ea82ee1f8da1a49ed", uri="/cgi-bin/get_miner_conf.cgi", response="44a9ced20ddbbc54f55628973429dabe", qop=auth, nc=00000004, cnonce="2c1b50c9d7bdba4d"


''' regex for kernel log:
(get RT hashrate from Chain\[\d*\]: [\(\)\w\s\-\[\]=\.]*)\n[\n|C] - initial parse
Asic\[\d{0,2}\]=\d{0,2}\.\d{0,4} - parse chips

'''



class Asics(hass.Hass):

    def initialize(self):
        
        self.LSTIME = 3
        self.BROKEN_CHIPS_COEF = 0.95
        self.BASE_IP = "192.168.1."
        
        self.settings = self.get_app("settings")
        self.asic_blades = self.settings.asic_blades
        
        self.log('Starting Asics module')
        self.run_every(self.asics_auto_restart, datetime.datetime.now(), 60*5)

   
    def change_power(self, IP, freq, autodownscale = "false"):
        auth = HTTPDigestAuth('root', self.settings.asics_pwd[IP])
        if freq in self.settings.asics_power.keys():
            voltage = self.settings.asics_power[freq]['voltage']
            profile = self.settings.asics_power[freq]['profile']
        else:
            voltage = 890
            profile = 8
        
        
        
        data = {
            "_ant_pool1url" : "stratum+tcp://eu.ss.btc.com:1800",
            "_ant_pool1user" : f"lakehouse.00{IP-130}",
            "_ant_pool1pw" : "123",
            "_ant_pool2url" : "stratum+tcp://eu.ss.btc.com:443",
            "_ant_pool2user" : f"lakehouse.00{IP-130}",
            "_ant_pool2pw" : "123",
            "_ant_pool3url" : "stratum+tcp://eu.ss.btc.com:25",
            "_ant_pool3user" : f"lakehouse.00{IP-130}",
            "_ant_pool3pw" : "123",
            "_ant_nobeeper": "false",
            "_ant_notempoverctrl": "false",
            "_ant_fan_customize_switch": "true",
            "_ant_fan_customize_value": "3",
            "_ant_freq": f"{freq}",
            "_ant_freq1": "0",
            "_ant_freq2": "0",
            "_ant_freq3": "0",
            "_ant_voltage": f"{voltage}",
            "_ant_voltage1": "0",
            "_ant_voltage2": "0",
            "_ant_voltage3": "0",
            "_ant_fan_rpm_off": "1",
            "_ant_chip_freq": "0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0",
            "_ant_autodownscale": autodownscale,
            "_ant_autodownscale_watch": "false",
            "_ant_autodownscale_watchtimer": "true",
            "_ant_autodownscale_timer": "3",
            "_ant_autodownscale_after": "60",
            "_ant_autodownscale_step": "2",
            "_ant_autodownscale_min": "400",
            "_ant_autodownscale_prec": "80",
            "_ant_autodownscale_profile": f"{profile}",
            "_ant_minhr": "3000",
            "_ant_asicboost": "true",
            "_ant_tempoff": "80",
            "_ant_altdf": "false",
            "_ant_presave": "0",
            "_ant_name": "antminer",
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}        
        http_path = f'http://{self.BASE_IP}{IP}/cgi-bin/set_miner_conf_custom.cgi'
        try: 
            result = requests.post(http_path, auth = auth, data=data, headers=headers)
            if 'ok' in result.text:
                self.log('ok')
                return 1
            else:
                self.log('not ok')
                return 0
        except Exception as e:
            self.log(f'smth wrong {e}')
            return -1
    
    def get_kernel_log(self, IP):
        
        auth = HTTPDigestAuth('root', self.settings.asics_pwd[IP])
        http_path = f'http://{self.BASE_IP}{IP}/cgi-bin/get_kernel_log.cgi'
        splitter = re.compile(r'get RT hashrate from Chain\[\d*\]: \(asic index start from \d\-\d{2}\)')
        chip_parser = re.compile(r'Asic\[\d{0,2}\]=\d{0,2}\.\d{0,4}')
        
        try: 
            result = requests.get(http_path, auth=auth)
            result = result.text
            #print(result)
            result = splitter.split(result)[1:]
            chips = {}
            for i,blade in enumerate(result):
                chips[f'blade_{i}'] = {}
                for chip in chip_parser.findall(blade):
                    chip_num, value = chip.split('=')
                    chip_num = int(re.findall('\[(\d{0,2})\]', chip_num)[0])
                    value = float(value)
                    chips[f'blade_{i}'][chip_num] = value
            
            
            
            #result_string = ''
            
            conf = self.get_miner_conf(IP)
            
            
            target_freq = []
            
            
            if int(conf['bitmain-freq1']) != 0:
                target_freq.append(int(conf['bitmain-freq1']) / 9)
            else:
                target_freq.append(int(conf['bitmain-freq']) / 9)
            if int(conf['bitmain-freq2']) != 0:
                target_freq.append(int(conf['bitmain-freq2']) / 9)
            else:
                target_freq.append(int(conf['bitmain-freq']) / 9)
            if int(conf['bitmain-freq3']) != 0:
                target_freq.append(int(conf['bitmain-freq3']) / 9)
            else:
                target_freq.append(int(conf['bitmain-freq']) / 9)
                
            
            chip_stats = {}
            for i, key in enumerate(chips.keys()):
                good_chips = 0
                bad_chips = 0
                medium_chips = 0
                
                for chip_key in chips[key].keys():
                    if chips[key][chip_key] >= 0.9*target_freq[i]:
                        good_chips += 1
                    elif chips[key][chip_key] >= 0.4*target_freq[i]:
                        medium_chips += 1
                    else:
                        bad_chips += 1
                chip_stats[key] = {
                    "green": good_chips,
                    "orange": medium_chips,
                    "red": bad_chips,
                }
            
            return chip_stats
            
            
        except Exception as e:
            self.log(f'Smth went wrong. Error - {e}')
            #self.call_service("variable/set_variable", variable = f'asic_{IP}', value=asic_hash, attributes = attributes)
            
        
    def get_miner_conf(self, IP):
        auth = HTTPDigestAuth('root', self.settings.asics_pwd[IP])
        http_path = f'http://{self.BASE_IP}{IP}/cgi-bin/get_miner_conf.cgi'
        try: 
            result = requests.get(http_path, auth=auth)
            #self.log(result)
            data = result.json()
            return data
            
            
        except Exception as e:
            self.log(f'Smth went wrong. Error - {e}')
            #self.call_service("variable/set_variable", variable = f'asic_{IP}', value=asic_hash, attributes = attributes)
            
    
    
    def get_miner_status(self, IP):
        
        #headers = {"Authorization" : 'Digest username="root", realm="antMiner Configuration", nonce="8308bd3ff24d2a2d815f98f7a34f9bcf", uri="/cgi-bin/get_miner_status.cgi", response="df4aee13722390f5730802a4942c3f4a", qop=auth, nc=00000191, cnonce="3de7a1474b60c649"' }
        auth = HTTPDigestAuth('root', self.settings.asics_pwd[int(IP)])
        http_path = f'http://{self.BASE_IP}{IP}/cgi-bin/get_miner_status.cgi'
        try: 
            result = requests.get(http_path, auth=auth)
            data = result.json()
            lstime = datetime.datetime.strptime(data['pools'][0]['lstime'], "%H:%M:%S").time()
            asic_hash = round(float(data['summary']['ghs5s']),0)
            attributes = {
                'hash_rate': asic_hash,
                'status': 'on',
                'blades': len(data['devs']),
                'lstime': lstime,
                'chips_6': 0,
                'chips_7': 0,
                'chips_8': 0,
            }
            
            max_chip_t = 0
            max_pcb_t = 0
            
            for i,blade in enumerate(data['devs']):
                if max_chip_t < int(blade['temp2']):
                    max_chip_t = int(blade['temp2'])
                if max_pcb_t < int(blade['temp']):
                    max_pcb_t = int(blade['temp'])
                attributes[f'chips_{i+6}'] = blade['chain_acs'].count('o')
                
            attributes['chip_t'] = max_chip_t
            attributes['board_t'] = max_pcb_t
            
            
            
            #self.call_service("variable/set_variable", variable = f'asic_{IP}', value=asic_hash, attributes = attributes)
            return attributes
        except Exception:
            asic_hash = 0.0
            attributes = {
                'hash_rate': asic_hash,
                'status': 'off',
                'blades': 0,
                'chip_t': 0,
                'board_t': 0,
                'chips_6': 0,
                'chips_7': 0,
                'chips_8': 0,
                'lstime': datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(),
            }
            #self.call_service("variable/set_variable", variable = f'asic_{IP}', value=asic_hash, attributes = attributes)
            return attributes
    
    def get_all_miners_status(self):
        asics_status = {}
        for key in self.settings.asic_ips.keys():
            for ip in self.settings.asic_ips[key]:
                if self.get_state(key, attribute='hvac_action') == 'heating':
                    result = self.get_miner_status(ip)
                    hash_rate = result['hash_rate']
                    attributes = result.copy()
                    attributes.pop('hash_rate')
                    attributes['lstime'] = attributes['lstime'].strftime("%H:%M:%S")
                    
                    result['climate_id'] = key
                    asics_status[ip] =result.copy()
                    
                    self.call_service("variable/set_variable", variable = f'asic_{ip}', value=hash_rate, attributes = attributes)
                else:
                    attributes = {
                        'status': 'off',
                        'blades': 0,
                        'chip_t': 0,
                        'board_t': 0,
                        'lstime': "00:00:00",
                        'chips_6': 0,
                        'chips_7': 0,
                        'chips_8': 0,
                    }
                    asics_status[ip] = {
                        "climate_id": key,
                        "hash_rate": 0,
                        "blades": 0,
                        "chip_t": 0,
                        "board_t": 0,
                        'chips_6': 0,
                        'chips_7': 0,
                        'chips_8': 0,
                        "lstime": datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(),
                    }
                    self.call_service("variable/set_variable", variable = f'asic_{ip}', value=0.0, attributes = attributes)
        return asics_status
    
    def reboot_miner(self, IP):
        #headers = {"Authorization" : 'Digest username="root", realm="antMiner Configuration", nonce="8308bd3ff24d2a2d815f98f7a34f9bcf", uri="/cgi-bin/get_miner_status.cgi", response="df4aee13722390f5730802a4942c3f4a", qop=auth, nc=00000191, cnonce="3de7a1474b60c649"' }
        #headers = {"Authorization" : 'Digest username="root", realm="antMiner Configuration", nonce="c7969ae21769513ea82ee1f8da1a49ed", uri="/cgi-bin/get_miner_status.cgi", response="d0afa2a13c1d9730630481d06cc5579f", qop=auth, nc=00000023, cnonce="2eb4475169ed68e5"' }
        auth = HTTPDigestAuth('root', self.settings.asics_pwd[IP])
        http_path = f'http://{self.BASE_IP}{IP}/cgi-bin/reboot.cgi'
        try: 
            result = requests.get(http_path, auth=auth)
            self.log(result.text)
            
            if result.text.lower() == 'reboot':
                return 1
            else:
                return 0
        except Exception:
            return -1
    

    def asics_auto_restart(self, kwargs):
        #blades_status = self.get_asics_blade_status()
        blades_status = self.get_all_miners_status()
        for key in blades_status.keys():
            self.log(f"Checking {key}")
            chips_sum = blades_status[key]['chips_6'] + blades_status[key]['chips_7'] + blades_status[key]['chips_8']
            self.log(f"Chips : {chips_sum}")
            if blades_status[key]['blades'] < self.asic_blades[key] and blades_status[key]['blades']!=0:
                self.log(f"Asic {key} has {blades_status[key]['blades']}. Rebooting")
                self.notify(f"Асик {key} видит {blades_status[key]['blades']} лезвий вместо необходимых {self.asic_blades[key]}. Перезагружаю", name = "telegram")
                self.call_service("climate/turn_off", entity_id = blades_status[key]['climate_id'])
                self.run_in(self.switch_boolean, 4*60, command = "climate/turn_on", boolean_var = blades_status[key]['climate_id'])
            elif blades_status[key]['blades']!=0 and chips_sum < self.asic_blades[key] * 63 * self.BROKEN_CHIPS_COEF:
                self.log(f"Asic {key} has {chips_sum} chips. Rebooting")
                self.notify(f"Асик {key} видит {chips_sum} чипов. Делаю ребут Асика", name = "telegram")
                self.reboot_miner(key)
            elif blades_status[key]['lstime'].minute > self.LSTIME:
                self.log(f"Asic {key}  didnt share for {blades_status[key]['lstime'].minute} minutes. Rebooting")
                self.notify(f"Асик {key} не отправлял шар {blades_status[key]['lstime'].minute} минут. Делаю ребут Асика", name = "telegram")
                self.reboot_miner(f"192.168.1.{key}")
        
    
    def switch_boolean(self, kwargs):
        self.call_service(kwargs['command'], entity_id = kwargs['boolean_var'])