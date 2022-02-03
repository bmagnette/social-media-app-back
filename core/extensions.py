from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from pytz import UTC

mail = Mail()
db = SQLAlchemy(engine_options={"pool_pre_ping": True})
cors = CORS()
scheduler = BackgroundScheduler(timezone=UTC)
