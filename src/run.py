from .app import create_app
import logging

logger = logging.getLogger(__name__)



#def start_ngrok():
#    # Start ngrok tunnel to expose your local server
#    http_tunnel = ngrok.connect(5000)
#    logger.info(f"Ngrok tunnel established at: {http_tunnel.public_url}")
#    return http_tunnel.public_url

app = create_app()

# Currently reconfigured for Render deployment
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)