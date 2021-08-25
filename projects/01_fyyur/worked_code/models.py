#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_, and_
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    genres = db.Column(db.String(120), nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable = False)
    facebook_link = db.Column(db.String(120))
    venue_shows = db.relationship('Show', backref='venue', lazy=True)

    # helper methods (guided by the famous "DRY" principle)
    def get_upcoming_shows(self):
        return Show.query.filter_by(venue_id=self.id).join(Artist, Show.artist_id==Artist.id).filter(Show.start_time > func.now()).all()

    def get_upcoming_shows_count(self):
        return Show.query.filter_by(venue_id=self.id).join(Artist, Show.artist_id==Artist.id).filter(Show.start_time > func.now()).count()

    def get_past_shows(self):
        return Show.query.filter_by(venue_id=self.id).join(Artist, Show.artist_id==Artist.id).filter(Show.start_time <= func.now()).all()

    def get_past_shows_count(self):
        return Show.query.filter_by(venue_id=self.id).join(Artist, Show.artist_id==Artist.id).filter(Show.start_time <= func.now()).count()


    def __repr__(self):
        return f'<Venue {self.id}: {self.name} phone: {self.phone}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500), nullable = False)
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    artist_shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id}: {self.name} phone: {self.phone}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False, primary_key=True)
    start_time = db.Column(db.DateTime, nullable = False, primary_key=True)

    def __repr__(self):
        return f'<Show from {self.artist_id} in {self.venue_id} at {self.start_time}>'
