import json
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, request, current_app, render_template
from werkzeug.security import generate_password_hash

from core.extensions import db
from core.helpers.handlers import response_wrapper
from core.libs.Mailer import send_email
from core.models.user import User, UserType

auth = Blueprint('auth', __name__)


@auth.route('/register/user', methods=['POST'])
def user_registration():
    """ Creation of a new user """
    data = request.get_json(silent=True)

    if data['email'] is None or data['password'] is None:
        return json.dumps({"message": "Missing arguments"}), 500

    # Check if the email already exist
    existing_email = User.query.filter_by(email=data['email']).first()
    if not existing_email:
        """ If not existing create an account """
        user = User(email=data['email'], password=generate_password_hash(data["password"]),
                    profile=UserType.CORPORATE.value)

        try:
            send_email("CronShot - Welcome", current_app.config['MAIL_DEFAULT_SENDER'], [user.email],
                       render_template('mail/welcome.html', user=user))
            db.session.add(user)
            db.session.commit()
            return response_wrapper('message', 'You are now registered ! You can log in !', 201)
        except Exception as e:
            print(e)
            current_app.logger.warn('Error sending email to {}'.format(user.email))
            return response_wrapper('message',
                                    'An issue with your email occured, contact our service : baptiste.magnette@gmail.com',
                                    400)
    else:
        current_app.logger.warn('Error already registered email {}'.format(existing_email.email))
        return response_wrapper('message', 'An account is already registered with this email !', 400)


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)

    if not auth or not data["username"] or not data["password"]:
        current_app.logger.info('Login {} - Il manque des informations'.format(data["username"]))
        return response_wrapper('message', 'Il manque des informations pour bien traiter la demande.', 405)

    user = User.query.filter_by(email=data["username"]).first()
    if not user:
        current_app.logger.info('Login {} - Identifiants incorrects'.format(data["username"]))
        return response_wrapper('message', 'Les identifiants saisis sont incorrects ! ', 401)

    if user.check_password(data["password"]):
        if user.is_confirmed == 0:
            current_app.logger.info('Login {} - Compte non confirmé'.format(data["username"]))
            return response_wrapper('message', "Pour se connecter, nous vous invitons à valider votre compte !", 402)

        user.last_login = datetime.utcnow().timestamp()
        db.session.commit()

        token = jwt.encode({'id': user.id, 'exp': datetime.utcnow() + timedelta(minutes=240)},
                           current_app.config['SECRET_KEY'])

        current_app.logger.info('Login {} - Success'.format(data["username"]))
        return response_wrapper('user', {'token': token}, 200)
    current_app.logger.info('Login {} - Match incorrect'.format(data["username"]))
    return response_wrapper('message', 'Votre mot de passe ou votre email est incorrect.', 400)
