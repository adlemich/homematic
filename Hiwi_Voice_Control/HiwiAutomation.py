#
# HIWI AUTOMATION APPLICATION
# This application uses PicoVoice to listen and recognize a key word.
# PicoVoice is also used to understand commands from voice.
# We use the AWS Polly API to syntetize text to speech for dynamic content
#
##################################################################################
import argparse
import logging as lg
from logging.handlers import RotatingFileHandler
from VoiceInputListener import *

##################################################################################
# DEFAULTS FOR APPLICATION CONFIGURATION
##################################################################################
DEF_CONF_LOG_LEVEL_CONSOLE      = lg.DEBUG
DEF_CONF_LOG_LEVEL_FILE         = lg.DEBUG

DEF_CONF_FILES_HOME_DIR         = '/home/pi/Documents/Jarvis/'
DEF_CONF_FILES_LOG_DIR          = DEF_CONF_FILES_HOME_DIR + 'log/'
DEF_CONF_FILES_LOG_FILE         = DEF_CONF_FILES_LOG_DIR + 'HiwiAutomation.log'

DEF_CONF_PICO_ACCESS_KEY        = 'XxplY/aiyMTN+9thH92DqN9QVttCKsT/S8EWUMZiugd9sbvYzfCUww=='
DEF_CONF_PICO_AUDIO_DEVICE_IDX  = 3
DEF_CONF_PICO_KEYWORD_FILE      = DEF_CONF_FILES_HOME_DIR + 'pico-voice/hey-hiwi_de_raspberry-pi_v2_0_0.ppn'
DEF_CONF_PICO_RHINO_FILE        = DEF_CONF_FILES_HOME_DIR + 'pico-voice/HiwiAutomation_de_raspberry-pi_v2_0_0.rhn'
DEF_CONF_PICO_LANG_MOD_FILE     = DEF_CONF_FILES_HOME_DIR + 'pico-voice/porcupine_params_de.pv'
DEF_CONF_PICO_RHINO_LANG_FILE   = DEF_CONF_FILES_HOME_DIR + 'pico-voice/rhino_params_de.pv'
DEF_CONF_PICO_SENSITIVITY       = 0.7
DEF_CONF_PICO_RHINO_SENSITIVITY = 0.5
DEF_CONF_PICO_RHINO_REQ_SILENCE = 'True'
DEF_CONF_PICO_LIB_FILE          = None
DEF_CONF_PICO_RHINOLIB_FILE     = None
DEF_CONF_PICO_DEBUG_AUDIO_OUT   = None  #DEF_CONF_FILES_LOG_DIR + "debug-audio.wav'

DEF_CONF_AWS_DEFAULT_REGION     = 'eu-west-1'

DEF_CONF_CCU_IP_ADDR            = "192.168.1.60"

