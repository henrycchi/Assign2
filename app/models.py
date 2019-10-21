from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    twofa = db.Column(db.String(11), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    inputtext = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
	
    def set_twofa(self, twofa):
        self.twofa = generate_password_hash(twofa)

    def check_twofa(self, twofa):
        return check_password_hash(self.twofa, twofa)





