import os
import sys
import unittest

topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

from app import create_app, db
from app.models import User
from config import Config


class TestConfig(Config):
    """Basic App configuration for testing environnement"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SECRET_KEY = "testingsecretkey"
    WTF_CSRF_ENABLED = False


class UserModelCase(unittest.TestCase):
    """Class for User authentification test case"""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.client = self.app.test_client()
        self.app_context.push()
        db.create_all()
        user = User(username="test", email="test@test.test")
        user.set_password("azerty")
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        user = User.query.get(1)
        self.assertFalse(user.check_password("qwerty"))
        self.assertTrue(user.check_password("azerty"))

    def test_reset_token(self):
        user = User.query.get(1)
        token = user.get_reset_password_token()
        assert user == User.verify_reset_password_token(token)
        assert User.verify_reset_password_token("abcd") is None

    def test_login(self):
        rv = self.client.post(
            "/login",
            data=dict(username="test", password="fakepwd"),
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert b"Invalid username or password" in rv.data

        rv = self.client.post(
            "/login",
            data=dict(username="test", password="azerty"),
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert b"Login successful" in rv.data

    def test_logout(self):
        rv = self.client.get("/logout", follow_redirects=True)
        assert rv.status_code == 200
        assert b"You were logged out" in rv.data

    def test_reset_password_request(self):
        rv = self.client.post(
            "/reset_password_request",
            data=dict(email="test@test.test"),
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert b"Check your email" in rv.data

        rv = self.client.post(
            "/reset_password_request",
            data=dict(email="azerty@azerty.azerty"),
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert b"No account found for this email" in rv.data

    def test_reset_password(self):
        user = User.query.get(1)
        token = user.get_reset_password_token()
        rv = self.client.get("/reset_password/" + token, follow_redirects=True)
        assert rv.status_code == 200
        assert b"Reset Your Password" in rv.data

        rv = self.client.post(
            "/reset_password/" + token,
            data=dict(password="qwerty", password2="qwerty"),
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert b"Your password has been reset" in rv.data
        self.assertTrue(user.check_password("qwerty"))
