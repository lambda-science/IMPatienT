import unittest
import os
import sys
import json

topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

from app import create_app, db
from app.models import User
from app.historeport.onto_func import Ontology
from config import Config


class TestConfig(Config):
    """Basic App configuration for testing environnement"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SECRET_KEY = "testingsecretkey"
    WTF_CSRF_ENABLED = False


class HistoReportCase(unittest.TestCase):
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

    def test_histo_report_index(self):
        rv = self.client.get("/historeport")
        assert rv.status_code == 200
        assert b"Create a Histo Report" in rv.data

    def test_update_from_template(self):
        report = Ontology(json.load(open("tests/data/sample_historeport.json", "r")))
        template = Ontology(json.load(open("tests/data/sample_template.json", "r")))
        result = report.update_ontology(template)
        node_names = [i["text"] for i in result]
        assert "OUTDATED : Fibre Type 1" in node_names
        assert "Created Node 1" in node_names
        assert "Modified Node 1" in node_names
