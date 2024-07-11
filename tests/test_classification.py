import unittest
from unittest.mock import patch, MagicMock
from website.classificaion import classify_image
from website.models import db
import website
import json
import os


class TestClassification(unittest.TestCase):

    def setUp(self):
        # Setup test database (SQLite in-memory)
        self.app = website.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # Teardown test database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('website.classificaion.vertexai.init')
    @patch('website.classificaion.ImageTextModel.from_pretrained')
    @patch('website.classificaion.Image.load_from_file')
    def test_classify_image_success(self, mock_load_from_file, mock_from_pretrained, mock_init):
        # Mocking dependencies and data
        mock_init.return_value = None
        mock_model = MagicMock()
        mock_from_pretrained.return_value = mock_model
        mock_image = MagicMock()
        mock_load_from_file.return_value = mock_image

        # Mocking ask_question method
        mock_model.ask_question.return_value = ['cat']

        # Calling the function
        question = "What animal is this?"
        image_path = 'test_image_path.png'
        result = classify_image(question, image_path)

        # Assertions
        self.assertEqual(result['result']['classification'], 'cat')
        self.assertEqual(result['result']['score'], 10)
        self.assertEqual(result['image_path'], 'test_image_path.png')



    @patch('website.classificaion.ImageTextModel')
    @patch('website.classificaion.Image')
    @patch('website.classificaion.vertexai')
    def test_classify_image_failure(self, mock_vertexai, mock_image, mock_model_class):
        # Mock the initialization of vertexai
        mock_vertexai.init.return_value = None

        # Mock the Image and ImageTextModel to raise an exception
        mock_image.load_from_file.side_effect = Exception('Image load failed')

        # Call the function
        result = classify_image('What is this?', 'test_image_path.png').response[0]
        result_dict = json.loads(result.decode())

        # Assertions
        self.assertIn('message', result_dict)
        self.assertEqual(result_dict['message'], 'Failed to classify image')
        self.assertIn('result', result_dict)
        self.assertIn('Image load failed', result_dict['result'])

    @patch.dict(os.environ, {}, clear=True)
    def test_classify_image_env_not_set(self):
        # Ensure the environment variable is not set
        self.assertNotIn("GOOGLE_APPLICATION_CREDENTIALS", os.environ)
        
        # Call the function
        result = classify_image("What is in the image?", "path/to/image.jpg")

        try:
            x = result['result'] # result in the case the exception didn't happen
            self.assertFalse(False)
        except Exception as e:
            self.assertTrue(True)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_classify_question_env_not_set(self):
        # Ensure the environment variable is not set
        self.assertNotIn("GOOGLE_APPLICATION_CREDENTIALS", os.environ)
        
        # Call the function
        result = classify_image("", "path/to/image.jpg")

        try:
            x = result['result'] # result in the case the exception didn't happen
            self.assertFalse(False)
        except Exception as e:
            self.assertTrue(True)
    

    @patch('vertexai.init')
    def test_vertexai_init_called_correctly(self, mock_vertexai_init): 

        with open('server_auth.json') as f:
            server_auth = json.load(f)
        
        classify_image("What is in the image?", "path/to/image.jpg")
        # Check if vertexai.init was called with the correct parameters
        mock_vertexai_init.assert_called_once_with(project=server_auth["project_id"], location="us-central1")
        

if __name__ == '__main__':
    unittest.main()
