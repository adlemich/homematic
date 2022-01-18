#
# HIWI AUTOMATION APPLICATION
# This application uses PicoVoice to listen and recognize a key word.
# PicoVoice is also used to understand commands from voice.
# We use the AWS Polly API to syntetize text to speech for dynamic content
#
##################################################################################

import sys
import struct
import wave
import logging as lg
from os import path
from threading import Thread
from picovoice import *
from pvrecorder import PvRecorder

from ActionHandler import *

##################################################################################
# CLASS VoiceInputListener (short VIL)
# Spaws a thread for voice recording and inference
##################################################################################
class VoiceInputListener(Thread):
    
    # variables that must work in static context
    recorder    = None
    action_h    = None
    logger      = lg.getLogger('HiwiAutomation.VIL')
    

    ####################################################################
    ## CONSTRUCTOR
    ####################################################################
    def __init__(self, app_config):
        super(VoiceInputListener, self).__init__()

        VoiceInputListener.logger.debug("Initalizing class VoiceInputListener. Parameters: ")
        VoiceInputListener.logger.debug(f"audio_device_index = [{app_config.audio_device_index}]")
        VoiceInputListener.logger.debug(f"require_endpoint   = [{app_config.require_endpoint}]")
        VoiceInputListener.logger.debug(f"output_path        = [{app_config.output_path}]")

        self.app_config = app_config
        self.wav_file   = None
        self.audio_device_index = app_config.audio_device_index

        if app_config.require_endpoint.lower() == 'false':
            require_endpoint = False
        else:
            require_endpoint = True

        if app_config.output_path is not None:
            self.output_path = path.expanduser(app_config.output_path)
        else:
            self.output_path = None


        try:
            self._picovoice = Picovoice (access_key = app_config.access_key,
                                         keyword_path = app_config.keyword_path,
                                         wake_word_callback = self._wake_word_callback,
                                         context_path = app_config.context_path,
                                         inference_callback = self._inference_callback,
                                         porcupine_library_path = app_config.porcupine_library_path,
                                         porcupine_model_path = app_config.porcupine_model_path,
                                         porcupine_sensitivity = app_config.porcupine_sensitivity,
                                         rhino_library_path = app_config.rhino_library_path,
                                         rhino_model_path = app_config.rhino_model_path,
                                         rhino_sensitivity = app_config.rhino_sensitivity,
                                         require_endpoint = require_endpoint)
        
        except PicovoiceInvalidArgumentError as e:
            VoiceInputListener.logger.error("One or more arguments provided to Picovoice are invalid! Check configuration.")
            VoiceInputListener.logger.error(f"If all other arguments seem valid, ensure that '{app_config.access_key}' is a valid PicoVoice AccessKey.")
            raise e
        except PicovoiceActivationError as e:
            VoiceInputListener.logger.error("PicoVoice AccessKey activation error!")
            raise e
        except PicovoiceActivationLimitError as e:
            VoiceInputListener.logger.error(f"PicoVoice AccessKey '{app_config.access_key}' has reached it's temporary device limit!")
            raise e
        except PicovoiceActivationRefusedError as e:
            VoiceInputListener.logger.error(f"PicoVoice AccessKey '{app_config.access_key}' was refused!")
            raise e
        except PicovoiceActivationThrottledError as e:
            VoiceInputListener.logger.warning(f"PicoVoice AccessKey '{app_config.access_key}' has been throttled!")
            raise e
        except PicovoiceError as e:
            VoiceInputListener.logger.error("Failed to initialize Picovoice!")
            raise e

    ##############################################################################
    ##############################################################################
    @staticmethod
    def _wake_word_callback():
        VoiceInputListener.logger.debug('[!! Wake word recognized !!]')
        VoiceInputListener.logger.debug('Stop recording and invoke wake word action...')
        VoiceInputListener.recorder.stop()        
        VoiceInputListener.action_h.wake_word_action()
        VoiceInputListener.logger.debug('Wake word action done, restart listening...')
        VoiceInputListener.recorder.start()

    ##############################################################################
    ##############################################################################
    @staticmethod
    def _inference_callback(inference):
        VoiceInputListener.logger.debug('[!! Intent inference recognized !!]')
        VoiceInputListener.logger.debug('Stop recording and invoke intent action...')
        VoiceInputListener.recorder.stop()
        VoiceInputListener.action_h.intent_action(inference)
        VoiceInputListener.logger.debug('Intent action done, restart listening...')
        VoiceInputListener.recorder.start()

    ##############################################################################
    ## MAIN THREAD FOR LISTENING AND AUDIO PROCESSING
    ##############################################################################
    def run(self):

        try:
            # Instantiate the action handler object with config
            VoiceInputListener.action_h = ActionHandler(app_config = self.app_config)
            
            VoiceInputListener.logger.debug(f'Starting recording in main thread at device index [{self.audio_device_index}]...')
            VoiceInputListener.recorder = PvRecorder(device_index = self.audio_device_index, 
                                                     frame_length = self._picovoice.frame_length)
            VoiceInputListener.recorder.start()

            if self.output_path is not None:
                VoiceInputListener.logger.debug(f'Starting to record voice input to audio file [{self.output_path}]...')
                self.wav_file = wave.open(self.output_path, "w")
                self.wav_file.setparams((1, 2, 16000, 512, "NONE", "NONE"))
           
            VoiceInputListener.logger.info(f'Start Listening to voice input on recording device [{VoiceInputListener.recorder.selected_device}]...')

            while True:
                pcm = VoiceInputListener.recorder.read()

                if self.wav_file is not None:
                    self.wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

                self._picovoice.process(pcm)

        except KeyboardInterrupt:
            sys.stdout.write('\b' * 2)
            VoiceInputListener.logger.info('KEYBOARD INTERRUPT: Stopping voice recorder...')

        finally:
            VoiceInputListener.logger.debug('Cleaning up...')
            if VoiceInputListener.recorder is not None:
                VoiceInputListener.recorder.delete()

            if self.wav_file is not None:
                self.wav_file.close()

            self._picovoice.delete()

    ##############################################################################
    ##############################################################################
    @classmethod
    def list_audio_devices(cls):
        devices = PvRecorder.get_audio_devices()
        VoiceInputListener.logger.info('Listing available audio devices...')
        for i in range(len(devices)):
            VoiceInputListener.logger.info(f'     Index: {i}, device name: {devices[i]}')

