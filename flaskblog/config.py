from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

class config:
    SECRET_KEY =os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI =os.getenv('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = '465'
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')