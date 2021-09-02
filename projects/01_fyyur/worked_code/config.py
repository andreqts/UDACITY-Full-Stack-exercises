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

# Workaround for Flask bug on CSRF (we need a hostname to remote access, otherwise Chrome will enforce https, and it does not 
#                                   accept local.dev too, but local.test is ok. In localhost this workaround is not neede,
#                                   you can use localhost or 127.0.0.1 in http and will not enforce https)
#see more info in: https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask#what-causes-bad-request-csrf-token-missing
#IMPORTANT: do not use local.dev, see: https://stackoverflow.com/questions/25277457/google-chrome-redirecting-localhost-to-https
#SERVER_NAME = 'local.test:5000'