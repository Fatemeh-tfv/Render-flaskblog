from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    Title = StringField('Title', validators=[DataRequired()])
    Content = TextAreaField('Content', validators=[DataRequired()])
    Submit = SubmitField('Post')