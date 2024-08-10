import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail
from flask_login import current_user

def Save_picture(form_Picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_Picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/P_pics', picture_fn)

    output_size = (125, 125)
    img = Image.open(form_Picture)
    img.thumbnail(output_size)
    pre_picture = os.path.join(current_app.root_path, 'static/P_pics', current_user.image_file) 
    if os.path.exists(pre_picture):
        os.remove(pre_picture)

    img.save(picture_path)

    return picture_fn

def send_reset_email(User):
    token = User.get_reset_token()
    msg = Message('Password Reset Request', sender='taraaaaaa772@gmail.com', recipients=[User.Email])
    msg.body= f'''To reset your password, visit the fallowing link: {url_for('users.reset_token', token= token, _external= True)}
if you did not make thid request then simply ignore this email and no changes will be made
'''
    try:
        mail.send(msg)
    except:
        print(msg)