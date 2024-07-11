import unittest
from unittest.mock import patch, MagicMock
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from website import create_app, db

class InitTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.DB_NAME = "database.db"

    def tearDown(self):
        self.app_context.pop()
        if os.path.exists('tests/' + self.DB_NAME):
            os.remove('tets/' + self.DB_NAME)

    def test_app_initialization_key(self):
        self.assertIsInstance(self.app, Flask)
        self.assertEqual(self.app.config['SECRET_KEY'], 'hjshjhdjah kjshkjdhjs')

    def test_blueprints_registration(self):
        auth_blueprint = [bp for bp in self.app.blueprints.values() if bp.name == 'auth']
        app_blueprint = [bp for bp in self.app.blueprints.values() if bp.name == '_app']
        self.assertTrue(len(auth_blueprint) > 0)
        self.assertTrue(len(app_blueprint) > 0)

    def test_login_manager_setup(self):
        with self.app.app_context():
            login_manager = self.app.login_manager
            self.assertIsNotNone(login_manager)

if __name__ == '__main__':
    unittest.main()