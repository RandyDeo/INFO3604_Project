from main import db, User, Student, Business, Internship, Report, DCITAdmin, Shortlist, Deadlines, app
import csv

db.create_all(app=app)

with open("database.csv", mode="w") as database:
    account_writer = csv.writer(database, delimiter=",", quotechar='"')

    account_writer.writerow([User.id, User.email, User.password])

    db.session.commit()
    print("Database Initialized!")

