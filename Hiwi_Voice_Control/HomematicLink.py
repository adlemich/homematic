####################################################################################
#
# HIWI AUTOMATION
#
####################################################################################
####################################################################################
import requests
import xml.etree.ElementTree as xmltree
import logging as lg

####################################################################################
# Constants
####################################################################################
CCU_PROTOCOL          = "http://"
CCU_STATE_CHANGE_URL  = "/addons/xmlapi/statechange.cgi?"
CCU_STATE_CHANGE_ID   = "ise_id="
CCU_STATE_CHANGE_VAL  = "&new_value="
CCU_STATE_LIST_URL    = "/addons/xmlapi/statelist.cgi?"
CCU_STATE_DEVICE_URL  = "/addons/xmlapi/state.cgi?"
CCU_STATE_DEVICE_ID   = "device_id="
CCU_STATE_DP_ID       = "&datapoint_id="  
CCU_PROG_RUN_URL      = "/addons/xmlapi/runprogram.cgi?"
CCU_PROG_RUN_ID       = "program_id="
CCU_STATUS_CODE_OK    = 200

CCU_DEVICE_ID_GARDENWAYLIGHTS     = "8177"
CCU_DEVICE_ID_GARDENDOOR_BUZ      = "8171"
CCU_DEVICE_ID_GARDEN_GARAGE_POWER = "8183"
CCU_DEVICE_ID_GARDEN_BRIGHTN_VAL  = "6526"
CCU_DEVICE_ID_GARDEN_MOTION_DETEC = "6528"
CCU_DEVICE_ID_GARDEN_WATERING_AUTO= "9410"
CCU_DEVICE_ID_POOL_FILTER_PUMP    = "9197"
CCU_DEVICE_ID_POOL_HEATING        = "9258"
CCU_DEVICE_ID_GROUND_WATER_PUMP   = "7293"
CCU_DEVICE_ID_IT_CABINET          = "8789"

CCU_PROG_ID_LEAVE_HOME            = "4057" ##Alarm on
CCU_PROG_ID_ENTER_HOME            = "4073" ##Alarm off

CCU_DEVICE_ID_TEMP_SENS           = "9123"
CCU_DEVICE_ID_OUTSIDE_TEMP_VAL    = "9150"
CCU_DEVICE_ID_OUTSIDE_HUMID_VAL   = "9152"

