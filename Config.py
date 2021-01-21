import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Schatz237994@MO@localhost:5432/postgres'

# remove console warning
#SQLALCHEMY_TRACK_MODIFICATIONS = False