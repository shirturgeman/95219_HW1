import unittest
from flask import url_for, current_app
from io import BytesIO
from website import create_app, db
from website.models import User
from unittest.mock import patch

class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.create_test_user()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_user(self):
        user = User(email='test@example.com', first_name='Test', password='password')
        db.session.add(user)
        db.session.commit()

    def login_test_user(self):
        return self.client.post('/login', data=dict(email='test@example.com', password='password'), follow_redirects=True)

    @patch('website.app.classify_image', return_value={'result': {'classification': 'cat', 'score': 0.95}, 'image_path': 'static/uploads/test_image.jpg'})
    def test_upload_image(self, mock_classify_image):
        with self.app.app_context():
            self.login_test_user()

            data = {
                'file': (BytesIO(b'test image content'), 'test_image.jpg'),
                'question': 'What is this image?'
            }

            with self.client:
                response = self.client.post(url_for('_app.upload_file'), content_type='multipart/form-data', data=data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)

                response_data = response.get_data(as_text=True)
                self.assertIn('Classification Result', response_data)
                self.assertIn('cat', response_data)
                self.assertIn('0.95', response_data)

    def test_get_result(self):
        with self.app.app_context():
            self.login_test_user()

            request_id = 1
            result_data = {'result': {'classification': 'dog', 'score': 0.85}, 'image_path': 'static/uploads/dog_image.jpg'}

            # Simulate the result being in the global request_results
            global request_results
            request_results[request_id] = result_data

            with self.client:
                response = self.client.get(url_for('_app.get_result', request_id=request_id))
                self.assertEqual(response.status_code, 200)

                response_data = response.get_data(as_text=True)
                self.assertIn('Classification Result', response_data)
                self.assertIn('dog', response_data)
                self.assertIn('0.85', response_data)

    @patch('website.app.classify_image', return_value={'result': {'classification': 'dog', 'score': 0.85}, 'image_path': 'static/uploads/test_image.jpg'})
    def test_upload_image_large_file(self, mock_classify_image):
        with self.app.app_context():
            self.login_test_user()

            large_file_content = b'x' * (1024 * 1024 * 10)  # 10 MB file
            data = {
                'file': (BytesIO(large_file_content), 'large_test_image.jpg'),
                'question': 'What is this image?'
            }

            with self.client:
                response = self.client.post(url_for('_app.upload_file'), content_type='multipart/form-data', data=data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)

                response_data = response.get_data(as_text=True)
                self.assertIn('Classification Result', response_data)
                self.assertIn('dog', response_data)
                self.assertIn('0.85', response_data)

    def test_upload_invalid_file_type(self):
        with self.app.app_context():
            self.login_test_user()

            data = {
                'file': (BytesIO(b'test image content'), 'test_image.txt'),
                'question': 'What is this image?'
            }

            with self.client:
                response = self.client.post(url_for('_app.upload_file'), content_type='multipart/form-data', data=data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)

                response_data = response.get_json()
                self.assertEqual(response_data['message'], 'Allowed file types are png, jpg, jpeg, gif')

    def test_upload_no_file(self):
        with self.app.app_context():
            self.login_test_user()

            data = {
                'question': 'What is this image?'
            }

            with self.client:
                response = self.client.post(url_for('_app.upload_file'), content_type='multipart/form-data', data=data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)

                response_data = response.get_json()
                self.assertEqual(response_data['message'], 'No file part')

    def test_upload_no_selected_file(self):
        with self.app.app_context():
            self.login_test_user()

            data = {
                'file': (BytesIO(b''), ''),
                'question': 'What is this image?'
            }

            with self.client:
                response = self.client.post(url_for('_app.upload_file'), content_type='multipart/form-data', data=data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)

                response_data = response.get_json()
                self.assertEqual(response_data['message'], 'No selected file')

    def test_upload_image_invalid_extension(self):
        with self.app.app_context():
            self.login_test_user()

            data = {
                'file': (BytesIO(b'test image content'), 'test_image.bmp'),
                'question': 'What is this image?'
            }

            with self.client:
                response = self.client.post(url_for('_app.upload_file'), content_type='multipart/form-data', data=data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)

                response_data = response.get_json()
                self.assertEqual(response_data['message'], 'Allowed file types are png, jpg, jpeg, gif')

    def test_upload_image_with_no_question(self):
        with self.app.app_context():
            self.login_test_user()

            data = {
                'file': (BytesIO(b'test image content'), 'test_image.jpg'),
                'question': ''
            }

            with self.client:
                response = self.client.post(url_for('_app.upload_file'), content_type='multipart/form-data', data=data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)

                response_data = response.get_data(as_text=True)
                self.assertIn('Classification Result', response_data)  # Ensuring that even without a question, we get a result

    def test_get_result_for_non_existent_request_id(self):
        with self.app.app_context():
            self.login_test_user()

            with self.client:
                response = self.client.get(url_for('_app.get_result', request_id=9999))
                self.assertEqual(response.status_code, 404)

                response_data = response.get_json()
                self.assertEqual(response_data['error']['message'], 'ID not found')

    def test_status_endpoint(self):
        with self.app.app_context():
            response = self.client.get('/status')
            self.assertEqual(response.status_code, 200)

            status_data = response.get_json()
            self.assertIn('uptime', status_data)
            self.assertIn('processed', status_data)
            self.assertIn('health', status_data)
            self.assertIn('api_version', status_data)
            self.assertEqual(status_data['api_version'], 1)

if __name__ == '__main__':
    unittest.main()
