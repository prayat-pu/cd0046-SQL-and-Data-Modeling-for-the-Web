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
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


db = SQLAlchemy(app)
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    looking_for_Talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.String(120))

    Shows = db.relationship('Shows', backref='venue')


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    looking_for_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    Shows = db.relationship('Shows', backref='artist')

class Shows(db.Model):
   __tablename__ = "Shows"

   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
   start_time = db.Column(db.DateTime)




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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = Venue.query.all()
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
    "genres": venue.genres.lstrip('{').rstrip('}').split(','),
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
  venue_past_shows = Shows.query.filter_by(venue_id=venue_id).filter(Shows.start_time < today).all()

  for show in venue_past_shows:
    print(f'shows: {show.id}, venue_id: {show.venue_id}, artist_id: {show.artist_id}, starttime: {show.start_time}')
    artist_show = Artist.query.filter_by(id=show.artist_id).first()
    artist_show_detail_dict = {
      'artist_id': show.artist_id ,
      'artist_name': artist_show.name,
      'artist_image_link': artist_show.image_link,
      'start_time': str(show.start_time)
    }

    data['past_shows'].append(artist_show_detail_dict)

  venue_upcoming_shows = Shows.query.filter_by(venue_id=venue_id).filter(Shows.start_time > today).all()

  for show in venue_upcoming_shows:
    print(f'shows: {show.id}, venue_id: {show.venue_id}, artist_id: {show.artist_id}, starttime: {show.start_time}')
    artist_show = Artist.query.filter_by(id=show.artist_id).first()
    artist_show_detail_dict = {
      'artist_id': show.artist_id ,
      'artist_name': artist_show.name,
      'artist_image_link': artist_show.image_link,
      'start_time': str(show.start_time),
    }
    data['upcoming_shows'].append(artist_show_detail_dict)

  data['past_shows_count'] = len(data['past_shows'])

  data['upcoming_shows_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
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
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

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
    "genres": artist.genres.lstrip('{').rstrip('}').strip('"').split(','),
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
  venue_past_shows = Shows.query.filter_by(artist_id=artist_id).filter(Shows.start_time < today).all()

  for show in venue_past_shows:
    venue_show = Venue.query.filter_by(id=show.venue_id).first()
    venue_show_detail_dict = {
      'venue_id': show.artist_id ,
      'venue_name': venue_show.name,
      'venue_image_link': venue_show.image_link,
      'start_time': str(show.start_time)
    }

    data['past_shows'].append(venue_show_detail_dict)

  venue_upcoming_shows = Shows.query.filter_by(artist_id=artist_id).filter(Shows.start_time > today).all()

  for show in venue_upcoming_shows:
    venue_show = Artist.query.filter_by(id=show.venue_id).first()
    venue_show_detail_dict = {
      'venue_id': show.artist_id ,
      'venue_name': venue_show.name,
      'venue_image_link': venue_show.image_link,
      'start_time': str(show.start_time),
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
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


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

  new_Show = Shows(venue_id=request.form['venue_id'],
                      artist_id=request.form['artist_id'],
                      start_time=request.form['start_time'],
                      )
  db.session.add(new_Show)
  db.session.commit()
  flash('Show was successfully listed!')

  # try:
  #   new_Show = Shows(venue_id=request.form['venue_id'],
  #                     artist_id=request.form['artist_id'],
  #                     start_time=request.form['start_time'],
  #                     )
  #   db.session.add(new_Show)
  #   db.session.commit()
  #   flash('Show was successfully listed!')
  # except:
  #   db.session.rollback()
  #   flash('An error occurred. Show could not be listed.')
  # finally:
  #   db.session.close()

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

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
