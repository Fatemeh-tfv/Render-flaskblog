from flask import Blueprint, url_for, flash, redirect, request, abort, render_template, session
from flask_login import current_user, login_required
from flaskblog.models import post, Like, Comment, Dislike
from flaskblog.posts.forms import PostForm
from flaskblog import db
from markupsafe import Markup
from flaskblog.users.utils import active_required

posts = Blueprint('posts', __name__)

@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
@active_required
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
@active_required
def update_post(post_id):
    Post = post.query.get_or_404(post_id)
    if Post.author != current_user and not current_user.is_admin:
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
@active_required
def delete_post(post_id):
    Post = post.query.get_or_404(post_id)
    if Post.author != current_user and not current_user.is_admin:
        abort(403)

    session['last_deleted_post']={
        'id': Post.id,
        'title': Post.title,
        'content': Post.content,
        'user_id': Post.user_id
    }
    db.session.delete(Post)
    db.session.commit()
    flash(Markup(f'The post has been deleted! <a href="{url_for("posts.undo_delete")}" class="text-light text-decoration-underline">Undo</a>'), 'info')
    return redirect(request.referrer or url_for('main.home'))

@posts.route('/undo_delete')
@login_required
@active_required
def undo_delete():
    post_data=session.pop('last_deleted_post', None)

    if  not post_data:
        flash('Nothing to undo', 'warning')
        return redirect(url_for('main.home'))
    
    restored_post= post(
        id= post_data['id'],
        title = post_data['title'],
        content= post_data['content'],
        user_id= post_data['user_id']
        )
    
    db.session.add(restored_post)
    db.session.commit()

    flash('The post has restored successfully|', 'success')
    return redirect(url_for('users.user_posts', UserName=restored_post.author.UserName))

@posts.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    Post_content= post.query.get_or_404(post_id)
    existing = Like.query.filter_by(user_id= current_user.id, post_id=Post_content.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Like(user_id= current_user.id, post_id= Post_content.id, is_like=True))
    
    db.session.commit()
    return redirect(request.referrer)

@posts.route('/post/<int:post_id>/dislike', methods=['POST'])
@login_required
def dislike_post(post_id):
    Post_content= post.query.get_or_404(post_id)
    existing = Dislike.query.filter_by(user_id= current_user.id, post_id=Post_content.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Dislike(user_id= current_user.id, post_id= Post_content.id, is_Dislike=True))
    
    db.session.commit()
    return redirect(request.referrer)

@posts.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    content = request.form['content']
    db.session.add(Comment(content=content, user_id= current_user.id, post_id=post_id))
    db.session.commit()
    return redirect(request.referrer)

@posts.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(comment)
    db.session.commit()
    flash("Your comment has been deleted.", "success")
    return redirect(request.referrer or url_for('main.home'))