
import os

class Config:

    BOT_TOKEN = os.environ.get('BOT_TOKEN', None)
    APP_ID = os.environ.get('APP_ID', None)
    API_HASH = os.environ.get('API_HASH', None)

    #comma seperated user id of users who are allowed to use

    DOWNLOAD_DIR = 'downloads'
