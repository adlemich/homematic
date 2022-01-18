####################################################################################
#
# HIWI AUTOMATION
#
####################################################################################
####################################################################################
import pygame
import random
import locale
import logging as lg
from datetime import datetime

from HomematicLink import *
from AWSLink import *

####################################################################################
# Constants
####################################################################################
JOB_TYPE_WAKEWORD   = 0
JOB_TYPE_INTENT_OK  = 1
JOB_TYPE_INTENT_NOK = 2

INTENT_GARDEN_WAY_ON  = "WegLichtAn"
INTENT_GARDEN_WAY_OFF = "WegLichtAus"
INTENT_STATUS_WINDOWS = "StatusFenster"
INTENT_STATUS_BATTS   = "StatusBatterien"
INTENT_GARDEN_DOOR_S  = "GartentuerSummer"
INTENT_ALARM_SYS_ON   = "AlarmAnlageAn"
INTENT_ALARM_SYS_OFF  = "AlarmAnlageAus"
INTENT_OUTSIDE_TEMP   = "AussenTemperatur"
INTENT_CURR_TIME      = "Uhrzeit"
INTENT_CURR_DATE      = "Datum"
INTENT_SET_ROOM_TEMP  = "RaumTemperatur"

ROOM_KITCHEN          = "Küche"
ROOM_LIVING           = "Wohnzimmer"
ROOM_DINING           = "Esszimmer"
ROOM_BATH_LOWER       = "Bad unten"
ROOM_BATH_UPPER       = "Bad oben"
ROOM_BED              = "Schlafzimmer"
ROOM_KID              = "Kinderzimmer"
ROOM_WORK_LOWER       = "Arbeitszimmer unten"
ROOM_WORK_UPPER       = "Arbeitszimmer oben"

