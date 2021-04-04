from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# Model for User
class User(db.Model, UserMixin, ):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    occupation = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def toDict(self):
        return {
            "User Id": self.id,
            "User Name": self.name,
            "Email": self.email,
            "Occupation": self.occupation,
            "password": self.password
        }

    # hashes the password parameter and stores it in the object
    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    # Returns true if the parameter is equal to the object's password property
    def check_password(self, password):
        return check_password_hash(self.password, password)

    # To String method
    def _repr_(self):
        return '< User Id {}>'.format(self.id)

    @property
    def is_authenticated(self):
        return True


class Student(db.Model, UserMixin, ):
    studentID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    uwiid = db.Column(db.Integer, unique=True, nullable=False)
    country = db.Column(db.String(120), nullable=False)
    curr_degree = db.Column(db.String(120), nullable=False)
    year_of_study = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    enrollment = db.Column(db.String(120), nullable=False)

    transcript = db.Column(db.String(120), nullable=False)
    resume = db.Column(db.String(120), nullable=False)
    essay = db.Column(db.String(120), nullable=False)
    photo = db.Column(db.String(120), nullable=False)
    language = db.Column(db.String(300), nullable=True)
    design = db.Column(db.String(300), nullable=True)
    dbms = db.Column(db.String(300), nullable=True)

    def toDict(self):
        return {
            "Student ID": self.studentID,
            "Name": self.name,
            "Email": self.email,
            "uwiid": self.uwiid,
            "Country": self.country,
            "Current Degree": self.curr_degree,
            "Year of Study": self.year_of_study,
            "Credits": self.credits,
            "Enrollment": self.enrollment,
            "Transcript": self.transcript,
            "Resume": self.resume,
            "Essay": self.essay,
            "Photo": self.photo,
            "Languages": self.language,
            "Design ": self.design,
            "Database Management Systems": self.dbms
        }


class Business(db.Model, UserMixin, ):
    businessID = db.Column(db.Integer, primary_key=True)
    bname = db.Column(db.String(120), nullable=False)
    num_interns = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    stipend = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(300), nullable=False)
    design = db.Column(db.String(300), nullable=False)
    dbms = db.Column(db.String(300), nullable=False)
    soft_skills = db.Column(db.String(300), nullable=False)

    def toDict(self):
        return {
            "Business ID": self.businessID,
            "Name": self.bname,
            "Number of Interns": self.num_interns,
            "Duration": self.duration,
            "Credits": self.credits,
            "Stipend": self.stipend,
            "Languages Required": self.language,
            "Design knowledge": self.design,
            "Database Management Systems": self.dbms,
            "Soft Skills": self.soft_skills

        }


class DCIT_Admin(db.Model, UserMixin, ):
    adminID = db.Column(db.Integer, primary_key=True)
    aname = db.Column(db.String(120), nullable=False)
    aemail = db.Column(db.String(120), unique=True, nullable=False)

    def toDict(self):
        return {
            "Admin ID": self.adminID,
            "Name": self.aname,
            "Email": self.aemail
        }


class Internship(db.Model, UserMixin, ):
    internshipID = db.Column(db.Integer, primary_key=True)
    proj_name = db.Column(db.String(120), nullable=False)
    proj_descript = db.Column(db.String(300), nullable=False)
    activities = db.Column(db.String(300), nullable=False)
    business_ID = db.Column(db.Integer, db.ForeignKey('business.businessID'), nullable=False)

    def toDict(self):
        return {
            "Internship ID": self.businessID,
            "Project Name": self.proj_name,
            "Project Description": self.proj_descript,
            "Activities": self.activities,
            "Business ID": self.business_ID

        }


