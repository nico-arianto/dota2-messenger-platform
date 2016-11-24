from flask import request
from flask import make_response

from middleware import validate_token
import logger

LOGGER = logger.getLogger(__name__)

def initalize_routes(app):
    if app is None:
        return
    context_root = '/v1.0/webhook'
    app.add_url_rule(context_root, 'webhook_validation', webhook_validation, methods=['GET'])
    app.add_url_rule(context_root, 'webhook_callback', webhook_callback, methods=['POST'])

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

def webhook_callback():
    return
