import unittest
import os
import sys
import shutil
from io import BytesIO

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
        self.client.post(
            "/login",
            data=dict(username="test", password="azerty"),
            follow_redirects=True,
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @classmethod
    def tearDownClass(cls):
        # TODO: Find a way to get app config data folder instead of hard coded
        shutil.rmtree(os.path.join("/data/", "pytest_id"))

    def test_image_page(self):
        rv = self.client.get("/upload_img")
        assert rv.status_code == 200
        assert b"Upload New Image" in rv.data

    def test_image_upload(self):
        with open("tests/data/image.svs", "rb") as file:
            image_content = file.read()
        data = {
            "patient_ID": "pytest_id",
            "patient_nom": "pytest_nom",
            "patient_prenom": "pytest_prenom",
            "image": (BytesIO(image_content), "image.svs"),
        }
        rv = self.client.post("/upload_img", data=data, follow_redirects=True)
        assert rv.status_code == 200
        assert b"Image Viewer" in rv.data
