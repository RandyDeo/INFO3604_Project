import json
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from sqlalchemy import or_
import collections
import os
import requests
import json


from models import db, User, Student, Business, Internship, parsed_courses, Report, DCITAdmin, Risk, Shortlist, Deadlines


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
    return User.query.get(email)


''' End Boilerplate Code '''

''' Set up JWT here '''


def authenticate(email, password):
    user = models.User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user


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
                return render_template('Login.html'), 201
            except IntegrityError:
                db.session.rollback()
                #flash("Email address already exists")
                #return render_template ("login.html"), 400
                return 'Email address already exists', render_template("login.html"), 400
        return


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
            flash("Please create an account!")
            return render_template("signup.html"), 400
            #return "Please create an account!"
    flash("Invalid login!")
    return render_template("login.html"), 401


# new_admin = DCIT_Admin(aname=user.name, aemail=user.email)
# db.session.add(new_admin)
# db.session.commit()

# DCIT ROUTES
# DCIT homepage route
@app.route("/dcitHome", methods=(['GET']))
@login_required
def dcitHome():
    return render_template("dcit-homepage.html")


# DCIT deadlines route
@app.route("/deadlines", methods=(['GET', 'POST']))
@login_required
def deadlines():
    if request.method == 'GET':
        return render_template("dcit-deadlines.html")

    elif request.method == 'POST':
        deadline_message = request.form.get('deadline')
        deadline = Deadlines.query.filter_by(deadline_message=deadline_message).first()
        admin = User.query.filter_by(occupation="DCIT").first()


        new_admin = DCITAdmin(aname=admin.name, aemail=admin.email)
        db.session.add(new_admin)
        db.session.commit()

        if deadline is None:
                new_deadline = Deadlines(deadline_message=deadline_message, deadline_adminID=new_admin.adminID)
                new_deadline.date = datetime.now()
        try:
                db.session.add(new_deadline)
                db.session.commit()
                flash ("Deadline has been posted!")
                return redirect(url_for('deadlines'))
        except IntegrityError:
                db.session.rollback()
                return 'Deadline cannot be added. Try again!', render_template("dcit-deadlines.html"), 400
    return


# DCIT student profiles route
@app.route("/dcitStudentProfiles", methods=(['GET', 'POST']))
@login_required
def dcitStudentProfiles():
    if request.method == 'GET':
        s_list = Student.query.all()
        c_list = parsed_courses.query.all()
        return render_template("dcit-studentprofiles.html", student_list=s_list, course_list=c_list)

    elif request.method == 'POST':
        st_id = request.form.get('v_profile')
        st_curr = Student.query.filter_by(uwiid=st_id).first()
        c_list = parsed_courses.query.all()
        return render_template("dcit-individualprofile.html", course_list=c_list, st_curr=st_curr)

# DCIT Student Profiles Search Function works with IDs lol
@app.route("/dcitStudentProfiles1", methods=(['POST']))
@login_required
def searchID():
    if request.method == 'POST':
        entry = request.form.to_dict()
        key = entry['keyword']
        print(key)
        searchkey = "%{}%".format(key)
        asgs = Student.query.filter(Student.uwiid.like(searchkey)).all()
        # asgs = Student.query.filter(Student.name.like(searchkey)).all()
        if asgs:
            report = ""
            return render_template("dcit-studentprofiles.html", message=report, student_list=asgs)
        else:
            #report = "No student found."
            flash("No student found!")
            #return render_template("dcit-studentprofiles.html", message=report, student_list=asgs)
            return render_template("dcit-studentprofiles.html")
    return error(), 400


# DCIT weekly reports route
@app.route("/dcitWeeklyReports", methods=(['GET', 'POST']))
@login_required
def dcitWeeklyReports():
    if request.method == 'GET':
        s_list = Student.query.all()
        reports = Report.query.all()
        return render_template("dcit-weeklyreports.html", student_list=s_list, report_list=reports)

    elif request.method == 'POST':
        st_id = request.form.get('v_report')
        st_curr = Student.query.filter_by(uwiid=st_id).first()
        reports = Report.query.all()
        return render_template("dcit-individualreports.html", report_list=reports, st_curr=st_curr)