####################################################################################
### Class HomematicLink
####################################################################################
class HomematicLink:

    # Static Logger
    logger = lg.getLogger('HiwiAutomation.CCU')

    ####################################################################
    ## CONSTRUCTOR #####################################################    
    def __init__(self, app_config):
        super(HomematicLink, self).__init__()

        HomematicLink.logger.debug("Initalizing class HomematicLink. Parameters:")
        HomematicLink.logger.debug(f"ccu_ip = [{app_config.ccu_ip}]")

        #member variables        
        self.ccu_ip_addr = app_config.ccu_ip
        self.list_low_bat_devices = list()
        self.list_open_windows = list()
        self.voice_out_txt = ""

    ####################################################################################
    ####################################################################################
    def refresh_ccu_state(self):
        HomematicLink.logger.debug("Will now get full status update from CCU for parsing")

        get_uri = CCU_PROTOCOL + self.ccu_ip_addr + CCU_STATE_LIST_URL

        HomematicLink.logger.debug(f"Running http against CCU: {get_uri} ")
        try:
            http_req = requests.get(get_uri)
        except requests.exceptions.RequestException as e:  
            HomematicLink.logger.error(f"Exception occurred during HTTP request against CCU [{get_uri}]: {e}")
            return False

        HomematicLink.logger.debug(f"HTTP Status code = {http_req.status_code}")
        if http_req.status_code == CCU_STATUS_CODE_OK:
                ## Request ok, now parse results into member variables
                self.parse_ccu_state(http_req.content)
                return True
        else:
                HomematicLink.logger.error(f"Running http against CCU [{get_uri}] resulted in error HTTP Status code [{http_req.status_code}]")
                return False
    
    ####################################################################################
    ####################################################################################
    def parse_ccu_state(self, ccu_data):
        HomematicLink.logger.debug("Start parsing CCU status data...")
        self.list_low_bat_devices.clear()

        xml_root = xmltree.fromstring(ccu_data)
        for ccu_device in xml_root.iter('device'):
            is_window = False

            for device_channel in ccu_device.iter('channel'):

                if device_channel.attrib["name"].find('_Sensor') > 0:
                    # This seems to be a window/door sensor
                    is_window = True

                for channel_dp in device_channel.iter('datapoint'):
                    if channel_dp.attrib['type'] == 'LOWBAT':
                        if channel_dp.attrib['value'] == 'true':
                            # HERE IS A LOW BATTERY!!
                            self.list_low_bat_devices.append(ccu_device.attrib["name"])

                    if channel_dp.attrib['type'] == 'STATE' and is_window == True:
                        if channel_dp.attrib['value'] == 'true':
                            # HERE IS A OPEN WINDOW!!
                            self.list_open_windows.append(ccu_device.attrib["name"])
        
        # Erase duplicates from lists
        self.list_low_bat_devices = list(dict.fromkeys(self.list_low_bat_devices))
        self.list_open_windows = list(dict.fromkeys(self.list_open_windows))

        HomematicLink.logger.debug(f"Found {len(self.list_low_bat_devices)} entries with low battery: {self.list_low_bat_devices}")
        HomematicLink.logger.debug(f"Found {len(self.list_open_windows)} windows open: {self.list_open_windows}")
        
        return True

    ####################################################################################
    ####################################################################################
    def action_garden_waylights_on(self):
        HomematicLink.logger.debug("ACTION HANDLER: action_garden_waylights_on")
        
        device_state_id = CCU_DEVICE_ID_GARDENWAYLIGHTS
        new_value = "true"
        get_uri = CCU_PROTOCOL + self.ccu_ip_addr + CCU_STATE_CHANGE_URL + CCU_STATE_CHANGE_ID + device_state_id + CCU_STATE_CHANGE_VAL + new_value

        HomematicLink.logger.debug(f"Running http against CCU: {get_uri} ")
        try:
            http_req = requests.get(get_uri)
        except requests.exceptions.RequestException as e:  
            HomematicLink.logger.error(f"Exception occurred during HTTP request against CCU [{get_uri}]: {e}")
            return False

        HomematicLink.logger.debug(f"HTTP Status code = {http_req.status_code}")
        if http_req.status_code == CCU_STATUS_CODE_OK:
                return True
        else:
                HomematicLink.logger.error(f"Running http against CCU [{get_uri}] resulted in error HTTP Status code [{http_req.status_code}]")
                return False

    ####################################################################################
    ####################################################################################
    def action_garden_waylights_off(self):
        HomematicLink.logger.debug("ACTION HANDLER: action_garden_waylights_off")
        device_state_id = CCU_DEVICE_ID_GARDENWAYLIGHTS
        new_value = "false"
        get_uri = CCU_PROTOCOL + self.ccu_ip_addr + CCU_STATE_CHANGE_URL + CCU_STATE_CHANGE_ID + device_state_id + CCU_STATE_CHANGE_VAL + new_value

        HomematicLink.logger.debug(f"Running http against CCU: {get_uri} ")
        try:
            http_req = requests.get(get_uri)
        except requests.exceptions.RequestException as e:  
            HomematicLink.logger.error(f"Exception occurred during HTTP request against CCU [{get_uri}]: {e}")
            return False

        HomematicLink.logger.debug(f"HTTP Status code = {http_req.status_code}")
        if http_req.status_code == CCU_STATUS_CODE_OK:
                return True
        else:
                HomematicLink.logger.error(f"Running http against CCU [{get_uri}] resulted in error HTTP Status code [{http_req.status_code}]")
                return False

    ####################################################################################
    ####################################################################################
    def action_status_batteries(self):
        HomematicLink.logger.debug("ACTION HANDLER: action_status_batteries")
        if self.refresh_ccu_state() == False:
            return False

        voice_out_txt = ""
        nun_dev = len(self.list_low_bat_devices)

        if nun_dev < 1:
            voice_out_txt = "Alle Batterien OK"
        elif nun_dev == 1:
            voice_out_txt = f"Es ist eine Batterie leer, Gerät, {self.list_low_bat_devices[0]}"
        elif nun_dev > 1:
            voice_out_txt = f"Es sind {nun_dev} Batterien leer, Geräte "
            for device_name in self.list_low_bat_devices:
                voice_out_txt += ", " + device_name
            
        HomematicLink.logger.debug(f"Generated output for voice: {voice_out_txt}")
        self.voice_out_txt = voice_out_txt
        return True

    ####################################################################################
    ####################################################################################
    def action_status_windows(self):
        HomematicLink.logger.debug("ACTION HANDLER: action_status_windows")
        if self.refresh_ccu_state() == False:
            return False

        voice_out_txt = ""
        nun_dev = len(self.list_open_windows)

        if nun_dev < 1:
            voice_out_txt = "Alle Fenster sind zu"
        elif nun_dev == 1:
            voice_out_txt = f"Es ist ein Fenster offen, {self.list_open_windows[0]}"
        elif nun_dev > 1:
            voice_out_txt = f"Es sind {nun_dev} Fenster offen, "
            for window_name in self.list_open_windows:
                voice_out_txt += ", " + window_name
            
        HomematicLink.logger.debug(f"Generated output for voice: {voice_out_txt}")
        self.voice_out_txt = voice_out_txt
        return True

    ####################################################################################
    ####################################################################################
    def action_garden_door_summer(self):
        HomematicLink.logger.debug("ACTION HANDLER: action_garden_door_summer")

        device_state_id = CCU_DEVICE_ID_GARDENDOOR_BUZ
        new_value = "true"
        get_uri = CCU_PROTOCOL + self.ccu_ip_addr + CCU_STATE_CHANGE_URL + CCU_STATE_CHANGE_ID + device_state_id + CCU_STATE_CHANGE_VAL + new_value

        HomematicLink.logger.debug(f"Running http against CCU: {get_uri} ")
        try:
            http_req = requests.get(get_uri)
        except requests.exceptions.RequestException as e:  
            HomematicLink.logger.error(f"Exception occurred during HTTP request against CCU [{get_uri}]: {e}")
            return False

        HomematicLink.logger.debug(f"HTTP Status code = {http_req.status_code}")
        if http_req.status_code == CCU_STATUS_CODE_OK:
                return True
        else:
                HomematicLink.logger.error(f"Running http against CCU [{get_uri}] resulted in error HTTP Status code [{http_req.status_code}]")
                return False

    ####################################################################################
    ####################################################################################
    def action_alarm_sys_on(self):
        HomematicLink.logger.debug("ACTION HANDLER: action_alarm_sys_on")

        get_uri = CCU_PROTOCOL + self.ccu_ip_addr + CCU_PROG_RUN_URL + CCU_PROG_RUN_ID + CCU_PROG_ID_LEAVE_HOME

        HomematicLink.logger.debug(f"Running http against CCU: {get_uri} ")
        try:
            http_req = requests.get(get_uri)
        except requests.exceptions.RequestException as e:  
            HomematicLink.logger.error(f"Exception occurred during HTTP request against CCU [{get_uri}]: {e}")
            return False

        HomematicLink.logger.debug(f"HTTP Status code = {http_req.status_code}")
        if http_req.status_code == CCU_STATUS_CODE_OK:
                return True
        else:
                HomematicLink.logger.error(f"Running http against CCU [{get_uri}] resulted in error HTTP Status code [{http_req.status_code}]")
                return False

    ####################################################################################
    ####################################################################################
    def action_alarm_sys_off(self):
        HomematicLink.logger.debug("ACTION HANDLER: action_alarm_sys_off")

        get_uri = CCU_PROTOCOL + self.ccu_ip_addr + CCU_PROG_RUN_URL + CCU_PROG_RUN_ID + CCU_PROG_ID_ENTER_HOME

        HomematicLink.logger.debug(f"Running http against CCU: {get_uri} ")
        try:
            http_req = requests.get(get_uri)
        except requests.exceptions.RequestException as e:  
            HomematicLink.logger.error(f"Exception occurred during HTTP request against CCU [{get_uri}]: {e}")
            return False

        HomematicLink.logger.debug(f"HTTP Status code = {http_req.status_code}")
        if http_req.status_code == CCU_STATUS_CODE_OK:
                return True
        else:
                HomematicLink.logger.error(f"Running http against CCU [{get_uri}] resulted in error HTTP Status code [{http_req.status_code}]")
                return False
        
    ####################################################################################
    ####################################################################################
    def action_status_outside_temp(self):
        HomematicLink.logger.debug("ACTION HANDLER: action_status_outside_temp")

        get_uri = CCU_PROTOCOL + self.ccu_ip_addr + CCU_STATE_DEVICE_URL + CCU_STATE_DEVICE_ID + CCU_DEVICE_ID_TEMP_SENS + CCU_STATE_DP_ID + CCU_DEVICE_ID_OUTSIDE_TEMP_VAL

        HomematicLink.logger.debug(f"Running http against CCU: {get_uri} ")
        try:
            http_req = requests.get(get_uri)
        except requests.exceptions.RequestException as e:  
            HomematicLink.logger.error(f"Exception occurred during HTTP request against CCU [{get_uri}]: {e}")
            return False

        HomematicLink.logger.debug(f"HTTP Status code = {http_req.status_code}")
        if http_req.status_code == CCU_STATUS_CODE_OK:

                xml_root = xmltree.fromstring(http_req.content)
                for ccu_state in xml_root.iter('state'):
                    for ccu_dp in ccu_state.iter('datapoint'):
                        temp_val = float(ccu_dp.attrib['value'])
                        self.voice_out_txt = "Draussen sind es {:.1f} Grad".format(temp_val)
                        HomematicLink.logger.debug(f"Generated output for voice: {self.voice_out_txt}")        
                        return True

                HomematicLink.logger.error(f"Running http against CCU [{get_uri}]  ok, but did not find Temp Value in response [{http_req.content}]")
        else:
                HomematicLink.logger.error(f"Running http against CCU [{get_uri}] resulted in error HTTP Status code [{http_req.status_code}]")

        return False
    ####################################################################################
    ####################################################################################
    def action_set_room_temp(self, slot_vars):
        HomematicLink.logger.debug(f"ACTION HANDLER: action_set_room_temp. Slot variables are: {slot_vars} ")

        return False




