from flask import Blueprint, request, jsonify
import json, logging
from dotenv import load_dotenv
import os

load_dotenv() #Load env variables

#Configuring a logger for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initializing webhook
webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    # WhatsApp will send a GET request to verify your webhook URL
    # They include three pieces of information as URL parameters:
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
    whatsapp_token = os.getenv('WHATSAPP_TOKEN')

    # Whatsapp API call header
    headers = {'Authorization': f'Bearer {whatsapp_token}'}

    logger.info(f"Received verification request - Mode: {mode}, Token: {token}")

    # Check if this is a valid verification request
    if mode and token and mode == 'subscribe' and token == verify_token:
        # If valid, return the challenge code WhatsApp sent us
        logger.info("Webhook verified successfully")
        return challenge
    # If invalid, return error
    else:
        logger.warning("Webhook verification failed")

    return jsonify({"success": False}), 403

@webhook_bp.route('/webhook', methods=['POST'])
def receive_message():
    # Verify WhatsApp token first, before processing any data
    whatsapp_token = os.getenv('WHATSAPP_TOKEN')
    if request.headers.get('Authorization') != f'Bearer {whatsapp_token}':
        return jsonify({"success": False, "error": "Invalid token"}), 401
    
    # Only process the data if token is valid
    data = request.get_json()
    
    # Process incoming WhatsApp message
    if data.get('object') == 'whatsapp_business_account':
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('value', {}).get('messages'):
                    messages = change['value']['messages']
                    for message in messages:
                        message_type = message.get('type')
                        if message_type == 'text':
                            text = message['text']['body']
                            sender = message['from']
                            print(f"Received text message from {sender}: {text}")
    
    return jsonify({"success": True})