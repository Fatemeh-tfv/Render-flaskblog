from datetime import datetime, timedelta
from flaskblog.models import user, post
from flaskblog import db
from sqlalchemy import func

def get_engagement_summary():
    now = datetime.utcnow()

    # Inactive: last_login more than 7 days ago
    inactive_since = now - timedelta(days=7)
    inactive_users = user.query.filter(
        user.last_login != None,
        user.last_login < inactive_since
    ).all()

    # Top posters in last 7 days
    one_week_ago = now - timedelta(days=7)
    top_users = (
        db.session.query(user.UserName, func.count(post.id).label('post_count'))
        .join(post)
        .filter(post.date_posted >= one_week_ago)
        .group_by(user.id)
        .order_by(func.count(post.id).desc())
        .limit(3)
        .all()
    )

    # Badge assignment
    def assign_badges():
        # Precompute champion
        first_day_of_month = now.replace(day=1)
        champion = (
            db.session.query(user.id, func.count(post.id).label('c'))
            .join(post)
            .filter(post.date_posted >= first_day_of_month)
            .group_by(user.id)
            .order_by(func.count(post.id).desc())
            .first()
        )

        champ_id = champion[0] if champion else None

        badged_users = {}
        for u in user.query.all():
            user_badges = []

            # Newcomer
            if u.last_login and (now - u.last_login).days < 7:
                user_badges.append({"emoji": "🐣", "description": "Newcomer"})

            # Contributor
            if len(u.posts) >= 5:
                user_badges.append({"emoji": "✍️", "description": "Contributor"})

            # Streaker: 3 posts in last 3 days
            recent = [p for p in u.posts if (now - p.date_posted).days <= 3]
            if len(recent) >= 3:
                user_badges.append({"emoji": "🔥", "description": "Streaker"})

            # Champion
            if u.id == champ_id:
                user_badges.append({"emoji": "🏆", "description": "Champion"})

            badged_users[u.id] = user_badges
        return badged_users

    return {
        "inactive_users": inactive_users,
        "top_users":      top_users,
        "badged_users":   assign_badges()
    }