# DCIT company list route
@app.route("/dcitCompanyList", methods=(['GET']))
@login_required
def dcitCompanyList():
    asgs = Business.query.all()
    return render_template("dcit-companylist.html", registered_companies=asgs)


# DCIT Intern List
@app.route("/dcit-shortlist", methods=(['GET']))
@login_required
def dcitInternList():
    businesses = Business.query.all()
    student = Student.query.order_by(Student.gpa.desc()).all()  # Filter for best student - sorts by GPA
    internships = Internship.query.all()
    studnts = Student.query.all()
    # Counts
    num_interns = 0
    # Checks
    l_check = False
    db_check = False
    de_check = False

    temp = []

    for business in businesses:
        if num_interns < business.num_interns:  # Move on to the next company if number of required interns is met
            internlist = []
            i = 0
            # Filtering for Fully Qualified
            if student[i].language == business.language:
                l_check = True
            if student[i].dbms == business.dbms:
                db_check = True
            if student[i].design == business.design:
                de_check = True
            if l_check == True & db_check == True & de_check == True:
                new_intern = ShortList(internID=student[i].studentID, intern_name=student[i].name,
                                       companyID=business.businessID,
                                       company_name=business.bname,
                                       proj_name=internships[business.businessID].proj_name)
                db.session.add(new_intern)
                db.session.commit()
                internlist.append(student[i].name)
                i = i + 1
            # Filtering for Overly Qualified

            set1 = set(list(business.language))
            set2 = set(student[i].language)
            set3 = set(list(business.dbms))
            set4 = set(student[i].dbms)
            set5 = set(list(business.design))
            set6 = set(student[i].design)

            if set1.issubset(set2):
                l_check = True
            if set3.issubset(set4):
                db_check = True
            if set5.issubset(set6):
                de_check = True
            if l_check == True & db_check == True & de_check == True:
                new_intern = Shortlist(internID=student[i].uwiid, intern_name=student[i].name,
                                       companyID=business.businessID,
                                       company_name=business.bname,
                                       proj_name=internships[business.businessID].proj_name)
                db.session.add(new_intern)
                db.session.commit()
                internlist.append(student[i].name)
                i = i + 1

            # Filtering for Barely Qualified
            if set1.intersection(set2):
                l_check = True
            if set3.intersection(set4):
                db_check = True
            if set5.intersection(set6):
                de_check = True
            if l_check == True & db_check == True & de_check == True:
                new_intern = Shortlist(internID=student[i].uwiid, intern_name=student[i].name,
                                       companyID=business.businessID,
                                       company_name=business.bname,
                                       proj_name=internships[business.businessID - 1].proj_name)
                db.session.add(new_intern)
                db.session.commit()
                internlist.append(student[i].name)
                i = i + 1
        else:
            continue
        # print("Business Name: ", business.bname)
        # print(internlist)
        num_interns = num_interns + 1

        temp.append(internlist)
        temp.insert(0, 'NULL')
        temps = []

    return render_template("dcit-shortlist.html", temps=temp.copy(), businesses=businesses, interns=internships,
                           studnts=students)

# STUDENT ROUTES
# Student home route
@app.route("/studentHome", methods=(['GET']))
@login_required
def studentHome():
    return render_template("student-homepage.html")


# Student Contact route
@app.route("/studentContact", methods=(['GET']))
@login_required
def studentContact():
    return render_template("student-contact.html")


# Student Internships route
@app.route("/studentInternship", methods=(['GET']))
@login_required
def studentInternship():
    return render_template("student-internships.html")


# Student View Deadlines Route
@app.route("/studentDeadlines", methods=(['GET']))
@login_required
def studentDeadlines():
    asgs = Deadlines.query.all()
    admin_list = DCITAdmin.query.all()
    return render_template("student-deadlines.html", deadlines=asgs, admin_list=admin_list)


# Student Registration route
@app.route("/studentRegistration")
@login_required
def studentRegistration():
    return render_template("student-registration.html")


# Student Weekly Status Report route1
@app.route("/studentWeeklyReport")
def studentWeeklyReport():
    return render_template("student-weeklyreports.html")


