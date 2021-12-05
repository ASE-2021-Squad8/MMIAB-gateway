from mib import app
from flask_login import (logout_user)
from flask import abort
import requests

class MessageManager:
    MESSAGE_ENDPOINT = app.config['MESSAGE_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']


    @classmethod
    def get_received_message(cls,message_id):

        try:
            response = requests.get(cls.MESSAGE_ENDPOINT + "/" +str(message_id), timeout=cls.REQUESTS_TIMEOUT_SECONDS)                        
            json_payload = response.json()
            if response.status_code == 200:
                message = response
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return message