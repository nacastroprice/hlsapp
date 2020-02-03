from flask import render_template, request, Blueprint, flash
from hls_webapp.models import User
from hls_webapp import db, bcrypt

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():

    return render_template('home.html')


@main.route("/about")
def about():
    return render_template('about.html', title='About')