class Report(db.Model, UserMixin):
    reportID = db.Column(db.Integer, primary_key=True)
    rep_proj_name = db.Column(db.String(120), db.ForeignKey('internship.proj_name'), nullable=False)
    rep_studentID = db.Column(db.Integer, db.ForeignKey('student.uwiid'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    iteration = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(120), nullable=False)
    date_entered = db.Column(db.DateTime, nullable=False)

    def toDict(self):
        return {
            "Report ID": self.reportID,
            "Project Name": self.rep_proj_name,
            "Student ID": self.rep_studentID,
            "Date": self.date,
            "Iteration": self.iteration,
            "Status": self.status,
            "Date Entered": self.date_entered
        }


class Risk(db.Model, UserMixin):
    riskID = db.Column(db.Integer, primary_key=True)
    risk_des = db.Column(db.String(300), nullable=False)
    risk_status = db.Column(db.String(300), nullable=False)
    risk_repID = db.Column(db.Integer, db.ForeignKey('report.reportID'), nullable=False)

    def toDict(self):
        return {
            "Risk ID": self.riskID,
            "Risk Description": self.risk_des,
            "Risk Status": self.risk_status,
            "Report ID": self.risk_repID
        }


class Task(db.Model, UserMixin, ):
    taskID = db.Column(db.Integer, primary_key=True)
    task_des = db.Column(db.String(300), nullable=False)
    task_member = db.Column(db.String(300), nullable=False)
    task_complete = db.Column(db.Integer, nullable=True)
    task_repID = db.Column(db.Integer, db.ForeignKey('report.reportID'), nullable=False)

    def toDict(self):
        return {
            "Task ID": self.taskID,
            "Task Description": self.task_des,
            "Task Member": self.task_member,
            "Percentage Completed": self.task_complete,
            "Report ID": self.task_repID
        }


class parsed_courses(db.Model, UserMixin, ):
    id = db.Column(db.Integer, primary_key=True)
    gpa = db.Column(db.Integer, nullable=False)
    comp2601 = db.Column(db.String(10), nullable=True)
    comp2602 = db.Column(db.String(10), nullable=True)
    comp2603 = db.Column(db.String(10), nullable=True)
    comp2604 = db.Column(db.String(10), nullable=True)
    comp2605 = db.Column(db.String(10), nullable=True)
    comp2606 = db.Column(db.String(10), nullable=True)
    comp2611 = db.Column(db.String(10), nullable=True)
    comp3601 = db.Column(db.String(10), nullable=True)
    comp3602 = db.Column(db.String(10), nullable=True)
    comp3603 = db.Column(db.String(10), nullable=True)
    comp3605 = db.Column(db.String(10), nullable=True)
    comp3606 = db.Column(db.String(10), nullable=True)
    comp3607 = db.Column(db.String(10), nullable=True)
    comp3608 = db.Column(db.String(10), nullable=True)
    comp3609 = db.Column(db.String(10), nullable=True)
    comp3610 = db.Column(db.String(10), nullable=True)
    comp3611 = db.Column(db.String(10), nullable=True)
    comp3612 = db.Column(db.String(10), nullable=True)
    comp3613 = db.Column(db.String(10), nullable=True)

    info2600 = db.Column(db.String(10), nullable=True)
    info2601 = db.Column(db.String(10), nullable=True)
    info2602 = db.Column(db.String(10), nullable=True)
    info2603 = db.Column(db.String(10), nullable=True)
    info2604 = db.Column(db.String(10), nullable=True)
    info2605 = db.Column(db.String(10), nullable=True)
    info3600 = db.Column(db.String(10), nullable=True)
    info3601 = db.Column(db.String(10), nullable=True)
    info3602 = db.Column(db.String(10), nullable=True)
    info3604 = db.Column(db.String(10), nullable=True)
    info3605 = db.Column(db.String(10), nullable=True)
    info3606 = db.Column(db.String(10), nullable=True)
    info3607 = db.Column(db.String(10), nullable=True)
    info3608 = db.Column(db.String(10), nullable=True)
    info3609 = db.Column(db.String(10), nullable=True)
    info3610 = db.Column(db.String(10), nullable=True)
    info3611 = db.Column(db.String(10), nullable=True)

    def toDict(self):
        return {
            "ID": self.id,
            "GPA": self.gpa,
            "COMP 2601": self.comp2601,
            "COMP 2602": self.comp2602,
            "COMP 2603": self.comp2603,
            "COMP 2604": self.comp2604,
            "COMP 2605": self.comp2605,
            "COMP 2606": self.comp2606,
            "COMP 2611": self.comp2611,
            "COMP 3601": self.comp3601,
            "COMP 3602": self.comp3602,
            "COMP 3603": self.comp3603,
            "COMP 3605": self.comp3605,
            "COMP 3606": self.comp3606,
            "COMP 3607": self.comp3607,
            "COMP 3608": self.comp3608,
            "COMP 3609": self.comp3609,
            "COMP 3610": self.comp3610,
            "COMP 3611": self.comp3611,
            "COMP 3612": self.comp3612,
            "COMP 3613": self.comp3613,

            "INFO 2600": self.info2600,
            "INFO 2601": self.info2601,
            "INFO 2602": self.info2602,
            "INFO 2603": self.info2603,
            "INFO 2604": self.info2604,
            "INFO 2605": self.info2605,
            "INFO 3600": self.info3600,
            "INFO 3601": self.info3601,
            "INFO 3602": self.info3602,
            "INFO 3604": self.info3604,
            "INFO 3605": self.info3605,
            "INFO 3606": self.info3606,
            "INFO 3607": self.info3607,
            "INFO 3608": self.info3608,
            "INFO 3609": self.info3609,
            "INFO 3610": self.info3610,
            "INFO 3611": self.info3611

        }
