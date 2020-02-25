from hls_webapp.models import User
from flask_login import current_user
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
<< << << < HEAD
== == == =
>>>>>> > 26e5989f0633a466d3c72fb64c6ca29be75d4486


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])

    audio = FileField('Upload .wav file', validators=[FileAllowed(['wav'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is taken. Please choose a different one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                'There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class SimulationOptions(FlaskForm):

    group_id = SelectField(u'Sound Group', coerce=int,
                           validators=[InputRequired()])

    submit = SubmitField('Submit simulation preferences')

    # def validate_sim_options(self, obj):
    #     # user = current_user.id:
    #     form = SimulationOptions(request.POST, obj=current_user.sound_file)
    #     form.group_id.choices = [(g.id, g.file_name)
    #                              for g in Group.query.all()]


class SimulationFreqForm(FlaskForm):
    hlleft125 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlright125 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlleft250 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlright250 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlleft500 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlright500 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlleft1000 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlright1000 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlleft2000 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlright2000 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlleft4000 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlright4000 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlleft8000 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    hlright8000 = IntegerField('', validators=[DataRequired(), NumberRange(
        min=0, max=130, message='Value cannot be less than 0 or greater than 130')])
    compression = IntegerField('', validators=[NumberRange(min=0, max=10)])
    submit = SubmitField('Enter Data')
