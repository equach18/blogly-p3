from unittest import TestCase

from app import app
from models import db, User, Post

# Use test database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_app'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


with app.app_context():
    db.drop_all()
    db.create_all()

class UserViewsTestCase(TestCase):
    """Tests for views for Users."""

    def setUp(self):
        """Remove any existing users and provide sample ones"""
        with app.app_context():
            User.query.delete()

            user = User(first_name="Paul", last_name="Smith", image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQdztTDcpZ2pFqwWDYwSXbvZq5nzJYg5cn8w&s")
            db.session.add(user)
            db.session.commit()

            self.id = user.id
    
    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()

    def test_list_users(self):
        """Tests that the list of users is correctly displayed"""
        with app.test_client() as client:
            response = client.get("/users")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Paul', html)

    def test_show_user_info(self):
        """Tests to if the user info is correctly displayed"""
        with app.test_client() as client:
            response = client.get(f"/users/{self.id}")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<h1>Paul Smith</h1>', html)

    def test_add_user(self):
        """Test adding a user through the form."""
        with app.test_client() as client:
            data = {
                'first-name': 'John',
                'last-name': 'Doe',
                'img-url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtuphMb4mq-EcVWhMVT8FCkv5dqZGgvn_QiA&s'
            }
            response = client.post('/users/new', data=data, follow_redirects=True)
            html = response.get_data(as_text=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("John Doe</a></li>", html)
        
        # Check the database
        with app.app_context():
            user = User.query.filter_by(first_name='John', last_name='Doe').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.first_name, 'John')
            self.assertEqual(user.last_name, 'Doe')

    def test_delete_user(self):
        """Tests to see if the user was deleted from the database and is not showing on the page."""
        with app.test_client() as client:
            response = client.post(f"/users/{self.id}/delete", follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            user = User.query.filter_by(first_name='John', last_name='Doe').first()
            self.assertIsNone(user)
            
