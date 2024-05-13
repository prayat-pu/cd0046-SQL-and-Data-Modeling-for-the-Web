from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    genres = db.Column(db.ARRAY(db.String))


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    looking_for_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    

Shows = db.Table('Shows',
                db.Column('venue_id',db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
                db.Column('artist_id',db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
                db.Column('start_time',db.DateTime))