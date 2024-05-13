#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask_migrate import Migrate
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
from models import Venue, Artist, Shows, db
from sqlalchemy import func
from sqlalchemy.orm import joinedload


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)

with app.app_context():
    db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  city_states = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  for city_state in city_states:
    venue_dict = {}
    venue_dict['city'] = city_state.city
    venue_dict['state'] = city_state.state
    venue_dict['venues'] = []
    venues = Venue.query.filter_by(state=city_state.state).filter_by(city=city_state.city).all()
    for venue in venues:
      venue_dict['venues'].append({'id':venue.id,'name':venue.name})
    data.append(venue_dict)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response={}
  response['data'] = []
  today = datetime.now().date()

  for venue in venues:
    venue_upcoming_show = Shows.query.filter_by(venue_id=venue.id).filter(Shows.start_time > today)   
    venue_dict = {
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': venue_upcoming_show.count()

     }
    response['data'].append(venue_dict)
  
  response['count'] = len(response['data'])
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter_by(id=venue_id).first()

  data = {"id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address":venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.looking_for_Talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link}
  
  data['past_shows'] = []
  data['upcoming_shows'] = []

  today = datetime.now().date()

  incoming_show_result = db.session.query(Shows, Artist).join(Artist).filter(Shows.c.start_time>today).all()
  past_show_result = db.session.query(Shows, Artist).join(Artist).filter(Shows.c.start_time<today).all()


  for item in past_show_result:
    shows_artist_id = item[0]
    shows_venue_id = item[1]
    shows_start_time = item[2]
    artist = item[3]

    artist_show_detail_dict = {
      'artist_id': artist.id ,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(shows_start_time)
    }

    data['past_shows'].append(artist_show_detail_dict)


  for item in incoming_show_result:
    shows_artist_id = item[0]
    shows_venue_id = item[1]
    shows_start_time = item[2]
    artist = item[3]

    artist_show_detail_dict = {
      'artist_id': artist.id ,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(shows_start_time)
    }

    data['upcoming_shows'].append(artist_show_detail_dict)



  data['past_shows_count'] = len(data['past_shows'])

  # data['upcoming_shows_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf':False})

  if form.validate():
    try:
      looking_for_Talent_bool=True if request.form['seeking_talent'] == 'y' else False
    except:
      looking_for_Talent_bool = False
      
    try:
      new_venue = Venue(name=request.form['name'],
                        city=request.form['city'],
                        state=request.form['state'],
                        address=request.form['address'],
                        phone=request.form['phone'],
                        genres=request.form['genres'],
                        facebook_link=request.form['facebook_link'],
                        image_link=request.form['image_link'],
                        website_link=request.form['website_link'],
                        looking_for_Talent=looking_for_Talent_bool,
                        seeking_description=request.form['seeking_description'])
      db.session.add(new_venue)
      db.session.commit()
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f'{field}: {error}')
    
    flash('Please fix the following errors: '+', '.join(message))
    form = VenueForm()
    return render_template('pages/new_venue.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
     result = Venue.query.filter_by(id=venue_id).first()
     Venue.query.filter_by(id=venue_id).delete()
     db.session.commit()
     flash('Venue ' + result.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + result.name + ' could not be deleted.')
  finally:
     db.session.close()
     

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response={}
  response['data'] = []
  today = datetime.now().date()

  for artist in artists:
    artist_upcoming_show = Shows.query.filter_by(artist_id=artist.id).filter(Shows.start_time > today)   
    artist_dict = {
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': artist_upcoming_show.count()

     }
    response['data'].append(artist_dict)
  
  response['count'] = len(response['data'])

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  artist = Artist.query.filter_by(id=artist_id).first()

  data = {"id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_for_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link}
  
  data['past_shows'] = []
  data['upcoming_shows'] = []

  today = datetime.now().date()
  incoming_show_venue_result = db.session.query(Shows, Venue).join(Venue).filter(Shows.c.start_time>today).all()
  past_venue_result = db.session.query(Shows, Venue).join(Venue).filter(Shows.c.start_time<today).all()

  for item in past_venue_result:
    shows_venue_id= item[0]
    shows_artist_id = item[1]
    shows_start_time = item[2]
    venue = item[3]

    venue_show_detail_dict = {
      'venue_id': venue.id ,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': str(shows_start_time)
    }

    data['past_shows'].append(venue_show_detail_dict)

  for item in incoming_show_venue_result:
    shows_venue_id= item[0]
    shows_artist_id = item[1]
    shows_start_time = item[2]
    venue = item[3]

    venue_show_detail_dict = {
      'venue_id': venue.id ,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': str(shows_start_time)
    }
    data['upcoming_shows'].append(venue_show_detail_dict)

  
  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()

  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.looking_for_venues
    form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes

  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    old_name = artist.name
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    try:
      artist.looking_for_venues = True if request.form['seeking_venue'] == 'y' else False
    except:
      artist.looking_for_Talent = False
    artist.seeking_description = request.form['seeking_description']
    artist.genres = request.form['genres']
    db.session.commit()
    flash('Artist: ' + old_name + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist:' + old_name + ' is not updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()

  print(venue)

  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.looking_for_Talent
    form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    old_name = venue.name
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    try:
      venue.looking_for_Talent = True if request.form['seeking_talent'] == 'y' else False
    except:
      venue.looking_for_Talent = False
    venue.seeking_description = request.form['seeking_description']
    venue.genres = request.form['genres']
    db.session.commit()
    flash('Venue: ' + old_name + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue:' + old_name + ' is not updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form, meta={'csrf':False})
  
  if form.validate():
    try:
      looking_for_venue_bool = True if request.form['seeking_venue'] == 'y' else False
    except:
      looking_for_venue_bool = False

    try:
      new_artist = Artist(name=request.form['name'],
                        city=request.form['city'],
                        state=request.form['state'],
                        phone=request.form['phone'],
                        genres=request.form['genres'],
                        facebook_link=request.form['facebook_link'],
                        image_link=request.form['image_link'],
                        website_link=request.form['website_link'],
                        looking_for_venues=looking_for_venue_bool,
                        seeking_description=request.form['seeking_description'])
      db.session.add(new_artist)
      db.session.commit()
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f'{field}: {error}')
    
    flash('Please fix the following errors: '+', '.join(message))
    form = ArtistForm()
    return render_template('pages/new_artist.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Shows.query.all()

  data = []

  for show in shows:
    artist = Artist.query.filter_by(id=show.artist_id).first()
    data_dict = {
      'venue_id':show.venue_id,
      'venue_name': Venue.query.filter_by(id=show.venue_id).first().name,
      'artist_id': show.artist_id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(show.start_time)
    }
    data.append(data_dict)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm(request.form, meta={'csrf':False})

  if form.validate():
    try:
      new_Show = Shows(venue_id=request.form['venue_id'],
                          artist_id=request.form['artist_id'],
                          start_time=request.form['start_time'],
                          )
      db.session.add(new_Show)
      db.session.commit()
    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f'{field}: {error}')
    
    flash('Please fix the following errors: '+', '.join(message))
    form = ShowForm()
    return render_template('pages/new_show.html')



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

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
