from flask import Flask, session, render_template, url_for, flash, redirect, request, Blueprint, send_file
from flask_login import login_user, current_user, logout_user, login_required
from hls_webapp import db, bcrypt
from hls_webapp.models import User, SoundFileIn, DecibelLoss, SoundFileOut, sound_file_out_table
from hls_webapp.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                    RequestResetForm, ResetPasswordForm, SimulationOptions, CombinedAudiogramForm, InputAudioForm)
from hls_webapp.users.utils import send_reset_email, save_audio, encrypt_name
from hls_webapp.offline_wav_file import compute
import numpy as np
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


@users.route("/account", methods=['GET'])
@login_required
def account():
        # This is to create the audiogram table dynamically
    audiograms = DecibelLoss.query.filter_by(user_id=current_user.id)
    choices_audiogram = [(g.id, g.audiogram_name, g.compress)
                         for g in audiograms]
    #  This is to create the input file table dynamically
    sound_files = SoundFileIn.query.filter_by(user_id=current_user.id)
    choices_audio = [(g.id, g.file_name) for g in sound_files]

    return render_template('account.html', title='Account', choices_audiogram=choices_audiogram, choices_audio=choices_audio)


@users.route("/user/output")
@login_required
def output():
    return render_template('output.html', title='output')


@users.route("/user/<string:username>/audiogramsetup", methods=['GET', 'POST'])
@login_required
def user_audiogramsetup(username):
    form_audiogram = CombinedAudiogramForm()
    if form_audiogram.validate_on_submit():
        audiogram_name = form_audiogram.audiogram_name.data
        left = form_audiogram.frequency_loss_left.data
        right = form_audiogram.frequency_loss_right.data
        sim_data = DecibelLoss(audiogram_name=audiogram_name, hll125=left['hlleft125'], hlr125=right['hlright125'], hll250=left['hlleft250'], hlr250=right['hlright250'], hll500=left['hlleft500'], hlr500=right['hlright500'], hll1000=left['hlleft1000'], hlr1000=right['hlright1000'],
                               hll2000=left['hlleft2000'], hlr2000=right['hlright2000'], hll4000=left['hlleft4000'], hlr4000=right['hlright4000'], hll8000=left['hlleft8000'], hlr8000=right['hlright8000'], compress=form_audiogram.compression_loss.data, user_id=current_user.id)
        db.session.add(sim_data)
        db.session.commit()
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        return render_template('audiogram.html', title='audiogram set up', form_audiogram=form_audiogram)


@users.route("/user/<string:username>/inputfile", methods=['GET', 'POST'])
@login_required
def user_inputfile(username):
    form_inputFile = InputAudioForm()
    if form_inputFile.validate_on_submit():
        audio_file = save_audio(form_inputFile.audio.data)
        audio_file = SoundFileIn(
            file_name=audio_file, user_id=current_user.id)
        db.session.add(audio_file)
        db.session.commit()
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        return render_template('inputfile.html', title='audio file set up', form_inputFile=form_inputFile)


@users.route("/user/<string:username>/simulator", methods=['GET', 'POST'])
@login_required
def user_simulator(username):
    path = 'audio_files_in/'
    file_path = os.path.join('/static', path).replace('\\', '/')

    form = SimulationOptions()
    sound_files = SoundFileIn.query.filter_by(user_id=current_user.id)
    choices_audio = [(g.id, g.file_name) for g in sound_files]
    audiograms = DecibelLoss.query.filter_by(user_id=current_user.id)
    choices_audiogram = [(g.id, g.audiogram_name) for g in audiograms]
    form.frequency_loss_group_id.choices = choices_audiogram
    form.sound_group_id.choices = choices_audio

    if form.validate_on_submit():

        audio_file_id = int(form.sound_group_id.data)
        file_name = form.sound_group_id.choices[audio_file_id - 1][1]
        in_file_object = SoundFileIn.query.filter_by(
            file_name=file_name).first()

        frequency_loss_file_id = int(form.frequency_loss_group_id.data)
        audiogram_name = form.frequency_loss_group_id.choices[frequency_loss_file_id - 1][1]
        frequency_loss_object = DecibelLoss.query.filter_by(
            audiogram_name=audiogram_name).first()

        # this gets the full path for the in_file and constructs it for the out_file
        path_in = "static/audio_files_in/"
        path_out = "static/audio_files_out/"
        file_path_out = os.path.join(
            "hls_webapp", path_out).replace('\\', '/')
        file_path_in = os.path.join(
            "hls_webapp", path_in).replace('\\', '/')

        in_file = file_path_in + file_name

        out_name = encrypt_name(file_name)
        out_file = file_path_out + out_name

        left_p_loss = [float(frequency_loss_object.hll125), float(frequency_loss_object.hll250), float(frequency_loss_object.hll500), float(
            frequency_loss_object.hll1000), float(frequency_loss_object.hll2000), float(frequency_loss_object.hll4000), float(frequency_loss_object.hll8000)]
        right_p_loss = [float(frequency_loss_object.hlr125), float(frequency_loss_object.hlr250), float(frequency_loss_object.hlr500), float(
            frequency_loss_object.hlr1000), float(frequency_loss_object.hlr2000), float(frequency_loss_object.hlr4000), float(frequency_loss_object.hlr8000)]

        # compression_degree: assumes same compression in both
        compression_degree = np.ones(
            7) * float(frequency_loss_object.compress)/10

        compute(in_file, out_file, left_p_loss,
                right_p_loss, compression_degree)

        session["sound_out"] = "/" + path_out + out_name
        # save the new file to db
        # out_file = save_audio(form_audio, "out")
        audio_file = SoundFileOut(file_name=out_name, user_id=current_user.id)

        db.session.add(audio_file)
        db.session.commit()

        ins = sound_file_out_table.insert().values(sound_file_out_id=audio_file.id, user_id=current_user.id,
                                                   sound_file_in_id=in_file_object.id, decibel_loss_id=frequency_loss_object.id)
        db.engine.execute(ins)

        return redirect(url_for('users.user_simulator', username=current_user.username))

    elif request.method == 'GET':
        sound = False
        if session.get('sound_out', None):
            soundout = session.get('sound_out', None)
            sound = True
            session.pop('sound_out')
            return render_template('simulation_setup.html', title='Simulation Set Up', form=form, file_path=file_path, sound=sound, sound_out=soundout)
        return render_template('simulation_setup.html', title='Simulation Set Up', form=form, file_path=file_path, sound=sound)


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
