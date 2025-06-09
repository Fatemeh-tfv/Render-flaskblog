from flask import Blueprint, render_template, request
from flaskblog.models import post, TeamMember, user
from flaskblog.bot.engagement_bot import get_engagement_summary
from sqlalchemy import func, or_

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    summary = get_engagement_summary()
    badged_users = summary.get("badged_users", {})
    inactive_users = summary.get("inactive_users", [])
    page = request.args.get('page', 1, type=int)
    posts = post.query.order_by(post.date_posted.desc()).paginate(page=page, per_page=4)
    user_badges = {}

    for p in posts:
        uid = p.user_id
        user_badges[uid] = badged_users.get(uid, [])

    return render_template('home.html', posts= posts, user_badges=user_badges, inactive_users=inactive_users)

@main.route('/about')
def about():
    team = TeamMember.query.all()
    return render_template('about.html', title='About Us', team=team)

@main.route('/search')
def search():
    query = request.args.get('query', '').strip()

    if not query:
        return render_template('search_results.html', users=[], posts=[], query=query)

    # Search Users by username (case-insensitive)
    users = user.query.filter(func.lower(user.UserName).like(f'%{query.lower()}%')).all()

    # Search Posts by title or content (case-insensitive)
    posts = post.query.filter(
        or_(
            func.lower(post.title).like(f'%{query.lower()}%'),
            func.lower(post.content).like(f'%{query.lower()}%')
        )
    ).all()

    return render_template('search_results.html', users=users, posts=posts, query=query)