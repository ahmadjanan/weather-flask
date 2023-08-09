from dotenv import load_dotenv, find_dotenv

from config.env_vars import required_env_var

load_dotenv(find_dotenv())


class Config:
    SECRET_KEY = required_env_var('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = required_env_var('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
