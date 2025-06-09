from flask import Blueprint, render_template, request, abort, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from flaskblog.models import user, post
from flaskblog import db
from sqlalchemy import func
from flaskblog.bot.engagement_bot import get_engagement_summary

admin = Blueprint('admin', __name__)

@admin.route("/admin/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'username')

    # Subquery to count posts per user
    post_counts = db.session.query(
        post.user_id,
        func.count(post.id).label('post_count')
    ).group_by(post.user_id).subquery()

    # Main query (excluding admin accounts)
    query = db.session.query(
        user,
        func.coalesce(post_counts.c.post_count, 0).label('post_count')
    ).outerjoin(
        post_counts, user.id == post_counts.c.user_id
    ).filter(user.is_admin == False)

    # Sorting
    if sort_by == 'post_count':
        query = query.order_by(
            post_counts.c.post_count.desc().nullslast(),
            user.UserName.asc()
        )
    else:
        query = query.order_by(user.UserName.asc())

    pagination = query.paginate(page=page, per_page=5, error_out=False)

    # Get engagement summary and badges
    summary = get_engagement_summary()
    badged_users = summary.get("badged_users", {})

    # Build users with badge info
    users_with_posts = []
    for user_obj, post_count in pagination.items:
        posts = post.query.filter_by(user_id=user_obj.id).all()
        badges = badged_users.get(user_obj.id, [])
        users_with_posts.append({
            'user': user_obj,
            'post_count': post_count,
            'posts': posts,
            'badges': badges
        })

    current_app.jinja_env.cache.clear()

    return render_template(
        'admin-dashboard.html',
        users=users_with_posts,
        pagination=pagination,
        sort_by=sort_by,
        summary=summary
    )


@admin.route("/admin/user/<int:user_id>/toggle", methods=["POST"])
@login_required
def toggle_user_status(user_id):
    if not current_user.is_admin:
        abort(403)
    
    target_user = user.query.get_or_404(user_id)
    if target_user.is_admin:
        flash("You cannot change the status of an admin.", "warning")
        return redirect(url_for("admin.dashboard"))
    
    target_user.is_active= not target_user.is_active
    db.session.commit()
    status="enabled" if target_user.is_active else "disabled"
    flash(f"user {target_user.UserName}'s account has been {status}.", "success")
    return redirect(url_for("admin.dashboard"))