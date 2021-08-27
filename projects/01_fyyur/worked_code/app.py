#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_, and_
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import os
from models import *
import sys


moment = Moment(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime
 
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  locales = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state)
  for city, state in locales:
    city_venues = Venue.query.filter(and_(Venue.city==city, Venue.state==state)).all()
    venues_list = []
    for v in city_venues:
      upcomming_shows_cnt = v.get_upcoming_shows_count()
      name_value = v.name
      if app.debug: #show upcoming count in debug, since it is not shown to the user
        name_value += f" [{upcomming_shows_cnt} upcoming shows]"
      venues_list.append({
        "id": v.id,
        "name": name_value,
        "num_upcoming_shows": upcomming_shows_cnt,
      })

      #show Venues with more upcoming shows first, highlithing them (relevance)
      venues_list.sort(reverse=True, key=(lambda d : d["num_upcoming_shows"]))

    data.append ({
    "city": city,
    "state": state,
    "venues": venues_list
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  str_to_search = request.form.get('search_term', '')

  venues_found = Venue.query.filter(Venue.name.ilike(f'%{str_to_search}%')).all()
  found_data = []
  for venue in venues_found:
    found_data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": venue.get_upcoming_shows_count(),
    })

  response={
    "count": len(venues_found),
    "data": found_data,
  }

  return render_template('pages/search_venues.html', results=response, search_term=str_to_search)

@app.route('/venues/<int:pvenue_id>')
def show_venue(pvenue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venueobj = Venue.query.filter_by(id=pvenue_id).one()
  
  venueobj.genres = venueobj.genres.split(',')
  venueobj.past_shows = venueobj.get_past_shows()
  venueobj.past_shows_count = len(venueobj.past_shows)
  venueobj.upcoming_shows = venueobj.get_upcoming_shows()
  venueobj.upcoming_shows_count = len(venueobj.upcoming_shows)

  return render_template('pages/show_venue.html', venue=venueobj)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  newvalueslist = dict(request.form.lists())
  no_error_occurred = True

  # special treatment, since it is not sent if unchecked
  seeking = ('seeking_talent' in newvalueslist.keys()) and (request.form['seeking_talent'] == 'y')

  newvenue = Venue(
    name = request.form['name'],
    genres = ','.join(newvalueslist['genres']),
    city = request.form['city'],
    state = request.form['state'],
    address = request.form['address'],
    phone = request.form['phone'],
    seeking_talent = seeking,
    seeking_description = request.form['seeking_description'],
    website_link = request.form['website_link'],
    image_link = request.form['image_link'],
    facebook_link = request.form['facebook_link'],
  )
  session = db.session()
  try:
    session.add(newvenue)
    session.commit()
    createdvenue = Venue.query.get(newvenue.id)
  except:
    print(f'Error creating venue {request.form["name"]}: {sys.exc_info()}')
    flash('Sorry, Venue ' + request.form['name'] + ' could not be listed, please contact the support!')
    session.rollback()
    no_error_occurred = False
  finally:
    session.close()

  if (no_error_occurred):
    flash('Venue ' + createdvenue.name + ' successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists_data = Artist.query.with_entities(Artist.id, Artist.name).all()

  data=[]
  for art_id, art_name in artists_data:
    data.append({ "id": art_id, "name": art_name })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  term_to_search = request.form.get('search_term', '')
  artists_found = Artist.query.filter(Artist.name.ilike(f'%{term_to_search}%')).all()

  artists_data = []
  for artist in artists_found:
    artists_data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": artist.get_upcoming_shows_count(),
    })

  response={
    "count": len(artists_found),
    "data": artists_data
  }
  return render_template('pages/search_artists.html', results=response, search_term=term_to_search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist_data = Artist.query.get(artist_id)
  artist_data.upcoming_shows = artist_data.get_upcoming_shows()
  artist_data.past_shows = artist_data.get_past_shows()
  artist_data.past_shows_count = len(artist_data.past_shows)
  artist_data.upcoming_shows_count = len(artist_data.upcoming_shows)
  artist_data.genres = artist_data.genres.split(',')

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  
  values_lst = dict(request.form.lists())

  b_seeking = ('seeking_venue' in values_lst.keys()) and (request.form['seeking_venue'].lower() == 'y')

  no_error_occurred = True
  new_artist = Artist(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    seeking_venue = b_seeking,
    seeking_description = request.form['seeking_description'],
    genres = ','.join(values_lst['genres']),
    image_link = request.form['image_link'],
    website_link = request.form['website_link'],
    facebook_link = request.form['facebook_link'],    
  )

  session = db.session()
  try:
    session.add(new_artist)
    session.commit()
    createdartist = Artist.query.get(new_artist.id)
  except:
    print(f'Error creating artist {request.form["name"]}: {sys.exc_info()}')
    flash('Sorry, artist ' + request.form['name'] + ' could not be listed, please contact the support!')
    session.rollback()
    no_error_occurred = False
  finally:
    session.close()

  if (no_error_occurred):
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.join(Artist).join(Venue).with_entities(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time).all()

  shows_data = []
  for venue_id, venue_name, artist_id, artist_name, artist_link, show_time in shows:
    shows_data.append({
    "venue_id": venue_id,
    "venue_name": venue_name,
    "artist_id": artist_id,
    "artist_name": artist_name,
    "artist_image_link": artist_link,
    "start_time": show_time
    })

  return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  no_error_occurred = True
  new_show = Show(
    artist_id = request.form['artist_id'],
    venue_id = request.form['venue_id'],
    start_time = request.form['start_time'], 
  )

  session = db.session()
  try:
    session.add(new_show)
    session.commit()
  except:
    print(f'Error creating show "{request.form}": {sys.exc_info()}')
    flash('Sorry, new show at venue id ' + request.form['venue_id'] + ' could not be listed, please contact the support!')
    session.rollback()
    no_error_occurred = False
  finally:
    if no_error_occurred:
      new_show = session.query(Show).filter_by(artist_id=new_show.artist_id,venue_id=new_show.venue_id,start_time=new_show.start_time).one()
    session.close()

  if (no_error_occurred):
    flash(f'Show by artist {new_show.artist_id} at venue id {new_show.venue_id} successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

'''
# Default port:
if __name__ == '__main__':
    app.run()
'''

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

