from app import app, db
from app.models import User, Post, Like
from flask import request
from flask_request_validator import validate_params, Param, MaxLength, JSON, rules, Pattern
from flask_jwt_simple import create_jwt, get_jwt_identity, jwt_required
from werkzeug.exceptions import NotFound
import sqlalchemy
from sqlalchemy.sql import label, text
from sqlalchemy import func, Date, cast
import datetime

def is_valid_date(date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return False
    return True

def get_JWT_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

def try_later():
    return {"error": "Something wrong. Try later."}, 400

@app.route('/api/register', methods=['POST'])
@validate_params(
    Param('login', JSON, str, rules=[Pattern(r'^[a-z_0-9\-.]{5,64}$')]),
    Param('password', JSON, str, rules=[Pattern(r'^[a-z_0-9\-.!$&]{5,15}$')])
)
def register(login, password):
    if User.query.filter_by(login=login).first():
        #To prevent iterating over existing values
        return try_later()
    user = User(login=login)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as err:
        return try_later()
    return {'user': {"id": user.id, "login": user.login}}, 201

@app.route('/api/login', methods=['POST'])
@validate_params(
    Param('login', JSON, str, rules=[Pattern(r'^[a-z_0-9\-.]{5,64}$')]),
    Param('password', JSON, str, rules=[Pattern(r'^[a-z_0-9\-.!$&]{5,15}$')])
)
def login(login, password):
    user = User.query.filter_by(login=login).first()
    if user is None or not user.is_password_valid(password):
        return {"error": "Invalid user name or password"}, 401
    user.update_last_login()
    return {"access_token": create_jwt(identity=user.id)}

@app.route('/api/posts', methods=['POST'])
@jwt_required
@validate_params(
    Param('text', JSON, str, rules=[MaxLength(255)]),
)
def create_post(text):
    user = get_JWT_user()
    user.update_last_activity()
    post = Post(body=text, author=user)
    db.session.add(post)
    try:
        db.session.commit()
    except Exception:
        return try_later()
    return {"post": {"id": post.id}}, 201

@app.route('/api/posts/<int:id>/like', methods=['GET', 'POST'])
@jwt_required
def like(id):
    user = get_JWT_user()
    user.update_last_activity()
    post = Post.query.get(id)
    if not post:
        raise NotFound
    like = Like.query.filter_by(post_id=id, user_id=user.id).first()
    if like is None:
        like = Like(post=post, author=user)
    like.liked = True
    db.session.add(like)
    try:
        db.session.commit()
    except Exception:
        return try_later()
    return {"like": {"id": like.id}}, 201

@app.route('/api/posts/<int:id>/unlike', methods=['GET', 'POST'])
@jwt_required
def unlike(id):
    user = get_JWT_user()
    user.update_last_activity()
    post = Post.query.get(id)
    if not post:
        raise NotFound
    like = Like.query.filter_by(post_id=id, user_id=user.id).first()
    if like:
        db.session.delete(like)
        try:
            db.session.commit()
        except Exception:
            return try_later()
    return ""

@app.route('/api/user_activity', methods=['GET'])
@jwt_required
def user_activity():
    user = get_JWT_user()
    user.update_last_activity()
    return {"last_login": user.last_login, "last_activity": user.last_activity}

@app.route('/api/activity', methods=['GET'])
@jwt_required
def activity():
    today = str(datetime.date.today())
    date_from = request.args.get("date_from", today)
    date_to = request.args.get("date_to", today)
    if not is_valid_date(date_from):
        date_from = today
    if not is_valid_date(date_to):
        date_to = today
    activity = db.session.query(label("date", func.date(Like.created_at)), label('likes', func.sum(cast(Like.liked, sqlalchemy.Integer)))).filter(func.date(Like.created_at) >= date_from).filter(func.date(Like.created_at) <= date_to).group_by(func.date(Like.created_at)).all()
    return {"activity": activity}