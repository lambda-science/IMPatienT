import json
import os
import sys
import unittest

topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

from impatient.app import create_app, db
from impatient.app.historeport.onto_func import StandardVocabulary
from impatient.config import Config


class TestConfig(Config):
    """Basic App configuration for testing environnement"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SECRET_KEY = "testingsecretkey"
    WTF_CSRF_ENABLED = False


class HistoReportCase(unittest.TestCase):
    """Class for text report module case"""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.client = self.app.test_client()
        self.app_context.push()
        db.create_all()
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
        assert b"digitize a new report" in rv.data

    def test_update_from_template(self):
        report = StandardVocabulary(
            json.load(open("tests/data/sample_historeport.json", "r"))
        )
        template = StandardVocabulary(
            json.load(open("tests/data/sample_template.json", "r"))
        )
        result = report.update_ontology(template)
        node_names = [i["text"] for i in result]
        assert "OUTDATED : Fibre Type 1" in node_names
        assert "Created Node 1" in node_names
        assert "Modified Node 1" in node_names
