import os.path
import boto3
import logging as lg
from botocore.config import Config


####################################################################################
### Class AWSLink
####################################################################################
class AWSLink:

    # Static Logger
    logger = lg.getLogger('HiwiAutomation.AWS')

    ####################################################################
    ## CONSTRUCTOR #####################################################    
    def __init__(self, app_config):
        super(AWSLink, self).__init__()

        AWSLink.logger.debug("Initalizing class AWSLink. Parameters:")
        AWSLink.logger.debug(f"aws_region = [{app_config.aws_region}]")

        #member variables
        self.app_config = app_config
        self.aws_config = Config(region_name = app_config.aws_region,
                                signature_version = 'v4',
                                retries = {
                                    'max_attempts': 3,
                                    'mode': 'standard'
                                }
        )
        self.polly_client = boto3.client('polly', config = self.aws_config)        

    ####################################################################################
    ####################################################################################
    def get_mp3_for_text(self, input_text, output_mp3_path):

        # Check if file exists. If yes, abort, file was created previously
        if os.path.isfile(output_mp3_path):
            AWSLink.logger.debug(f"SKIP connection to AWS Polly for text [{input_text}]. File exists already.")
            return True

        AWSLink.logger.debug(f"Will now try to connect to AWS Polly and syntezise voice for text [{input_text}]...")
        response = None

        try:
            response = self.polly_client.synthesize_speech(
                Engine = 'neural',
                LanguageCode = 'de-DE',
                OutputFormat = 'mp3',
                Text = input_text,
                TextType = 'text',
                VoiceId = 'Vicki')    
        
        except:
            AWSLink.logger.error("Exception occurred during Web API call against AWS Polly!")
            return False
        
        AWSLink.logger.debug(f"AWS call completed with response [{response}]. Will now try to write audio file [{output_mp3_path}]...")
        
        try:
            mp3_file = open(output_mp3_path, 'wb')
            mp3_file.write(response['AudioStream'].read())
            mp3_file.close()
        except:
            AWSLink.logger.error(f"Error while writing data to mp3 file {output_mp3_path}!")
            return False

        AWSLink.logger.debug(f"OK: AWS Polly syntezise voice for text [{input_text}]...\n")
        return True

#### END class AWSLink #######    