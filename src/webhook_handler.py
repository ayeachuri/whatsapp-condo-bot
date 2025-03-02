from flask import Blueprint, request, jsonify
import requests
import os
import json
import data_access as da

# Create blueprint
webhook_bp = Blueprint('webhook', __name__)

# Meta API configuration
META_API_VERSION = 'v18.0'
META_PHONE_NUMBER_ID = os.getenv('WHATSAPP_TEST_NUMBER')
META_ACCESS_TOKEN = os.getenv('WHATSAPP_TOKEN')
WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')

# Verification endpoint for WhatsApp webhook
@webhook_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            print("Webhook verified!")
            return challenge, 200
        else:
            return jsonify({"error": "Verification failed"}), 403
    
    return jsonify({"error": "Invalid request"}), 400

# Main webhook endpoint for receiving messages
@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Log incoming webhook for debugging
    print(f"Received webhook: {json.dumps(data)}")
    
    # Check if this is a WhatsApp message
    if 'object' in data and data['object'] == 'whatsapp_business_account':
        try:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        for message in change.get('value', {}).get('messages', []):
                            process_message(message, change.get('value', {}))
            
            return jsonify({"status": "success"}), 200
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "not a WhatsApp message"}), 404

def process_message(message, message_data):
    """Process incoming WhatsApp message"""
    if message.get('type') == 'text':
        # Extract message details
        phone_number = message.get('from')
        message_id = message.get('id')
        message_text = message.get('text', {}).get('body', '')
        timestamp = message.get('timestamp')
        
        # Check if user exists
        user = da.get_user_by_phone(phone_number)
        
        # Log the message
        if user:
            da.log_message(user['id'], message_text, 'incoming')
        else:
            da.log_anonymous_message(message_text, 'incoming')
        
        if user:
            # User exists, process command
            process_user_command(user, message_text, phone_number)
        else:
            # New user, start onboarding
            send_onboarding_message(phone_number)

def process_user_command(user, message_text, phone_number):
    """Process command from existing user"""
    command = message_text.lower().strip()
    
    # Check if it's a registration command for unit assignment
    if command.startswith('register ') and len(command.split()) > 1:
        unit_number = command.split()[1].upper()
        process_unit_registration(user, unit_number, phone_number)
        return
    
    # Simple command processing
    if command == 'help':
        send_message(phone_number, "Available commands:\n"
                                  "- help: Show this message\n"
                                  "- facilities: List available facilities\n"
                                  "- book <facility>: Book a facility\n"
                                  "- report issue: Report a maintenance issue\n"
                                  "- announcements: View recent announcements")
    elif command == 'facilities':
        # Query facilities from database
        facilities = da.get_all_facilities()
        if facilities:
            facility_list = "\n".join([f"- {f['name']}: {f['description'] or 'No description'}" for f in facilities])
            send_message(phone_number, f"Available facilities:\n{facility_list}")
        else:
            send_message(phone_number, "No facilities have been added yet.")
    else:
        # Default response
        send_message(phone_number, "I didn't understand that command. Type 'help' for a list of commands.")

def process_unit_registration(user, unit_number, phone_number):
    """Process unit registration command"""
    # Check if unit exists
    unit = da.get_unit_by_number(unit_number)
    
    # If unit doesn't exist, create it
    if not unit:
        unit = da.create_unit(unit_number)
        
    # Update user with unit_id
    updated_user = da.update_user(user['id'], unit_id=unit['id'])
    
    if updated_user:
        send_message(phone_number, f"Success! You've been registered to unit {unit_number}.")
    else:
        send_message(phone_number, "There was an error registering your unit. Please try again.")

def send_onboarding_message(phone_number):
    """Send onboarding message to new user"""
    message = ("Welcome to the Condominium WhatsApp Bot! 👋\n\n"
              "To get started, we need to register your unit number.\n\n"
              "Please reply with your unit number in this format: REGISTER A-123")
    
    send_message(phone_number, message)
    
    # Create a new user with the phone number
    da.create_user(phone_number)

def send_message(to, message_text):
    """Send WhatsApp message using Meta API"""
    url = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "body": message_text
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {META_ACCESS_TOKEN}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        # Get user to log message
        user = da.get_user_by_phone(to)
        
        # Log the outgoing message
        if user:
            da.log_message(user['id'], message_text, 'outgoing')
        else:
            da.log_anonymous_message(message_text, 'outgoing')
        
        print(f"Message sent. Response: {response_data}")
        return response_data
    except Exception as e:
        print(f"Error sending message: {e}")
        return None
