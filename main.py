import json
from flask import Flask, render_template, request
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

from models import db, User

''' Begin boilerplate code '''
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def create_app():
    app = Flask("__name__", template_folder="templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "MYSECRET"
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=7)
    db.init_app(app)
    return app


app = create_app()

app.app_context().push()
db.create_all(app=app)
''' End Boilerplate Code '''

''' Set up JWT here '''


def authenticate(sid, password):
    # search for the specified user
    user = models.User.query.filter_by(id=sid).first()
    # if user is found and password matches
    if user and user.check_password(password):
        return user


# Payload is a dictionary which is passed to the function by Flask JWT
def identity(payload):
    return models.User.query.get(payload['identity'])


jwt = JWT(app, authenticate, identity)

''' End JWT Setup '''


@app.route("/")
def home():
    return render_template("landing-page.html")


@app.route("/signup-login.html")
def signupPage():
    return render_template("signup-login.html")


@app.route("/signup-login.html", methods=(['POST']))
def signup():
    email = request.form.get('email')
    name = request.form.get('name')
    occupation = request.form.get('occupation')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        return 'Email address already exists', render_template("signup-login.html"), 400

    # create new user with the form data
    new_user = User(name=user("name"), email=user("email"), occupation=user("occupation"))
    new_user.password = generate_password_hash(password, method='sha256')

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return render_template("student-homepage.html"), 201


@app.route("/signup-login.html", methods=(['GET', 'POST']))
def login():
    if request.method == 'GET':
        return render_template("signup-login.html")
    elif request.method == 'POST':
        userData = reqest.form.to.dict()
        username = userData['name']
        password = userData['pass']
        user = User.query.filter_by(name=username).first()
        if user and user.check_password(password):
            time = timedelat(hours=1)
            login_user(user, False, time)
            return render_template('student-homepage.html'), 200
        if user is None:
            return render_template('signup-login.html'), 401
    return "Invalid Login", 401


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('signup-login.html')


@app.route("/logout", methods=(['GET']))
@login_required
def logout():
    logout_user()
    return render_template('landing-page.html')

# @app.route("/upload", methods=['POST'])
# def upload():
#   file = request.files['inputFile']

#  newFile = FileContents(name=file.filename, data=file.read())
# db.session.add(newFile)
# db.session.commit()

# return 'Saved ' + file.filename + ' to the database!'
