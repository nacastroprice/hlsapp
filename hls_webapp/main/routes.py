from flask import render_template, request, Blueprint, flash
from hls_webapp.models import User
from hls_webapp import db, bcrypt
from hls_webapp.users.forms import SimulationFreqForm

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():

    return render_template('home.html', title='')


