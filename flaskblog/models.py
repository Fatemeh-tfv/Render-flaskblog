from datetime import datetime
from itsdangerous.url_safe import URLSafeSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))

class post(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.String(100), nullable= False)
    date_posted= db.Column(db.DateTime, nullable= False, default= datetime.utcnow)
    content= db.Column(db.Text, nullable= False)
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)

    def __repr__(self) -> str:
        return f"post('{self.title}','{self.date_posted}')"
    
class user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    UserName = db.Column(db.String(20), unique= True, nullable= False)
    Email = db.Column(db.String(120), unique= True, nullable= False)
    image_file = db.Column(db.String(20), nullable= False, default='default.jpg')
    Password = db.Column(db.String(60), nullable= False)
    posts = db.relationship('post', backref= 'author', lazy= True)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, expires_sec=1800)['user_id']
        except:
            return None
        
        return user.query.get(user_id)

    def __repr__(self) -> str:
        return f"user('{self.UserName}','{self.Email}','{self.image_file}')"