from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, flash
from hls_webapp import db, login_manager
from flask_login import UserMixin
from sqlalchemy.schema import PrimaryKeyConstraint


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    sound_file_in = db.relationship('SoundFileIn', backref='user', lazy=True)
    sound_file_out = db.relationship('SoundFileOut', backref='user', lazy=True)
    sim_data = db.relationship('DecibelLoss', backref='user', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class SoundFileIn(db.Model):
    __tablename__ = 'sound_file_in'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(120), nullable=False,
                          default='default_audio.wav')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"SoundFileIn('{self.file_name}','{self.id}','{self.user}')"


class DecibelLoss(db.Model):
    __tablename__ = 'decibel_loss'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    audiogram_name = db.Column(db.String(120), nullable=False)

    # create a left dict and a right dict
    hll125 = db.Column(db.String(3), nullable=False)
    hlr125 = db.Column(db.String(3), nullable=False)
    hll250 = db.Column(db.String(3), nullable=False)
    hlr250 = db.Column(db.String(3), nullable=False)
    hll500 = db.Column(db.String(3), nullable=False)
    hlr500 = db.Column(db.String(3), nullable=False)
    hll1000 = db.Column(db.String(3), nullable=False)
    hlr1000 = db.Column(db.String(3), nullable=False)
    hll2000 = db.Column(db.String(3), nullable=False)
    hlr2000 = db.Column(db.String(3), nullable=False)
    hll4000 = db.Column(db.String(3), nullable=False)
    hlr4000 = db.Column(db.String(3), nullable=False)
    hll8000 = db.Column(db.String(3), nullable=False)
    hlr8000 = db.Column(db.String(3), nullable=False)
    compress = db.Column(db.String(3), nullable=False, default='0')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"DecibelLoss('{self.hll125}','{self.hlr125}','{self.hll250}','{self.hlr250}','{self.hll500}','{self.hlr500}','{self.hll1000}','{self.hlr1000}','{self.hll2000}','{self.hlr2000}','{self.hll4000}','{self.hlr4000}','{self.hll8000}','{self.hlr8000}','{self.compress}','{self.id}','{self.user}')"


class SoundFileOut(db.Model):
    __tablename__ = 'sound_file_out'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sound_file_in = db.Column(db.String(120), nullable=False)
    frequency_loss = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"SoundFileOut('{self.file_name}','{self.id}','{self.user}')"

# class SoundFileOut(db.Model):
#     __tablename__ = 'sound_file_out'
#     __table_args__ = (
#         PrimaryKeyConstraint('sound_in_id', 'decibel_loss_id'),
#         {})

#     file_name = db.Column(db.String(120), nullable=False)

#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     sound_in_id = db.Column(db.Integer, db.ForeignKey(
#         'sound_file_in.id'), nullable=False)
#     decibel_loss_id = db.Column(db.Integer, db.ForeignKey(
#         'decibel_loss.id'), nullable=False)

#     db.relationship('User', uselist=False,
#                     backref='sound_file_out', lazy='dynamic')
#     db.relationship('SoundFileIn', uselist=False,
#                     backref='sound_file_out', lazy='dynamic')
#     db.relationship('DecibelLoss', uselist=False,
#                     backref='sound_file_out', lazy='dynamic')

#     def __repr__(self):
#         return f"SoundFileOut('{self.file_name}','{self.user_id}','{self.sound_in_id}','{self.decibel_loss_id}')"
