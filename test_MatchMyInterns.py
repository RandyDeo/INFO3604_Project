import unittest
from unittest import TestCase
from main import db, User, Student, Business, Internship, Report, app


class MatchMyInternsTest(unittest.TestCase):

    def test_valid_login(self):
        test = app.test_client(self)
        response = test.post(
            '/login',
            data=dict(email='randydeo@gmail.com', passw='password'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_wrong_email(self):
        test = app.test_client(self)
        response = test.post(
            '/login',
            data=dict(email='rdydeo@gmail.com', passw='password'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

    def test_wrong_password(self):
        test = app.test_client(self)
        response = test.post(
            '/login',
            data=dict(email='randydeo@gmail.com', passw='passw'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 401)

#It saves the email in db, so if you run twice with same email, it will fail. PUT NEW EMAIL FOR EACH RUN
    def test_valid_signup(self):
        test = app.test_client(self)
        response = test.post(
            '/signup',
            data=dict(email='1@gmail.com', name="John Doe", occupation="Student", passw='password'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 201)

    def test_email_already_exists_signup(self):
        test = app.test_client(self)
        response = test.post(
            '/signup',
            data=dict(email='randydeo@gmail.com', name="John Doe", occupation="Student", passw='password'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 401)

    

