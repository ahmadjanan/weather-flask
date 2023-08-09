from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models.users import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify(message='email, username and password are required'), 400

    if User.query.filter_by(username=username).first():
        return jsonify(message='Username already exists'), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='user registered successfully'), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(message='username and password are required'), 400

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify(message='invalid credentials'), 401


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def user_profile():
    current_user_username = get_jwt_identity()
    user = User.query.filter_by(username=current_user_username).first()
    return jsonify(email=user.email, username=current_user_username), 200
