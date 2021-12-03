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


class IndexView(unittest.TestCase):
    """Class for the index page test case"""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.client = self.app.test_client()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_index(self):
        rv = self.client.get("/")
        assert rv.status_code == 200
        assert b"EHRoes" in rv.data
