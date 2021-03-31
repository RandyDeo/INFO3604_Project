import json
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

import os

from models import db, User, Student, Business, Internship, FileContents

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
        password = request.form.get('pass')
        user = User.query.filter_by(email=email).first()
        if user is None:
            new_user = User(name=name, email=email, occupation=occupation)
            new_user.password = generate_password_hash(password, method='sha256')
            try:
                db.session.add(new_user)
                db.session.commit()
                # login_user(new_user)
                # return render_template("student-homepage.html"), 201
                return render_template('Login.html'), 201
            except IntegrityError:
                db.session.rollback()
                return 'Email address already exists', render_template("login.html"), 400
        return


# create new user with the form data
# new_user = new_user.name=["name"], email=user["email"], occupation=user["occupation"])
# new_user.password = generate_password_hash(password, method='sha256')

# add the new user to the database
# COMMENTING THIS OUT BECAUSE YEAH NO
# @app.route("/login", methods=(['GET', 'POST']))
# def login():
# if request.method == 'GET':
# return render_template('login.html')

# elif request.method == 'POST':
# email = request.form.get('email')
# password = request.form.get('password')

# if not (current_user == authenticate(email, password)):
# pass
# else:
# return render_template('student-homepage')

# user = User.query.filter_by(email=email).first()
# if user and user.check_password_hash(password):
# try:
# login_user(user, remember=True)  # this is an error but line has to be there
# return render_template('student-homepage.html'), 200
# except IntegrityError:
# return 'Email address does not exist', render_template("signup.html"), 400
# return render_template('student-homepage.html')

@app.route("/login", methods=(['GET', 'POST']))
def login():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            time = timedelta(hours=1)
            login_user(user, False, time)
            if user.occupation == "Business" :
                return businessHome(), 200
            if user.occupation == "Student":
                return studentHome(), 200
            elif user.occupation == "DCIT":
                return dcitHome(), 200
        if user is None:
            return "Please create an account!"
            # return render_template('signup.html'), 401
        return "Invalid login", 401

    # return render_template("student-homepage.html")


@app.route("/studentHome", methods=(['GET']))
@login_required
def studentHome():
    return render_template("student-homepage.html")


#DCIT ROUTES
#DCIT homepage route
@app.route("/dcitHome", methods=(['GET']))
@login_required
def dcitHome():
    return render_template("dcit-homepage.html")

#DCIT deadlines route
@app.route("/deadlines", methods=(['GET']))
@login_required
def deadlines():
    return render_template("dcit-deadlines.html")

#DCIT student profiles route
@app.route("/dcitStudentProfiles", methods=(['GET']))
@login_required
def dcitStudentProfiles():
    return render_template("dcit-studentprofiles.html")

#DCIT weekly reports route
@app.route("/dcitWeeklyReports", methods=(['GET']))
@login_required
def dcitWeeklyReports():
    return render_template("dcit-weeklyreports.html")

#DCIT company list route
@app.route("/dcitCompanyList", methods=(['GET']))
@login_required
def dcitCompanyList():
    return render_template("dcit-companylist.html")



@app.route("/studentRegistration")
def studentRegistration():
    return render_template("student-registration.html")


@app.route("/displayStudentForm", methods=(['GET', 'POST']))
def displayStudentForm():
    if request.method == 'GET':
        return render_template('student-registration-form.html')

    elif request.method == 'POST':
        name = request.form.get('fname')
        email = request.form.get('emails')
        uwiid = request.form.get('uwiid')
        country = request.form.get('country')
        curr_degree = request.form.get('curr_degree')
        year_of_study = request.form.get('yos')
        credit = request.form.get('credits')
        enrollment = request.form.get('enrollment')

        transcript = request.files['transcript']
        resume = request.files['resume']
        essay = request.files['essay']

        student = Student.query.filter_by(uwiid=uwiid).first()

        transcript.save(os.path.join("uploads", uwiid + "_transcript.pdf"))
        resume.save(os.path.join("uploads", uwiid + "_resume.pdf"))
        essay.save(os.path.join("uploads", uwiid + "_essay.pdf"))

        if student is None and transcript.filename != '' and resume.filename != '' and essay.filename != '':
            new_student = Student(name=name, email=email, uwiid=uwiid, country=country,
                                  year_of_study=year_of_study, credits=credit, enrollment=enrollment,
                                  curr_degree=curr_degree, transcript=(uwiid + "_transcript.pdf"),
                                  resume=(uwiid + "_resume.pdf"), essay=(uwiid + "_essay.pdf"))
            try:
                db.session.add(new_student)
                db.session.commit()
                return render_template('student-homepage.html')
            except IntegrityError:
                return 'Application does not exist', render_template("student-registration.html"), 400
        return


@app.route("/businessHome", methods=(['GET']))
# @login_required
def businessHome():
    return render_template("business-homepage.html")

@app.route("/businessRegistration")
def businessRegistration():
    return render_template("business-registration.html")


@app.route("/displayBusinessForm", methods=(['GET', 'POST']))
def displayBusinessForm():
    if request.method == 'GET':
        return render_template('business-registration-form.html')

    elif request.method == 'POST':
        bname = request.form.get('bname')
        num_interns = request.form.get('num_interns')
        duration = request.form.get('duration')
        credits = request.form.get('credits')
        stipend = request.form.get('stipend')
        tech_skills = request.form.get('tech_skills')
        soft_skills = request.form.get('soft_skills')

        business = Business.query.filter_by(bname=bname).first()

        if business is None:
            new_business = Business(bname=bname, num_interns=num_interns, duration=duration, stipend=stipend,
                                    credits=credits, tech_skills=tech_skills, soft_skills=soft_skills)

            db.session.add(new_business)
            db.session.commit()

            proj_name = request.form.get('proj_name')
            proj_descript = request.form.get('proj_descript')
            activities = request.form.get('activities')
            internship = Internship.query.filter_by(proj_name=proj_name).first()

            if internship is None:
                new_internship = Internship(proj_name=proj_name, proj_descript=proj_descript, activities=activities,
                                            business_ID=new_business.businessID)
            try:
                db.session.add(new_internship)
                db.session.commit()
                return render_template('business-homepage.html')
            except IntegrityError:
                return 'Application does not exist', render_template("business-registration.html"), 400
    return


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


# @app.route("/register", methods=(['POST']))
