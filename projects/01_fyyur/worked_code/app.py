#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, make_response
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

from models import csrf

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

def flash_errors(form):
  """Flashes form errors"""
  for field, errors in form.errors.items():
      for error in errors:
          flash(u"Error in the %s field - %s" % (
              getattr(form, field).label.text,
              error
          ), category='error')


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

  form = VenueForm(request.form)
  if not form.validate():
    print('New venue form validation failed!')
    flash_errors(form)
    return render_template('forms/new_venue.html', form=form)

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
    flash('Sorry, Venue ' + request.form['name'] + ' could not be listed, please contact the support!', category='error')
    session.rollback()
    no_error_occurred = False
  finally:
    session.close()

  if (no_error_occurred):
    flash('Venue ' + createdvenue.name + ' successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
 
  try:
    venue_to_delete = Venue.query.get(venue_id)
  except:
    print(f'Error retrieving venue {venue_id}: {sys.exc_info()}')
    msgerror = 'Sorry, Venue ' + venue_id + ' could not be accessed, please contact the support!'
    flash(msgerror)
    no_errors = False
    return make_response(jsonify(message=msgerror), 500)

  venue_name = venue_to_delete.name
  try:
    db.session.delete(venue_to_delete)
    db.session.commit()
  except:
    db.session.rollback()
    print(f'Error deleting venue {venue_id}: {sys.exc_info()}')
    msgerror = 'Sorry, Venue ' + venue_id + ' could not be deleted, please check if there are pending shows, or contact the support!'
    flash(msgerror)
    no_errors = False
    return make_response(jsonify(message=msgerror), 500)
  finally:
    db.session.close()

  flash(f'Venue {venue_name}, id={venue_id} successfully deleted!')

  return make_response(jsonify(message='ok'), 200)

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

  try:
    artist = Artist.query.get(artist_id)
  except:
    print(f'Error retrieving artist {artist_id} data: {sys.exc_info()}')
    flash(f'Sorry, could not retrieve data on artist {artist_id}, please contact the support!')
    return redirect(url_for('show_artist', artist_id=artist_id))

  form = ArtistForm(
    name = artist.name,
    genres = artist.genres.split(','),
    city = artist.city,
    state = artist.state,
    phone = artist.phone,
    website_link = artist.website_link,
    facebook_link = artist.facebook_link,
    seeking_venue = artist.seeking_venue,
    seeking_description = artist.seeking_description,
    image_link = artist.image_link,
  )

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  edited_data_lists = dict(request.form.lists())

  try:
    artist = Artist.query.get(artist_id)
  except:
    print(f'Error retrieving artist {artist_id} data: {sys.exc_info()}')
    flash(f'Sorry, could not retrieve data on artist {artist_id}, please contact the support!')
    return redirect(url_for('show_artist', artist_id=artist_id))

  form = ArtistForm(request.form)
  if not form.validate():
    print('Form Validation failed!')
    flash_errors(form)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


  b_seeking = ('seeking_venue' in edited_data_lists.keys()) and (request.form['seeking_venue'].lower() == 'y')
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.seeking_venue = b_seeking
    artist.seeking_description = request.form['seeking_description']
    artist.genres = ','.join(edited_data_lists['genres'])
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    print(f'Error editing artist {artist_id} data: {sys.exc_info()}')
    flash(f'Sorry, could not edit data on artist {artist_id}, please contact the support!')
    db.session.rollback()
    return redirect(url_for('show_artist', artist_id=artist_id))
  finally:
    db.session.close()

  flash(f'Artist {request.form["name"]} with id={artist_id} successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  try:
    venue = Venue.query.get(venue_id)
  except:
    print(f'Error retrieving venue {venue_id} data: {sys.exc_info()}')
    flash(f'Sorry, could not retrieve data on venue {venue_id}, please contact the support!')
    return redirect(url_for('show_venue', pvenue_id=venue_id))

  print('=> genres = {}'.format(venue.genres.split(',')))

  form = VenueForm(
    id = venue.id,
    name = venue.name,
    genres = venue.genres.split(','),
    city = venue.city,
    state = venue.state,
    address = venue.address,
    phone = venue.phone,
    seeking_talent = venue.seeking_talent,
    seeking_description = venue.seeking_description,
    website_link = venue.website_link,
    image_link = venue.image_link,
    facebook_link = venue.facebook_link,
  )

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  edited_data_lists = dict(request.form.lists())

  b_seeking = ('seeking_talent' in edited_data_lists.keys()) and (request.form['seeking_talent'].lower() == 'y')

  try:
    venue = Venue.query.get(venue_id)
  except:
    print(f'Error retrieving venue {venue_id} data: {sys.exc_info()}')
    flash(f'Sorry, could not retrieve data on venue {venue_id}, please contact the support!')
    return redirect(url_for('show_venue', pvenue_id=venue_id))

  form = VenueForm(request.form)
  if not form.validate():
    print('Edit venue form validation failed!')
    flash_errors(form)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  try:
    venue.name = request.form['name']
    venue.genres = ','.join(edited_data_lists['genres'])
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.seeking_talent = b_seeking
    venue.seeking_description = request.form['seeking_description']
    venue.website_link = request.form['website_link']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    print(f'Error editing venue {venue_id} data: {sys.exc_info()}')
    flash(f'Sorry, could not edit data on venue {venue_id}, please contact the support!')
    db.session.rollback()
    return redirect(url_for('show_venue', pvenue_id=venue_id))
  finally:
    db.session.close()

  flash(f'Venue {request.form["name"]} with id={venue_id} successfully edited!')

  return redirect(url_for('show_venue', pvenue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  
  values_lst = dict(request.form.lists())

  form = ArtistForm(request.form)
  if not form.validate():
    print('New artist form validation failed!')
    flash_errors(form)
    return render_template('forms/new_artist.html', form=form)

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
    flash('Sorry, artist ' + request.form['name'] + ' could not be listed, please contact the support!', category='error')
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

  form = ShowForm(request.form)
  if not form.validate():
    print('New show form validation failed!')
    flash_errors(form)
    return render_template('forms/new_show.html', form=form)

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
    flash('Sorry, new show at venue id ' + request.form['venue_id'] + ' could not be listed, please contact the support!', category='error')
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

