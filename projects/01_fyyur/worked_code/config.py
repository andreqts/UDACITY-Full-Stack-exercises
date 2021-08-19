import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
dbuser = 'andrequites'
dbpassword = '*#N-w3is7u&%'
dbhost = 'localhost' 
dbname = 'fyyurdb'

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(dbuser, dbpassword, dbhost, dbname)
SQLALCHEMY_TRACK_MODIFICATIONS = True  #explicit is better than implicit...