from flask import Flask, session, render_template, url_for, flash, redirect, request, Blueprint, send_file
from flask_login import login_user, current_user, logout_user, login_required
from hls_webapp import db, bcrypt
from hls_webapp.models import User, SoundFile, DecibelLoss
from hls_webapp.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                    RequestResetForm, ResetPasswordForm, SimulationOptions, SimulationFreqForm)
from hls_webapp.users.utils import save_picture, send_reset_email, save_audio
from hls_webapp.offline_wav_file import compute
import os

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        if form.audio.data:
            audio_file = save_audio(form.audio.data)
            audio_file = SoundFile(file_name=audio_file, user=current_user)
            db.session.add(audio_file)

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@users.route("/user/output")
@login_required
def output():
    path_in = "static/audio_files_in/"
    path_out = "static/audio_files_out/"
    file_path_out = os.path.join(
        "hls_webapp", path_out).replace('\\', '/')
    file_path_in = os.path.join(
        "hls_webapp", path_in).replace('\\', '/')
    file_name = session.get('file')
    in_file = file_path_in + file_name
    out_file = file_path_out + "sim" + file_name
    compute(in_file, out_file)
    # save the new file to db
    return render_template('output.html', title='output', in_file=in_file, out_file="/" + path_out + "sim" + file_name)


@users.route("/user/<string:username>/simulation", methods=['GET', 'POST'])
@login_required
def user_simulation(username):
    path = 'audio_files_in/'
    file_path = os.path.join('/static', path).replace('\\', '/')

    form = SimulationOptions()
    sound_files = SoundFile.query.filter_by(user_id=current_user.id)
    choices_audio = [(g.id, g.file_name) for g in sound_files]
    form.group_id.choices = choices_audio

    if form.validate_on_submit():
        audio_file_id = int(form.group_id.data)
        file_name = form.group_id.choices[audio_file_id - 1][1]
        session["file"] = file_name
        return redirect(url_for('users.output'))

    return render_template('simulation_setup.html', title='Simulation Set Up', form=form, file_path=file_path)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@users.route("/simulator", methods=['GET', 'POST'])
@login_required
def simulator():
    form = SimulationFreqForm()
    if form.validate_on_submit():
        sim_data = DecibelLoss(hll125=form.hlleft125.data, hlr125=form.hlright125.data, hll250=form.hlleft250.data, hlr250=form.hlright250.data, hll500=form.hlleft500.data, hlr500=form.hlright500.data, hll1000=form.hlleft1000.data, hlr1000=form.hlright1000.data,
                               hll2000=form.hlleft2000.data, hlr2000=form.hlright2000.data, hll4000=form.hlleft4000.data, hlr4000=form.hlright4000.data, hll8000=form.hlleft8000.data, hlr8000=form.hlright8000.data, compress=form.compression.data, user=current_user)
        db.session.add(sim_data)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('simulator.html', form=form, title='Simulator')
