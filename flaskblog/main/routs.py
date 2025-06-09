from flask import Blueprint, render_template, request
from flaskblog.models import post, TeamMember
from flaskblog.bot.engagement_bot import get_engagement_summary

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    summary = get_engagement_summary()
    badged_users = summary.get("badged_users", {})
    page = request.args.get('page', 1, type=int)
    posts = post.query.order_by(post.date_posted.desc()).paginate(page=page, per_page=4)
    user_badges = {}

    for p in posts:
        uid = p.user_id
        user_badges[uid] = badged_users.get(uid, [])

    return render_template('home.html', posts= posts, user_badges=user_badges)

@main.route('/about')
def about():
    team = TeamMember.query.all()
    return render_template('about.html', title='About Us', team=team)