##################################################################################
##################################################################################
def main():

    ### SETUP LOGGING ###
    logger = lg.getLogger('HiwiAutomation')
    logger.setLevel(lg.DEBUG)
    log_formatter = lg.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console channel
    log_chc = lg.StreamHandler()
    log_chc.setLevel(DEF_CONF_LOG_LEVEL_CONSOLE)
    log_chc.setFormatter(log_formatter)
    logger.addHandler(log_chc)
    # file channel
    log_chf = RotatingFileHandler(filename = DEF_CONF_FILES_LOG_FILE,
                                  mode = 'a',
                                  maxBytes = 1024 * 1024 * 5, # 5 MB
                                  backupCount = 2,
                                  encoding = 'UTF-8')
    log_chf.setLevel(DEF_CONF_LOG_LEVEL_FILE)
    log_chf.setFormatter(log_formatter)
    logger.addHandler(log_chf)

    logger.info('HiwiAutomation Application is starting. Have fun and enjoy.')

    ### PARSING ARGUMENTS AND SETTING APPLICATION CONFIGURATION ###
    parser = argparse.ArgumentParser()

    parser.add_argument('--home_dir',
        help = 'Base directory for all application files',
        default = DEF_CONF_FILES_HOME_DIR)

    parser.add_argument('--log_dir',
        help = 'Directory for logging and debug information',
        default = DEF_CONF_FILES_LOG_DIR)

    parser.add_argument('--aws_region',
        help = 'AWS Region to use for Polly calls',
        default = DEF_CONF_AWS_DEFAULT_REGION)

    parser.add_argument('--ccu_ip',
        help = 'IP address of the Homematic CCU3 for smart home actions',
        default = DEF_CONF_CCU_IP_ADDR)

    parser.add_argument('--access_key',
        help = 'AccessKey obtained from Picovoice Console (https://picovoice.ai/console/)',
        default = DEF_CONF_PICO_ACCESS_KEY)

    parser.add_argument('--keyword_path',
        help = "Absolute path to a Porcupine keyword file.",
        default = DEF_CONF_PICO_KEYWORD_FILE)

    parser.add_argument('--context_path',
        help = "Absolute path to a Rhino context file.",
        default = DEF_CONF_PICO_RHINO_FILE)

    parser.add_argument('--porcupine_library_path',
        help = "Absolute path to Porcupine's dynamic library.",
        default = DEF_CONF_PICO_LIB_FILE)

    parser.add_argument('--porcupine_model_path',
        help = "Absolute path to Porcupine's language specific model file.",
        default = DEF_CONF_PICO_LANG_MOD_FILE)

    parser.add_argument('--porcupine_sensitivity',
        help = "Sensitivity for detecting wake word. Each value should be a number within [0, 1]. A higher sensitivity " +
             "results in fewer misses at the cost of increasing the false alarm rate.",
        type = float,
        default = DEF_CONF_PICO_SENSITIVITY)

    parser.add_argument('--rhino_library_path',
        help = "Absolute path to Rhino's dynamic library.",
        default = DEF_CONF_PICO_RHINOLIB_FILE)

    parser.add_argument('--rhino_model_path',
        help = "Absolute path to Rhino's language specific model file.",
        default = DEF_CONF_PICO_RHINO_LANG_FILE)

    parser.add_argument('--rhino_sensitivity',
        help = "Inference sensitivity. It should be a number within [0, 1]. A higher sensitivity value results in fewer" +
               "misses at the cost of (potentially) increasing the erroneous inference rate.",
        type = float,
        default = DEF_CONF_PICO_RHINO_SENSITIVITY)

    parser.add_argument('--require_endpoint',
        help = "If set to `False`, Rhino does not require an endpoint (chunk of silence) before finishing inference.",
        default = DEF_CONF_PICO_RHINO_REQ_SILENCE,
        choices = ['True', 'False'])

    parser.add_argument('--audio_device_index',
        help = 'index of input audio device',
        type = int,
        default = DEF_CONF_PICO_AUDIO_DEVICE_IDX)

    parser.add_argument('--output_path',
        help = 'Absolute path to recorded audio for debugging.',
        default = DEF_CONF_PICO_DEBUG_AUDIO_OUT)

    app_args = parser.parse_args()

    
    ########################################################################
    # Log application configuration
    ########################################################################

    logger.debug('######## Application configuration dump ##########')
    logger.debug(f'# Home Directory              = [{app_args.home_dir}]')
    logger.debug(f'# Log and Debug Directory     = [{app_args.log_dir}]')    
    logger.debug(f'# AWS region for Polly        = [{app_args.aws_region}]') 
    logger.debug(f'# CCU3 IP address             = [{app_args.ccu_ip}]') 
    logger.debug(f'# Pico access key             = [{app_args.access_key}]')
    logger.debug(f'# Pico audio device index     = [{app_args.audio_device_index}]')
    logger.debug(f'# Pico keyword file           = [{app_args.keyword_path}]')
    logger.debug(f'# Pico library file           = [{app_args.porcupine_library_path}]')
    logger.debug(f'# Pico language model file    = [{app_args.porcupine_model_path}]')
    logger.debug(f'# Pico inference sensitivity  = [{app_args.porcupine_sensitivity}]')
    logger.debug(f'# Rhino context file          = [{app_args.context_path}]')
    logger.debug(f'# Rhino library file          = [{app_args.rhino_library_path}]')
    logger.debug(f'# Rhino language model file   = [{app_args.rhino_model_path}]')
    logger.debug(f'# Rhino inference sensitivity = [{app_args.rhino_sensitivity}]')
    logger.debug(f'# Rhino require silence       = [{app_args.require_endpoint}]')
    logger.debug(f'# Debug voice output file     = [{app_args.output_path}]')
    logger.debug('##################################################')

    ########################################################################
    # START LISTENING AND INFER
    ########################################################################
    voice_listener = VoiceInputListener(app_args)
    voice_listener.list_audio_devices()
    voice_listener.run()
## end def main():

############################################################################
############################################################################
if __name__ == '__main__':
    main()