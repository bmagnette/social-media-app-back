import datetime as dt
import json
import random
import string
from datetime import datetime, timedelta
from functools import partial

import jwt
import stripe
from flask import Blueprint, request, current_app, render_template
from werkzeug.security import generate_password_hash

from core.extensions import db
from core.helpers.handlers import response_wrapper, login_required, to_json
from core.libs.mailer import send_email
from core.models.Social.account_category import AccountCategory, CategoryGroup
from core.models.Stripe.Customer import Customer
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
        user = User(email=data['email'], password=generate_password_hash(data["password"]))

        try:
            send_email("Welcome on our platform !", current_app.config['MAIL_DEFAULT_SENDER'], [user.email],
                       render_template('mail/welcome.html', user=user))
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f'New account {user.email}')
            return response_wrapper('message', 'You are now registered ! You can log in !', 201)
        except Exception as e:
            current_app.logger.warn(f'Error sending email to {user.email} {e}')
            return response_wrapper('message',
                                    'An issue with your email occured, contact our service : contact@cronshot.com',
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
            return response_wrapper('message', "You need to validate your account to connect it!", 402)

        user.last_login = datetime.now(
            dt.timezone.utc)
        db.session.commit()

        token = jwt.encode({'id': user.id, 'exp': datetime.now(
            dt.timezone.utc) + timedelta(minutes=240)},
                           current_app.config['SECRET_KEY'])

        current_app.logger.info('Login {} - Success'.format(data["username"]))
        return response_wrapper('user', {'token': token, 'type': user.user_type}, 200)
    current_app.logger.info('Login {} - Match incorrect'.format(data["username"]))
    return response_wrapper('message', 'Your password or email is incorrect!', 400)


@auth.route('/user/price', methods=['GET'])
@partial(login_required)
def get_price(current_user: User):
    return response_wrapper('content', current_user.get_price(), 200)


@auth.route('/user/accounts', methods=['GET'])
@partial(login_required)
def get_accounts(current_user: User):
    return response_wrapper('content', current_user.get_accounts(), 200)


@auth.route('/user/end_free_trial', methods=['GET'])
@partial(login_required)
def get_end_free_trial(current_user: User):
    return response_wrapper('content', current_user.get_end_free_trial(), 200)


@auth.route('/user/settings', methods=['GET'])
@partial(login_required)
def get_user_data(current_user: User):
    customer = Customer.query.filter_by(user_id=current_user.id).first()

    card_info = None
    if customer:
        card_info = stripe.Customer.retrieve_source(
            customer.stripe_id,
            customer.card_id,
        )

    data = {
        "current_price": current_user.get_price(),
        "current_accounts": current_user.get_accounts(),
        "current_users": current_user.get_users(),
        "end_free_trial": current_user.get_end_free_trial(),
        "user": current_user.__dict__,
        "card": card_info
    }

    return response_wrapper('content', data, 200)


@auth.route('/user', methods=['POST'])
@partial(login_required)
def create_user(current_user: User):
    data = request.get_json(silent=True)
    if data['email'] is None:
        return json.dumps({"message": "Missing arguments"}), 500

    existing_email = User.query.filter_by(email=data['email']).first()
    if existing_email:
        return response_wrapper('message',
                                "Email already known by our services, we can't create two accounts with the same email",
                                400)
    else:
        random_password = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
        user = User(email=data['email'], password=generate_password_hash(random_password), user_type=UserType.USER,
                    admin_id=current_user.id, last_name=data["name"], sponsor_id=current_user.sponsor_id)
        db.session.add(user)
        if not data["groups"]:
            return response_wrapper('message', "Select a group", 400)

        for _id, status in data["groups"].items():
            if status["checked"]:
                group = AccountCategory.query.filter_by(id=_id).first_or_404()
                test = CategoryGroup(category_id=group.id, user_id=user.id, access_type=status["authorization"])
                db.session.add(test)
                current_app.logger.info(f'Link user N°{user.email} with category N: {group.id}')
        try:
            send_email("Welcome on our platform !", current_app.config['MAIL_DEFAULT_SENDER'], [user.email],
                       render_template('mail/welcome_user.html', user=user, password=random_password))
            db.session.commit()
            current_app.logger.info(f'New account {user.email}')
            return response_wrapper('message', 'Your new account is registered, you can log in !', 201)
        except Exception as e:
            current_app.logger.warn(f'Error sending email to {user.email} {e}')
            return response_wrapper('message',
                                    'An issue with your email occured, contact our service : contact@cronshot.com',
                                    400)


@auth.route('/users', methods=['GET'])
@partial(login_required)
def get_users(current_user: User):
    res = []
    if current_user.is_admin:
        users = User.query.filter_by(admin_id=current_user.id).all()
        for user in users:
            tmp_user = user.__dict__
            tmp_user["groups"] = []
            for group in user.categories:
                right = CategoryGroup.query.filter_by(user_id=user.id, category_id=group.id).first_or_404()
                temp_res = group.__dict__
                temp_res['right'] = right.__dict__
                tmp_user["groups"].append(temp_res)

            res.append(tmp_user)
        return response_wrapper('data', res, 200)
    else:
        response_wrapper('message', 'Only admin account should have sub accounts.', 400)


@auth.route('/user/<email>', methods=['DELETE'])
@partial(login_required)
def delete_user(current_user: User, email: str):
    if current_user.is_admin:
        user = User.query.filter_by(email=email).first_or_404()
        db.session.delete(user)
        db.session.commit()
        return response_wrapper('message', 'Account has been deleted', 200)
    else:
        response_wrapper('message', 'Only admin account can delete a user.', 400)


@auth.route('/user/<email>', methods=['PUT'])
@partial(login_required)
def edit_user(current_user: User, email: str):
    data = request.get_json()
    if current_user.is_admin:
        user = User.query.filter_by(email=email).first_or_404()
        user.last_name = data["name"]
        if email != data["oldEmail"]:
            return response_wrapper('message', "You can't modify existing email", 400)
        for _id, values in data["groups"].items():
            group = CategoryGroup.query.filter_by(user_id=user.id, category_id=int(_id)).first()
            if group:
                if values["checked"]:
                    group.access_type = values["authorization"]
                else:
                    print("SUPPRIMER L'ACCESS aux utilisateurs et non pas à l'ADMIN.")
                    db.session.delete(group)
            else:
                group = CategoryGroup(user_id=user.id, category_id=int(_id), access_type=values["authorization"])
                db.session.add(group)
        db.session.commit()
        return response_wrapper('message', 'Account has been modified', 200)
    else:
        return response_wrapper('message', 'Only admin account can edit a user.', 400)

