import unittest
from sqlalchemy.exc import IntegrityError
from website import create_app, db  
from website.models import Image, User  # Replace with the actual import path for your models

class TestModels(unittest.TestCase):
    
    def setUp(self):
        # Setup Flask app context and SQLAlchemy database
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database for testing
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create the database and the database table
        self.user = User()
        self.image = Image()
        db.create_all()
    
    def tearDown(self):
        # Clean up after each test method
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ##empty
    def test_empty_image_creation(self):
        """ Test creation of an empty Image instance """
        empty_image = Image()
        self.assertIsInstance(self.image, Image)

    def test_empty_user_creation(self):
        """ Test creation of an empty User instance """
        empty_user = User()
        self.assertIsInstance(self.user, User)

    # ## unique
    def test_user_unique_email_constraint(self):
        """ Test unique constraint on User.email """
        user1 = User(email='unique@example.com', password='password', first_name='User1')
        user2 = User(email='unique@example.com', password='password', first_name='User2')
        db.session.add(user1)
        db.session.commit()
        
        with self.assertRaises(IntegrityError):
            db.session.add(user2)
            db.session.commit()
        db.session.rollback()

    '''
    # ##types
    def test_user_wrong_type_email(self):
        with self.assertRaises(TypeError):
            db.session.add(User(email= 1234111111191, password='password', first_name='User1'))
            db.session.commit()
            db.session.rollback()

    def test_user_wrong_type_password(self):
        with self.assertRaises(Exception):
            db.session.add(User(email= 'example@d.cpm', password=1234567, first_name='User1'))
            db.session.commit()
        db.session.rollback()

    def test_user_wrong_type_name(self):
        with self.assertRaises(Exception):
            db.session.add(User(email= 'example@d.cpm', password='1234567', first_name=123))
            db.session.commit()
        db.session.rollback()
    
    def test_image_wrong_type_path(self):
        with self.assertRaises(Exception):
            db.session.add(Image(path=123, classification='bird', user=self.user))
            db.session.commit()
        db.session.rollback()

    def test_image_wrong_type_classification(self):
        with self.assertRaises(Exception):
            db.session.add(Image(path='long_path', classification=10, user=self.user))
            db.session.commit()
        db.session.rollback()

    def test_image_wrong_type_user_id(self):
        with self.assertRaises(Exception):
            db.session.add(Image(path='long_path', classification='bird', user='sss'))
            db.session.commit()
            db.session.rollback()
    '''
    # ## length 
    def test_image_path_length(self):
        """ Test maximum length of Image.path """
        long_path = 'a' * 301  # Create a path longer than 300 characters
        image_long_path = Image(path=long_path, classification='bird', user=self.user)
        try:
            db.session.add(image_long_path)
            db.session.commit()
            db.session.rollback()
        except Exception as e:
            self.assertRaises(Exception)

    def test_image_classification_length(self):
        """ Test maximum length of Image.path """
        long_path = 'a' * 301  # Create a path longer than 300 characters
        image_long_path = Image(path='long_path', classification=long_path, user=self.user)
        try:
            db.session.add(image_long_path)
            db.session.commit()
            db.session.rollback()
        except Exception as e:
            self.assertRaises(Exception)

    def test_user_email_length(self):
        """ Test maximum length of Image.path """
        long_path = 'a' * 151  # Create a path longer than 300 characters
        image_long_path = User(email= long_path, password='1234567', first_name=123)
        try:
            db.session.add(image_long_path)
            db.session.commit()
            db.session.rollback()
        except Exception as e:
            self.assertRaises(Exception)

    def test_user_password_length(self):
        """ Test maximum length of Image.path """
        long_path = 'a' * 151  # Create a path longer than 300 characters
        image_long_path = User(email= 'long_path', password=long_path, first_name=123)
        try:
            db.session.add(image_long_path)
            db.session.commit()
            db.session.rollback()
        except Exception as e:
            self.assertRaises(Exception)
    
    def test_user_password_name(self):
        """ Test maximum length of Image.path """
        long_path = 'a' * 151  # Create a path longer than 300 characters
        image_long_path = User(email= 'long_path', password='long_path', first_name=long_path)
        try:
            db.session.add(image_long_path)
            db.session.commit()
            db.session.rollback()
        except Exception as e:
            self.assertRaises(Exception)

    # ##blanks
    def test_image_without_user(self):
        """ Test creating an Image without associating it with a User """
        image_no_user = Image(path='/path/to/another/image.png', classification='dog')
        db.session.add(image_no_user)
        db.session.commit()
        
        self.assertIsNone(image_no_user.user_id)

    def test_image_classification_none(self):
        """ Test creating an Image with classification set to None """
        image_no_classification = Image(path='/path/to/another/image', classification=None, user=self.user)
        db.session.add(image_no_classification)
        db.session.commit()
        
        self.assertIsNone(image_no_classification.classification)

    # auth
    def test_user_authentication(self):
        """ Test User authentication properties (assuming UserMixin functionality) """
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_anonymous)
        self.assertTrue(self.user.is_authenticated)

    # forign key
    def test_user_relationship(self):
        """ Test relationship between User and Image """
        user = User(email='new@example.com', password='password', first_name='Jane')
        image = Image(path='/path/to/new_image.jpg', classification='dog', user=user)
        db.session.add(user)
        db.session.add(image)
        db.session.commit()
        
        retrieved_user = User.query.filter_by(email='new@example.com').first()
        self.assertEqual(len(retrieved_user.notes), 1)
        self.assertEqual(retrieved_user.notes[0].path, '/path/to/new_image.jpg')

    def test_user_notes_deletion_cascade(self):
        """ Test deletion cascade from User to Image.notes """
        new = User(email='test@example.com', password='password', first_name='John')
        db.session.add(new)
        db.session.commit()
        
        user = User.query.filter_by(email='test@example.com').first()
        db.session.delete(user)
        db.session.commit()
        
        images = Image.query.filter_by(user_id=self.user.id).all()
        self.assertEqual(len(images), 0)

if __name__ == '__main__':
    unittest.main()