# Student Weekly Status Report route2 for iframe form
@app.route("/displayStudentWeeklyReport", methods=(['GET', 'POST']))
def displayStudentWeeklyReport():
    if request.method == 'GET':
        return render_template("student-weeklyreport-form.html")

    elif request.method == 'POST':
        student_id = request.form.get('s_id')
        proj_name = request.form.get('pname')
        date = request.form.get('date')
        py_date = datetime.strptime(date, '%Y-%m-%d')
        iteration = request.form.get('iteration_no')
        imp_stat = request.form.get('impl_status')
        highlts = request.form.get('highlights')

        risk_name = request.form.get('risk')
        risk_desc = request.form.get('description')
        risk_res = request.form.get('resolution')
        risk_status = request.form.get('risk_status')

        task_name = request.form.get('task_name1')
        task_desc = request.form.get('task_descript1')
        task_member = request.form.get('team_member1')
        task_comp = request.form.get('completed')

        task_name_iter = request.form.get('task_name')
        task_desc_iter = request.form.get('task_descript')
        task_member_iter = request.form.get('team_member')

        new_report = Report(rep_studentID=student_id, rep_proj_name=proj_name, date=py_date, iteration=iteration,
                            status=imp_stat, highlights=highlts, risk_name=risk_name, risk_desc=risk_desc,
                            risk_res=risk_res, risk_status=risk_status, task_name=task_name, task_desc=task_desc,
                            task_member=task_member, task_comp=task_comp, task_name_iter=task_name_iter,
                            task_desc_iter=task_desc_iter, task_member_iter=task_member_iter)

        try:
            db.session.add(new_report)
            db.session.commit()
            return render_template("student-homepage.html")
        except IntegrityError:
            return render_template("student-weeklyreport-form.html"), 400
    return


# Student Display Student form route
class students:
    def __init__(self):
        self.tech = self.Tech()

    class Tech:
        def __init__(self):
            self.design = []
            self.dbms = []
            self.language = []

        def compareList(self, studentID):
            student_courses = []
            student_id = studentID
            parsed_data_file = open("parsed_files/" + student_id + "_parsed.txt", "r")
            parsed_dict = json.load(parsed_data_file)
            for key in parsed_dict:
                if parsed_dict[key] == "B-" or parsed_dict[key] == "B" or parsed_dict[key] == "B+" or \
                        parsed_dict[key] == "A-" or parsed_dict[key] == "A" or parsed_dict[key] == "A+":
                    str_key = str(key)
                    student_courses.append(key)

            print(student_courses)

            list_length = len(student_courses)

            design = []
            dbms = []
            language = []

            for i in range(list_length):
                if student_courses[i] == "comp2602":
                    language.append("Python")
                elif student_courses[i] == "comp2603":
                    language.append("Java")
                elif student_courses[i] == "comp2604":
                    language.append("C"), language.append("C++")
                elif student_courses[i] == "comp2605":
                    language.append("SQL")
                    dbms.append("MySQL"), dbms.append("Oracle")
                elif student_courses[i] == "comp2611":
                    language.append("C++"), language.append("Python")
                elif student_courses[i] == "comp3603":
                    design.append("Web")
                elif student_courses[i] == "comp3605":
                    language.append("Python")
                elif student_courses[i] == "comp3606":
                    language.append("Java")
                    design.append("Mobile")
                elif student_courses[i] == "comp3607":
                    language.append("Java")
                elif student_courses[i] == "comp3608":
                    language.append("MiniZinc"), language.append("Python")
                elif student_courses[i] == "comp3609":
                    language.append("Java")
                elif student_courses[i] == "comp3610":
                    language.append("SQL")
                    dbms.append("NoSQL")
                elif student_courses[i] == "comp3613":
                    language.append("Python"), language.append("HTML"), language.append("JavaScript")
                    design.append("Web"), design.append("CSS"), design.append("SASS")
                    dbms.append("MySQL"), dbms.append("Oracle"), dbms.append("MongoDB")
                elif student_courses[i] == "info2601":
                    language.append("Python")
                    design.append("Networking")
                elif student_courses[i] == "info2602":
                    language.append("JavaScript"), language.append("CSS"), language.append(
                        "Flask-Python"), language.append("Python")
                    design.append("Web")
                    dbms.append("MySQL"), dbms.append("Oracle"), dbms.append("MongoDB")
                elif student_courses[i] == "info2603":
                    language.append("Python")
                    design.append("Networking")
                elif student_courses[i] == "info2604":
                    language.append("Python")
                    design.append("Networking")
                elif student_courses[i] == "info3600":
                    language.append("Visual Basic")
                    dbms.append("Microsoft Access (Excel)")
                elif student_courses[i] == "info3602":
                    language.append("JavaScript"), language.append("HTML")
                    language.append("CSS"), language.append("SASS")
                elif student_courses[i] == "info3604":
                    language.append("Python"), language.append("Flask-Python"), language.append(
                        "React"), language.append("HTML"), language.append(
                        "Machine-Learning"), language.append(
                        "JavaScript")
                    design.append("CSS"), design.append("SASS")
                    dbms.append("MySQL"), dbms.append("Oracle"), dbms.append("MongoDB")
                elif student_courses[i] == "info3605":
                    language.append("Python")
                    design.append("Networking")
                elif student_courses[i] == "info3606":
                    language.append("Cloud")
                    dbms.append("IBM"), dbms.append("Cloud")  # Check this
                elif student_courses[i] == "info3608":
                    language.append("PHP"), language.append("HTML"), language.append("WordPress")
                    design.append("CSS"), design.append("Web")
                    dbms.append("phpMyAdmin"), dbms.append("Xampp")
                elif student_courses[i] == "info3611":
                    language.append("SQL")
                    dbms.append("MySQL"), dbms.append("Oracle")

            list(dict.fromkeys(design))
            list(dict.fromkeys(dbms))
            list(dict.fromkeys(language))
            test = students()
            test.tech.design = design
            test.tech.dbms = dbms
            test.tech.language = language

            return test


