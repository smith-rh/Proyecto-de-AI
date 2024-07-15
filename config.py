import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    QUERY_SAVE_PATH = os.path.join(os.getcwd(), 'app', 'queries')
