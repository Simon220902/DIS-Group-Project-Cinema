from flask import Flask
from config import Config
import psycopg
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = psycopg.connect("dbname=cinema user=simonlykkeandersen")
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models, errors