import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# in my terminal on windows operating system i ran the following command to create a database called fyyur
'''
create database fyyur;
'''

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:zeddy.emy@localhost:5432/fyyur'
