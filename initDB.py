from main import db, Student, FileContents, app
import csv

db.create_all(app=app)

with open("database.csv", mode="w") as database:
    account_writer = csv.writer(database, delimiter=",", quotechar='"')

    account_writer.writerow([Student.studentId, Student.email, Student.password])

    db.session.commit()
    print("Database Initialized!")
