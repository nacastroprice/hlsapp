from flask import render_template, request, Blueprint, flash
from hls_webapp.models import User
from hls_webapp import db, bcrypt

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    # user = User(username="admin",
    #             email='admin@admin.com', password="admin")
    # db.session.add(user)
    # db.session.commit()

    return render_template('home.html', title='')