@app.route("/displayStudentForm", methods=(['GET', 'POST']))
def displayStudentForm():
    if request.method == 'GET':
        return render_template("student-registration-form.html")

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
        photo.save(os.path.join("static/images/student_pictures", uwiid + "_photo.jpg"))

        filename = (uwiid + "_transcript.pdf")
        url = "https://ark-parser.herokuapp.com/parse"
        ajax_send = {'file': open("uploads/" + filename, "rb")}
        parsed = requests.post(url, files=ajax_send)

        parse_save = open("parsed_files/" + uwiid + "_parsed.txt", "w")
        parse_save.write(parsed.text)
        parse_save.close()

        outer = students()
        outer = outer.tech.compareList(uwiid)
        # print(outer.tech.language, outer.tech.design, outer.tech.dbms)

        if student is None and transcript.filename != '' and resume.filename != '' and essay.filename != '':
            parsed_data = open("parsed_files/" + uwiid + "_parsed.txt", "r")
            parsed_data = json.load(parsed_data)
            for key in parsed_data:
                if key == "id":
                    _id = parsed_data[key]
                if key == "gpa":
                    _gpa = parsed_data[key]
                if key == "comp2601":
                    _comp2601 = parsed_data[key]
                if key == "comp2602":
                    _comp2602 = parsed_data[key]
                if key == "comp2603":
                    _comp2603 = parsed_data[key]
                if key == "comp2604":
                    _comp2604 = parsed_data[key]
                if key == "comp2605":
                    _comp2605 = parsed_data[key]
                if key == "comp2606":
                    _comp2606 = parsed_data[key]
                if key == "comp2611":
                    _comp2611 = parsed_data[key]
                if key == "comp3601":
                    _comp3601 = parsed_data[key]
                if key == "comp3602":
                    _comp3602 = parsed_data[key]
                if key == "comp3603":
                    _comp3603 = parsed_data[key]
                if key == "comp3605":
                    _comp3605 = parsed_data[key]
                if key == "comp3606":
                    _comp3606 = parsed_data[key]
                if key == "comp3607":
                    _comp3607 = parsed_data[key]
                if key == "comp3608":
                    _comp3608 = parsed_data[key]
                if key == "comp3609":
                    _comp3609 = parsed_data[key]
                if key == "comp3610":
                    _comp3610 = parsed_data[key]
                if key == "comp3611":
                    _comp3611 = parsed_data[key]
                if key == "comp3612":
                    _comp3612 = parsed_data[key]
                if key == "comp3613":
                    _comp3613 = parsed_data[key]
                if key == "info2600":
                    _info2600 = parsed_data[key]
                if key == "info2601":
                    _info2601 = parsed_data[key]
                if key == "info2602":
                    _info2602 = parsed_data[key]
                if key == "info2603":
                    _info2603 = parsed_data[key]
                if key == "info2604":
                    _info2604 = parsed_data[key]
                if key == "info2605":
                    _info2605 = parsed_data[key]
                if key == "info3600":
                    _info3600 = parsed_data[key]
                if key == "info3601":
                    _info3601 = parsed_data[key]
                if key == "info3602":
                    _info3602 = parsed_data[key]
                if key == "info3604":
                    _info3604 = parsed_data[key]
                if key == "info3605":
                    _info3605 = parsed_data[key]
                if key == "info3606":
                    _info3606 = parsed_data[key]
                if key == "info3607":
                    _info3607 = parsed_data[key]
                if key == "info3608":
                    _info3608 = parsed_data[key]
                if key == "info3609":
                    _info3609 = parsed_data[key]
                if key == "info3610":
                    _info3610 = parsed_data[key]
                if key == "info3611":
                    _info3611 = parsed_data[key]

            new_parsed = parsed_courses(id=_id, gpa=_gpa, comp2601=_comp2601, comp2602=_comp2602, comp2603=_comp2603,
                                        comp2604=_comp2604, comp2605=_comp2605, comp2606=_comp2606, comp2611=_comp2611,
                                        comp3601=_comp3601, comp3602=_comp3602, comp3603=_comp3603, comp3605=_comp3605,
                                        comp3606=_comp3606, comp3607=_comp3607, comp3608=_comp3608, comp3609=_comp3609,
                                        comp3610=_comp3610, comp3611=_comp3611, comp3612=_comp3612, comp3613=_comp3613,
                                        info2600=_info2600, info2601=_info2601, info2602=_info2602, info2603=_info2603,
                                        info2604=_info2604, info2605=_info2605, info3600=_info3600, info3601=_info3601,
                                        info3602=_info3602, info3604=_info3604, info3605=_info3605, info3606=_info3606,
                                        info3607=_info3607, info3608=_info3608, info3609=_info3609, info3610=_info3610,
                                        info3611=_info3611)

            new_student = Student(name=name, email=email, gpa=_gpa, uwiid=uwiid, country=country,
                                  year_of_study=year_of_study, credits=credit, enrollment=enrollment,
                                  curr_degree=curr_degree, transcript=(uwiid + "_transcript.pdf"),
                                  resume=(uwiid + "_resume.pdf"), essay=(uwiid + "_essay.pdf"),
                                  photo=(uwiid + "_photo.jpg"), language=str(outer.tech.language),
                                  design=str(outer.tech.design),
                                  dbms=str(outer.tech.dbms))

            try:
                db.session.add(new_student)
                db.session.add(new_parsed)
                db.session.commit()
                return redirect(url_for('studentHome'))
            except IntegrityError:
                return 'Application does not exist', render_template("student-registration.html"), 400
        return


# BUSINESS ROUTES
# Business Home route
@app.route("/businessHome", methods=(['GET']))
# @login_required
def businessHome():
    return render_template("business-homepage.html")


# Business Registration form route
@app.route("/businessRegistration")
def businessRegistration():
    return render_template("business-registration.html")


# Display Business Form route
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
                # return render_template('business-homepage.html')
                return redirect(url_for('displayBusinessForm'))
            except IntegrityError:
                return 'Application does not exist', render_template("business-registration.html"), 400
    return


@app.route("/oops")
def error():
    return render_template("error.html")


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('signup.html')


@app.route("/logout", methods=(['GET']))
@login_required
def logout():
    logout_user()
    return render_template('landing-page.html')
