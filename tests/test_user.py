import unittest
import os
import sys

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


class UserModelCase(unittest.TestCase):
    """Class for User authentification test case"""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        user = User(username="test")
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
