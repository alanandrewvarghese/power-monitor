from flask import Flask
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()


def create_app():
    print("Creating the app!")  # This should be printed in the terminal
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration

    mysql.init_app(app)

    # Import routes inside the app context
    with app.app_context():
        from . import routes  # Ensure routes are imported here
        routes.init_routes(app)  # Initialize routes

    return app