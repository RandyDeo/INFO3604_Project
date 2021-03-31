import json
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import collections
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
            if user.occupation == "Business":
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


@app.route("/businessHome", methods=(['GET']))
# @login_required
def businessHome():
    return render_template("business-homepage.html")


@app.route("/dcitHome", methods=(['GET']))
@login_required
def dcitHome():
    return render_template("DCIT-homepage.html")


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
        photo = request.files['photo']

        student = Student.query.filter_by(uwiid=uwiid).first()

        transcript.save(os.path.join("uploads", uwiid + "_transcript.pdf"))
        resume.save(os.path.join("uploads", uwiid + "_resume.pdf"))
        essay.save(os.path.join("uploads", uwiid + "_essay.pdf"))
        photo.save(os.path.join("uploads", uwiid + "_photo.pdf"))

        if student is None and transcript.filename != '' and resume.filename != '' and essay.filename != '':
            new_student = Student(name=name, email=email, uwiid=uwiid, country=country,
                                  year_of_study=year_of_study, credits=credit, enrollment=enrollment,
                                  curr_degree=curr_degree, transcript=(uwiid + "_transcript.pdf"),
                                  resume=(uwiid + "_resume.pdf"), essay=(uwiid + "_essay.pdf"),
                                  photo=(uwiid + "_essay.pdf"))

            try:
                db.session.add(new_student)
                db.session.commit()
                return render_template('student-homepage.html')
            except IntegrityError:
                return 'Application does not exist', render_template("student-registration.html"), 400
        return


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
        lang = request.form.get('lang')
        design = request.form.get('design')
        dbms = request.form.get('dbms')
        soft_skills = request.form.get('soft_skills')

        business = Business.query.filter_by(bname=bname).first()

        if business is None:
            new_business = Business(bname=bname, num_interns=num_interns, duration=duration, stipend=stipend,
                                    credits=credits, language=lang, design=design, dbms=dbms, soft_skills=soft_skills)

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

class Students:
    def __init__(self):
        self.studentId = '816000505'
        self.tech = self.Tech()

    class Tech:
        def __init__(self):
            self.course_list = []  # This is going to be form AJAX Array
            self.design = []
            self.dbms = []
            self.language = []

        def dupe(self, arg):
            mylist = arg
            mylist = list(dict.fromkeys(mylist))
            return mylist

        def listing(self, arg):
            list_length = len(arg)

            design = []
            dbms = []
            language = []

            for i in range(list_length):
                if arg[i] == "COMP 2602":
                    language.append("Python")
                elif arg[i] == "COMP 2603":
                    language.append("JAVA")
                elif arg[i] == "COMP 2604":
                    language.append("C"), language.append("C++")
                elif arg[i] == "COMP 2605":
                    language.append("SQL")
                    dbms.append("MySQL"), dbms.append("Oracle")
                elif arg[i] == "COMP 2611":
                    language.append("C++"), language.append("Python")
                elif arg[i] == "COMP 3603":
                    design.append("Web")
                elif arg[i] == "COMP 3605":
                    language.append("Python")
                elif arg[i] == "COMP 3606":
                    language.append("JAVA")
                    design.append("Mobile")
                elif arg[i] == "COMP 3607":
                    language.append("JAVA")
                elif arg[i] == "COMP 3608":
                    language.append("MiniZinc"), language.append("Python")
                elif arg[i] == "COMP 3609":
                    language.append("JAVA")
                elif arg[i] == "COMP 3610":
                    language.append("SQL")
                    dbms.append("NoSQL")
                elif arg[i] == "COMP 3613":
                    language.append("Python"), language.append("HTML"), language.append("JavaScript")
                    design.append("Web"), design.append("CSS"), design.append("SASS")
                    dbms.append("MySQL"), dbms.append("Oracle"), dbms.append("MongoDB")
                elif arg[i] == "INFO 2601":
                    language.append("Python")
                    design.append("Networking")
                elif arg[i] == "INFO 2602":
                    language.append("JavaScript"), language.append("CSS"), language.append(
                        "Flask-Python"), language.append("Python")
                    design.append("Web")
                    dbms.append("MySQL"), dbms.append("Oracle"), dbms.append("MongoDB")
                elif arg[i] == "INFO 2603":
                    language.append("Python")
                    design.append("Networking")
                elif arg[i] == "INFO 2604":
                    language.append("Python")
                    design.append("Networking")
                elif arg[i] == "INFO 3600":
                    language.append("Visual Basic")
                    dbms.append("Microsoft Access (Excel)")
                elif arg[i] == "INFO 3602":
                    language.append("JavaScript"), language.append("HTML")
                    language.append("CSS"), language.append("SASS")
                elif arg[i] == "INFO 3604":
                    language.append("Python"), language.append("Flask-Python"), language.append(
                        "React"), language.append("HTML"), language.append("Machine-Learning"), language.append(
                        "JavaScript")
                    design.append("CSS"), design.append("SASS")
                    dbms.append("MySQL"), dbms.append("Oracle"), dbms.append("MongoDB")
                elif arg[i] == "INFO 3605":
                    language.append("Python")
                    design.append("Networking")
                elif arg[i] == "INFO 3606":
                    language.append("Cloud")
                    dbms.append("IBM"), dbms.append("Cloud")  # Check this
                elif arg[i] == "INFO 3608":
                    dbms.append("PHP"), dbms.append("HTML"), dbms.append("WordPress")
                    design.append("CSS"), design.append("Web")
                    dbms.append("phpMyAdmin"), dbms.append("Xampp")
                elif arg[i] == "INFO 3611":
                    language.append("SQL")
                    dbms.append("MySQL"), dbms.append("Oracle")

            test = Students()
            test.tech.design = test.tech.dupe(design)
            test.tech.dbms = test.tech.dupe(dbms)
            test.tech.language = test.tech.dupe(language)
            print(test.tech.dupe(language), test.tech.dupe(design), test.tech.dupe(dbms))
            return test

    def show(self):
        print('In outer class')
        print('Name:', self.studentId)
        print('TechSkills:', self.tech.language, self.tech.dbms, self.tech.design)


courselst = ["COMP 2605", "COMP 3606", "INFO 3611"]
outer = Students()
outer.tech.course_list = courselst
print('Name:', outer.studentId)
outer = outer.tech.listing(courselst)
print(outer.tech.language, outer.tech.design, outer.tech.dbms)
# outer.show()

# if self.techskills.course_code[0] == self.course.courseCode:
#    self.techskills.language.append(self.course.languages)
#   self.techskills.networks.append(self.course.networkss)
#  self.techskills.design.append(self.course.designs)
