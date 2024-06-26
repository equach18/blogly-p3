from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secret'

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

with app.app_context():
    db.create_all()

@app.route('/')
def homepage():
    """Redirects to list of users."""

    return redirect("/users")

@app.route('/users')
def list_users():
    """Show all users with links for more details. Contains link to add a user"""
    users = User.query.all()
    return render_template("index.html", users=users)

@app.route('/users/new')
def show_user_form():
    """Shows an add form for users"""
    return render_template("new-user.html")

@app.route('/users/new', methods=['POST'])
def add_user():
    """Processes the add form, adding a new user and goes back to /users"""

    first_name = request.form['first-name']
    last_name = request.form['last-name']
    img_url = request.form['img-url'] or None

    user = User(first_name=first_name, last_name=last_name, image_url=img_url)
    db.session.add(user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>')
def show_user_info(user_id):
    """Shows information about the given user."""
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)


@app.route('/users/<int:user_id>/edit')
def show_edit_user(user_id):
    """Shows the edit page for the user. """
    user = User.query.get_or_404(user_id)
    return render_template('edit-user.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def edit_user(user_id):
    """Finalize the edits of a user"""
    user = User.query.get_or_404(user_id)

    user.first_name = request.form['first-name'] or user.first_name
    user.last_name = request.form['last-name'] or user.last_name
    user.img_url = request.form['img-url'] or None

    db.session.add(user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Finalize the edits of a user"""
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>/posts/new')
def show_post_form(user_id):
    """Shows form to add a post for that user"""
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('post-form.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def handle_post_form(user_id):
    """Handles post add and redirects to the user detail page."""
    
    title = request.form['title']
    content = request.form['content']
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    
    post = Post(title=title, content=content,user_id=user_id)
    for tag in tags:
        post.tags.append(tag)
        
    db.session.add(post)
    db.session.commit()
    return redirect(f"/users/{user_id}")

@app.route('/posts/<post_id>')
def show_post(post_id):
    """shows the post and buttons to cancel, edit, and delete"""
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',post=post)

@app.route('/posts/<post_id>/edit')
def show_edit_post(post_id):
    """Shows form to edit a post and to cancel"""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('edit-post.html', post=post, tags=tags)
    
@app.route('/posts/<post_id>/edit', methods=['POST'])
def handle_post_edit(post_id):
    """Handles the editing of a post. Redirects back to the post view"""
    post = Post.query.get_or_404(post_id)
    
    post.title = request.form['title'] or post.title
    post.content = request.form['content'] or post.content
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    

    db.session.add(post)
    db.session.commit()

    return redirect(f"/posts/{post.id}")

@app.route('/posts/<post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Deletes the post."""
    post = Post.query.get_or_404(post_id)
    
    db.session.delete(post)
    db.session.commit()
    
    return redirect(f"/")

@app.route('/tags')
def list_tags():
    """Lists all tags with links to the tag detail page"""
    tags = Tag.query.all()
    return render_template('tag-list.html', tags=tags)

@app.route('/tags/<int:tag_id>')
def show_tag_details(tag_id):
    """Shows details about a tag."""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag-details.html', tag=tag)

@app.route('/tags/new')
def show_new_tag():
    """Shows a form to add a new tag"""
    tags = Tag.query.all()
    return render_template('new-tag.html', tags=tags)

@app.route('/tags/new', methods=['POST'])
def handle_new_tag():
    """Processes the add form, adds tag, and redirects to tags list"""
    name = request.form['name']
    
    db.session.add(Tag(name=name))
    db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:tag_id>/edit')
def show_edit_tag(tag_id):
    """Shows edit form for a tag."""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('edit-tag.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def handle_edit_tag(tag_id):
    """Processes the edit form, edit tag, and redirects to the tags list."""
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    
    db.session.add(tag)
    db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect('/tags')