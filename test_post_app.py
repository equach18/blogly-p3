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
            Post.query.delete()
            User.query.delete()

            user = User(first_name="Paul", last_name="Smith", image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQdztTDcpZ2pFqwWDYwSXbvZq5nzJYg5cn8w&s")
            db.session.add(user)
            db.session.commit()

            self.user_id = user.id
            
            p1 = Post(title="Test title1", content="test", user_id=self.user_id)
            p2 = Post(title="Test title2", content="test", user_id=self.user_id)
            db.session.add_all([p1,p2])
            db.session.commit()

    
    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()

    def test_show_user_info(self):
        """Tests that the posts for the user is displayed"""
        with app.test_client() as client:
            response = client.get(f"/users/{self.user_id}")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Paul', html)
            self.assertIn('Test title1', html)
    
    def test_post_handler(self):
        """Tests that the post is added to the database"""
        with app.test_client() as client:
            data = {
                'title': 'test3',
                'content': 'some content',
                'user_id': self.user_id
            }
            response = client.post(f"/users/{self.user_id}/posts/new", data=data, follow_redirects=True)
            html = response.get_data(as_text=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn('test3', html)
    
    def test_show_post(self):
        """Tests to see if the new post is displayed"""
        with app.app_context():
            p3 = Post(title="Test title3", content="test", user_id=self.user_id)
            db.session.add(p3)
            db.session.commit()
            post=Post.query.all()
            with app.test_client() as client:
                response = client.get(f"posts/{post[2].id}")
                html = response.get_data(as_text=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn('Test title3', html)

    def test_delete_user(self):
        """Tests to see if the post was deleted from the database and is not showing on the page."""
        with app.test_client() as client:
            response = client.post(f"/posts/1/delete", follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            post = Post.query.filter_by(title="Test title1").first()
            self.assertIsNone(post)
            
