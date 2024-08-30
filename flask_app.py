from flask import Flask, request
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.authorization_code = None
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/callback')
        def callback():
            self.authorization_code = request.args.get('code')
            logging.info(f"Authorization code received: {self.authorization_code}")
            return "Authorization successful! You can close the window."

    def start(self):
        # Using `use_reloader=False` is suitable for running Flask in a thread.
        self.app.run(port=5000, debug=True, use_reloader=False)