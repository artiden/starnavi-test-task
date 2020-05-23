from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

#===============================================================================
# User
#===============================================================================
class User(db.Model):
    id = db.Column(db.INTEGER, primary_key = True)
    login = db.Column(db.String(64), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    last_login = db.Column(db.DateTime, index=True)
    last_activity = db.Column(db.DateTime, index=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='author', lazy='dynamic')

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def update_last_activity(self):
        self.last_activity = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def is_password_valid(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User {}>".format(self.login)

class Post(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.String(255))
    likes = db.relationship('Like', backref='post', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __str__(self):
        return "<{} says: {}>".format(self.author.login, self.body)

class Like(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.INTEGER, db.ForeignKey('post.id'), nullable=False)
    liked = db.Column(db.BOOLEAN, default=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "Post: {}\nUser: {}".format(self.post.body, self.author.login)