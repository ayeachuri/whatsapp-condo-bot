from flask import Flask
import os
from webhook_handler import webhook_bp
from db_utils import initialize_db

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(webhook_bp)
    
    @app.route('/')
    def index():
        return 'WhatsApp Condominium Bot is running!'
    
    return app

if __name__ == '__main__':
    # Initialize database if needed
    if os.getenv('INIT_DB', 'false').lower() == 'true':
        initialize_db()
    
    app = create_app()
    app.run(debug=True)