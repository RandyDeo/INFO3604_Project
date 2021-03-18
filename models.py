from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

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
    transcript = db.Column(db.LargeBinary)
    resume = db.Column(db.LargeBinary)
    essay = db.Column(db.LargeBinary)

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
            "Essay": self.essay
        }


class Business(db.Model, UserMixin, ):
    businessID = db.Column(db.Integer, primary_key=True)
    bname = db.Column(db.String(120), nullable=False)
    num_interns = db.Column(db.Integer, nullable= False)
    duration = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    stipend = db.Column(db.Integer, nullable=False)
    tech_skills = db.Column(db.String(300), nullable=False)
    soft_skills = db.Column(db.String(300), nullable=False)

    def toDict(self):
        return {
            "Business ID": self.businessID,
            "Name": self.bname,
            "Number of Interns": self.num_interns,
            "Duration": self.duration,
            "credits": self.credits,
            "stipend": self.stipend,
            "Technical Skills": self.tech_skills,
            "Soft Skills": self.soft_skills

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
