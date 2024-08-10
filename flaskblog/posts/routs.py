from flask import Blueprint, url_for, flash, redirect, request, abort, render_template
from flask_login import current_user, login_required
from flaskblog.models import post
from flaskblog.posts.forms import PostForm
from flaskblog import db
posts = Blueprint('posts', __name__)

@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        Post = post(title= form.Title.data, content= form.Content.data, author= current_user)
        db.session.add(Post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title= 'New Post', form= form, legend= 'New Post')

@posts.route('/post/<int:post_id>')
def Post(post_id):
    Post = post.query.get_or_404(post_id)
    return render_template('Post.html', title=Post.title, Post= Post)

@posts.route('/post/<int:post_id>/update', methods= ['GET', 'POST'])
@login_required
def update_post(post_id):
    Post = post.query.get_or_404(post_id)
    if Post.author != current_user:
        abort(403)
    form= PostForm()
    if form.validate_on_submit():
        Post.title = form.Title.data
        Post.content = form.Content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.Post', post_id = post_id))
    elif request.method == 'GET':
        form.Title.data = Post.title
        form.Content.data = Post.content
    return render_template('create_post.html', title= 'Update Post', form= form, legend= 'Update Post')

@posts.route('/post/<int:post_id>/delete', methods= ['POST'])
@login_required
def delete_post(post_id):
    Post = post.query.get_or_404(post_id)
    if Post.author != current_user:
        abort(403)
    db.session.delete(Post)
    db.session.commit()
    flash('Your post has been deleted!', 'info')
    return redirect(url_for('main.home'))