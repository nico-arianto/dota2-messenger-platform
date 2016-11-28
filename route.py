from functools import wraps
import hmac
from flask import request
from flask import make_response

from middleware import validate_token
from middleware import received_message
import logger

import config

LOGGER = logger.getLogger(__name__)
APP_SECRET = bytes(config.facebook['APP_SECRET'], 'utf-8')

def initalize_routes(app):
    if app is None:
        return
    context_root = '/v1.0/'
    app.add_url_rule(context_root + 'webhook', 'webhook_validation', webhook_validation, methods=['GET'])
    app.add_url_rule(context_root + 'webhook', 'webhook_callback', webhook_callback, methods=['POST'])

def verify_request_signature(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        signature = request.headers.get('x-hub-signature', None)
        if signature:
            elements = signature.split('=')
            method = elements[0]
            signature_hash = elements[1]
            expected_hash = hmac.new(APP_SECRET, msg = request.get_data(), digestmod = method).hexdigest()
            if signature_hash != expected_hash:
                LOGGER.error('Signature was invalid')
                return make_response('', 403)
        else:
            LOGGER.error('Could not validate the signature')
        return func(*args, **kwargs)
    return decorated

def webhook_validation():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge', '')
    if validate_token(mode, token):
        LOGGER.info('Token was successfully validated')
        return make_response(challenge, 200)
    else:
        LOGGER.warning('Token was invalid!')
        return make_response('', 403)

@verify_request_signature
def webhook_callback():
    data = request.json
    if data['object'] == 'page':
        for page_entry in data['entry']:
            page_id = page_entry['id']
            time_of_event = page_entry['time']
            for message_event in page_entry['messaging']:
                if 'optin' in message_event:
                    LOGGER.info('Webhook received message event: option')
                elif 'message' in message_event:
                    received_message(message_event)
                elif 'delivery' in message_event:
                    LOGGER.info('Webhook received message event: delivery')
                elif 'postback' in message_event:
                    LOGGER.info('Webhook received message event: postback')
                elif 'read' in message_event:
                    LOGGER.info('Webhook received message event: read')
                elif 'account_linking' in message_event:
                    LOGGER.info('Webhook received message event: account linking')
                else:
                    LOGGER.info('Webhook received unknown message event: %s', message_event)
    return make_response('', 200)