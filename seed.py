"""Seed file to make sample data for db."""

from app import app
from models import User, Post, db, Tag, PostTag

# Create all tables
with app.app_context():
    db.drop_all()
    db.create_all()

    User.query.delete()
    Post.query.delete()


    # Add sample employees and departments
    tom = User(first_name='Tom',last_name='Doe')
    bob = User(first_name='Bob',last_name='Chin')

    db.session.add_all([tom, bob])
    db.session.commit()

    p1 = Post(title='First Post!', content='I have no idea what to say.', user_id='1')
    p2 = Post(title='Second Post!', content='I still have no idea what to say.', user_id='2')

    db.session.add_all([p1,p2])
    db.session.commit()
    
    # add sample tags and posts-tags
    t1 = Tag(name='cool')
    t2 = Tag(name='funny')
    
    db.session.add_all([t1,t2])
    db.session.commit()
    
    pt1 = PostTag(post_id=1,tag_id=1)
    pt2 = PostTag(post_id=1,tag_id=2)
    pt3 = PostTag(post_id=2,tag_id=2)
    
    db.session.add_all([pt1, pt2, pt3])
    db.session.commit()
    