####################################################################################
### class ActionHandler
####################################################################################
class ActionHandler:
    # Static logger
    logger = lg.getLogger('HiwiAutomation.ACH')

    ####################################################################
    ## CONSTRUCTOR #####################################################    
    def __init__(self, app_config):
        super(ActionHandler, self).__init__()

        ActionHandler.logger.debug("Initalizing class ActionHandler. Parameters:")
        ActionHandler.logger.debug(f"home_dir = [{app_config.home_dir}]")

        ### INIT
        pygame.init()
        pygame.mixer.init()
        random.seed()
        locale.setlocale(locale.LC_ALL, 'de_DE.utf8')

        ### member variables
        self.folder_dyn_mp3files  = app_config.home_dir + 'voice-output/'
        self.aws                  = AWSLink(app_config = app_config)
        self.ccu                  = HomematicLink(app_config = app_config)

        ### Static audio files
        self.audio_wake_response_list = [
            self.folder_dyn_mp3files + "WakeWord_Response_1.mp3",
            self.folder_dyn_mp3files + "WakeWord_Response_2.mp3",
            self.folder_dyn_mp3files + "WakeWord_Response_3.mp3"]

        self.audio_intentOK_response_list = [
            self.folder_dyn_mp3files + "Intent_OK_Response_1.mp3",
            self.folder_dyn_mp3files + "Intent_OK_Response_2.mp3",
            self.folder_dyn_mp3files + "Intent_OK_Response_3.mp3"]

        self.audio_intentNOK_response_list = [
            self.folder_dyn_mp3files + "Intent_NOK_Response_1.mp3",
            self.folder_dyn_mp3files + "Intent_NOK_Response_2.mp3",
            self.folder_dyn_mp3files + "Intent_NOK_Response_3.mp3"]
        
        self.audio_done_response_list = [
            self.folder_dyn_mp3files + "Done_1.mp3",
            self.folder_dyn_mp3files + "Done_2.mp3",
            self.folder_dyn_mp3files + "Done_3.mp3"]
        
        self.audio_error_response_list = [
            self.folder_dyn_mp3files + "Error_1.mp3",
            self.folder_dyn_mp3files + "Error_2.mp3",
            self.folder_dyn_mp3files + "Error_3.mp3"]

    ### end def __init__(self, app_config)        

    ####################################################################################
    ####################################################################################
    def wake_word_action(self):
        ActionHandler.logger.debug('-- WAKE WORD ACTION -- Playing wake response audio... ')
        self.play_voice(self.audio_wake_response_list[random.randint(0, len(self.audio_wake_response_list)-1)])

    ####################################################################################
    ####################################################################################
    def intent_action(self, inference):
        if inference.is_understood:
            action_ok = False
            ActionHandler.logger.debug('-- INTENT UNDERSTOOD ACTION -- Playing intent understood response audio... ')
            self.play_voice(self.audio_intentOK_response_list[random.randint(0, len(self.audio_intentOK_response_list)-1)])
            
            ## do stuff and report result    
    #                        print('{')
    #                        print("  intent : '%s'" % inference.intent)
    #                        print('  slots : {')
    #                        for slot, value in inference.slots.items():
    #                            print("    %s : '%s'" % (slot, value))
    #                        print('  }')
    #                        print('}\n')

            ############### DATE & TIME ########################
            if inference.intent == INTENT_CURR_TIME:
                ActionHandler.logger.info("INTENT_CURR_TIME")
                if self.play_curr_time() == True:
                    return True

            elif inference.intent == INTENT_CURR_DATE:
                ActionHandler.logger.info("INTENT_CURR_DATE")
                if self.play_curr_date() == True:
                    return True

            ############### HOMEMATIC ########################
            elif inference.intent == INTENT_GARDEN_WAY_ON:
                ActionHandler.logger.info("INTENT_GARDEN_WAY_ON")
                action_ok = self.ccu.action_garden_waylights_on()

            elif inference.intent == INTENT_GARDEN_WAY_OFF:
                ActionHandler.logger.info("INTENT_GARDEN_WAY_OFF")
                action_ok = self.ccu.action_garden_waylights_off()

            elif inference.intent == INTENT_STATUS_WINDOWS:
                ActionHandler.logger.info("INTENT_STATUS_WINDOWS")
                action_ok = self.ccu.action_status_windows()
                if action_ok == True:
                    mp3_name = self.folder_dyn_mp3files + self.ccu.voice_out_txt + ".mp3"
                    if self.aws.get_mp3_for_text(self.ccu.voice_out_txt, mp3_name) == True:
                        self.play_voice(mp3_name)
                        return True

            elif inference.intent == INTENT_STATUS_BATTS:
                ActionHandler.logger.info("INTENT_STATUS_BATTS")
                action_ok = self.ccu.action_status_batteries()
                if action_ok == True:
                    mp3_name = self.folder_dyn_mp3files + self.ccu.voice_out_txt + ".mp3"
                    if self.aws.get_mp3_for_text(self.ccu.voice_out_txt, mp3_name) == True:
                        self.play_voice(mp3_name)
                        return True

            elif inference.intent == INTENT_GARDEN_DOOR_S:
                ActionHandler.logger.info("INTENT_GARDEN_DOOR_S")
                action_ok = self.ccu.action_garden_door_summer()

            elif inference.intent == INTENT_ALARM_SYS_ON:
                ActionHandler.logger.info("INTENT_ALARM_SYS_ON")
                action_ok = self.ccu.action_alarm_sys_on()

            elif inference.intent == INTENT_ALARM_SYS_OFF:
                ActionHandler.logger.info("INTENT_ALARM_SYS_OFF")
                action_ok = self.ccu.action_alarm_sys_off()

            elif inference.intent == INTENT_OUTSIDE_TEMP:
                ActionHandler.logger.info("INTENT_OUTSIDE_TEMP")
                action_ok = self.ccu.action_status_outside_temp()
                if action_ok == True:
                    mp3_name = self.folder_dyn_mp3files + self.ccu.voice_out_txt + ".mp3"
                    if self.aws.get_mp3_for_text(self.ccu.voice_out_txt, mp3_name) == True:
                        self.play_voice(mp3_name)
                        return True

            elif inference.intent == INTENT_SET_ROOM_TEMP:
                ActionHandler.logger.info("INTENT_SET_ROOM_TEMP")
                action_ok = self.ccu.action_set_room_temp(inference.slots)

            ######################################################################
            ######################################################################

            else:
                ActionHandler.logger.error(f'-- INTENT UNKNOWN! Failed to process [{inference.intent}]')
                self.play_voice(self.audio_error_response_list[random.randint(0, len(self.audio_error_response_list)-1)])

            #DONE
            if action_ok:
                ActionHandler.logger.debug('-- INTENT ACTION SUCCESS -- Playing intent done response audio')
                self.play_voice(self.audio_done_response_list[random.randint(0, len(self.audio_done_response_list)-1)])
            else: 
                ActionHandler.logger.debug('-- INTENT ACTION FAILURE -- Playing intent done response audio')
                self.play_voice(self.audio_error_response_list[random.randint(0, len(self.audio_error_response_list)-1)])
        else:
            # Was not understood
            ActionHandler.logger.debug(f'-- INTENT NOT UNDERSTOOD - Playing intent not understood response audio')
            self.play_voice(self.audio_intentNOK_response_list[random.randint(0, len(self.audio_intentNOK_response_list)-1)])

    ####################################################################################
    ####################################################################################
    def play_voice(self, sound_file):
        ActionHandler.logger.debug(f'Playing sound from file [{sound_file}]')
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): 
            pygame.time.Clock().tick(10)

    ####################################################################################
    ####################################################################################
    def play_curr_time(self):
        now = datetime.now()
        voice_text = now.strftime("Es ist %H:%M Uhr")
        mp3_name = self.folder_dyn_mp3files + now.strftime("time_%H_%M.mp3")

        ActionHandler.logger.debug(f'ACTION for Intent "Current Time" compiled text [{voice_text}]. Try to get audio file from AWS Polly...')

        if self.aws.get_mp3_for_text(voice_text, mp3_name) == False:
            return False
        
        self.play_voice(mp3_name)
        return True

    ####################################################################################
    ####################################################################################
    def play_curr_date(self):
        now = datetime.now()
        voice_text = now.strftime("Heute ist der %d. %B")
        mp3_name = self.folder_dyn_mp3files + now.strftime("date_%d_%B.mp3")
        
        ActionHandler.logger.debug(f'ACTION for Intent "Current Date" compiled text [{voice_text}]. Try to get audio file from AWS Polly...')

        if self.aws.get_mp3_for_text(voice_text, mp3_name) == False:
            return False
        
        self.play_voice(mp3_name)
        return True

### END class ActionHandler   