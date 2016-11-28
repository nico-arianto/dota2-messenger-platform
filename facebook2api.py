import requests
from requests.exceptions import HTTPError
from requests import codes

import logger

import config

LOGGER = logger.getLogger(__name__)

def _send(message_data):
    response = requests.post(config.facebook['URL'], json=message_data, params={ 'access_token': config.facebook['PAGE_ACCESS_TOKEN'] })
    if response.status_code != codes.ok:
        try:
            LOGGER.error('Failed to sent the message data to Facebook API, status: %d', response.status_code)
            LOGGER.error('Error message: %s', response.json()['error'])
        except ValueError as error:
            LOGGER.error('Failed to retrieved the error message')
        return
    body = response.json()
    recipient_id = body['recipient_id']
    message_id = body['message_id']

    if message_id:
        LOGGER.info('Successfully sent message with id %s to recipient %s', message_id, recipient_id)
    else:
        LOGGER.info('Successfully called Facebook API to recipient %s', recipient_id)

def send_text_message(recipient_id, message_text):
    message_data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text,
            'metadata': 'DOTA2_TEXT_MESSAGE'
        }
    };
    _send(message_data)

def send_generic_message(recipient_id, elements):
    message_data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': elements
                }
            },
            'metadata': 'DOTA2_GENERIC_MESSAGE'
        }
    }
    _send(message_data)
