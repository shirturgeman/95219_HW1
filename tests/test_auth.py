import unittest
from website import create_app, db
from website.models import User
from flask import url_for, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database for testing
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.secret_key = 'test_secret_key' 
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create the database and the database table
        self.user = User()
        db.create_all()
        self.create_test_user()

    def tearDown(self):
        # Clean up after each test method
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def create_test_user(self):
        self.client.post('/sign-up', data=dict(
                    email='test@example.com',
                    firstName='New',
                    password1='password',
                    password2='password'
                ), follow_redirects=True)

    def test_login_success(self):
        response = self.client.post('/login', data=dict(email='test@example.com', password='password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully!', response.data)

    def test_login_incorrect_password(self):
        response = self.client.post('/login', data=dict(email='test@example.com', password='wrongpassword'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect password, try again.', response.data)

    def test_login_non_existent_user(self):
        response = self.client.post('/login', data=dict(email='nonexistent@example.com', password='password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email does not exist.', response.data)

    def test_logout(self):
        self.client.post('/login', data=dict(email='test@example.com', password='password'), follow_redirects=True)
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_success(self):
        with self.client as client:
            response = client.post('/sign-up', data=dict(
                email='newuser@example.com',
                firstName='New',
                password1='newpassword',
                password2='newpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with client.session_transaction() as session:
                flash_messages = get_flashed_messages(with_categories=True)
            self.assertIn(('success', 'Account created!'), flash_messages)

    def test_sign_up_existing_email(self):
        with self.client as client:
            response = client.post('/sign-up', data=dict(
                email='test@example.com',  # Email already exists
                firstName='Test',
                password1='newpassword',
                password2='newpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with client.session_transaction() as session:
                flash_messages = get_flashed_messages(with_categories=True)
            self.assertIn(('error', 'Email already exists.'), flash_messages)

    def test_sign_up_invalid_email(self):
        with self.client as client:
            response = client.post('/sign-up', data=dict(
                email='a@b',
                firstName='Test',
                password1='newpassword',
                password2='newpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with client.session_transaction() as session:
                flash_messages = get_flashed_messages(with_categories=True)
            self.assertIn(('error', 'Email must be greater than 3 characters.'), flash_messages)


    def test_sign_up_invalid_name(self):
        with self.client as client:
            response = client.post('/sign-up', data=dict(
                email='newuser@example.com',
                firstName='A',
                password1='newpassword',
                password2='newpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with client.session_transaction() as session:
                flash_messages = get_flashed_messages(with_categories=True)
            self.assertIn(('error', 'First name must be greater than 1 character.'), flash_messages)


    def test_sign_up_password_mismatch(self):
        with self.client as client:
            response = client.post('/sign-up', data=dict(
                email='newuser@example.com',
                firstName='Test',
                password1='password1',
                password2='password2'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with client.session_transaction() as session:
                flash_messages = get_flashed_messages(with_categories=True)
            self.assertIn(('error', 'Passwords don\'t match.'), flash_messages)

    def test_sign_up_password_short(self):
        with self.client as client:
            response = client.post('/sign-up', data=dict(
                email='newuser@example.com',
                firstName='Test',
                password1='short',
                password2='short'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            with client.session_transaction() as session:
                flash_messages = get_flashed_messages(with_categories=True)
            self.assertIn(('error', 'Password must be at least 7 characters.'), flash_messages)



if __name__ == '__main__':
    unittest.main()
