import json
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

from models import db, User, Student

''' Begin boilerplate code '''


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

login_manager = LoginManager(app)


@login_manager.user_loader
def user_loader(email):
    return User.query.get(email)  # review this// may result in error


''' End Boilerplate Code '''

''' Set up JWT here '''


def authenticate(email, password):
    user = models.User.query.filter_by(email=email).first()
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


@app.route("/signup")
def signupPage():
    return render_template("signup.html")


@app.route("/signup", methods=(['POST']))
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        occupation = request.form.get('occupation')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user is None:
            new_user = User(name=name, email=email, occupation=occupation)
            new_user.password = generate_password_hash(password, method='sha256')
            try:
                db.session.add(new_user)
                db.session.commit()
                # login_user(new_user)
                #return render_template("student-homepage.html"), 201
                return render_template('Login.html'), 201
            except IntegrityError:
                db.session.rollback()
                return 'Email address already exists', render_template("login.html"), 400
        return


# create new user with the form data
# new_user = new_user.name=["name"], email=user["email"], occupation=user["occupation"])
# new_user.password = generate_password_hash(password, method='sha256')

# add the new user to the database
#COMMENTING THIS OUT BECAUSE YEAH NO
#@app.route("/login", methods=(['GET', 'POST']))
#def login():
    #if request.method == 'GET':
        #return render_template('login.html')

    #elif request.method == 'POST':
        #email = request.form.get('email')
        #password = request.form.get('password')

        #if not (current_user == authenticate(email, password)):
            #pass
        #else:
            #return render_template('student-homepage')

        #user = User.query.filter_by(email=email).first()
        #if user and user.check_password_hash(password):
            #try:
                #login_user(user, remember=True)  # this is an error but line has to be there
                #return render_template('student-homepage.html'), 200
            #except IntegrityError:
                #return 'Email address does not exist', render_template("signup.html"), 400
    #return render_template('student-homepage.html')

@app.route ("/login", methods =(['GET', 'POST']))
def login():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            time = timedelta(hours=1)
            login_user(user, False, time)
            return studentHome(), 200
        if user is None:
            return "Please create an account!"
            #return render_template('signup.html'), 401
        return "Invalid login", 401

    #return render_template("student-homepage.html")

@app.route("/studentHome", methods=(['GET']))
@login_required
def studentHome():
    return render_template("student-homepage.html")

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('signup.html')


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

#@app.route("/register", methods=(['POST']))
