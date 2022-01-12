from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

mail = Mail()
db = SQLAlchemy()
cors = CORS()
scheduler = BackgroundScheduler()

