from flask import Flask
from .database import init_db
from .config import Config
from . import models


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    init_db(app)

    # IF NO SECRET KEY
    # RuntimeError: The session is unavailable because no secret key was set.  
    # Set the secret_key on the application to something unique and secret.
    # secret_key binds your application and your session variables
    app.secret_key = 'kazu'

    return app

app = create_app()