
import os
import secrets
from flask import url_for, current_app
from flask_mail import Message
from hls_webapp import mail


def save_audio(form_audio):
    audio_fn = form_audio.filename
    audio_path = os.path.join(current_app.root_path,
                              'static\\audio_files_in', audio_fn).replace('\\', '/')

    form_audio.save(audio_path)
    return audio_fn


def encrypt_name(name):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(name)
    name = random_hex + f_ext
    return name


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='hlosssimulator@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
