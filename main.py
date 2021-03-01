import json
from flask import Flask, render_template, request
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

from models import db, User

''' Begin boilerplate code '''


def create_app():
    app = Flask("__name__", template_folder="templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
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
    user = models.User.query.filter_by(id =sid).first()
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
    return render_template("index.html")


#@app.route("/upload", methods=['POST'])
#def upload():
 #   file = request.files['inputFile']

  #  newFile = FileContents(name=file.filename, data=file.read())
   # db.session.add(newFile)
    #db.session.commit()

    #return 'Saved ' + file.filename + ' to the database!'
