from flask_sqlalchemy import SQLAlchemy 
db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String())
    seeking_description = db.Column(db.Text)
    upcoming_shows_count = db.Column(db.Integer, default=2)
    past_shows_count = db.Column(db.Integer, default=4)
    shows = db.relationship('Show',backref='venue',lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.Text)
    upcoming_shows_count = db.Column(db.Integer, default=1)
    past_shows_count = db.Column(db.Integer, default=3)
    shows = db.relationship('Show',backref='artist',lazy=True)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'shows'
  
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
  start_time = db.Column(db.DateTime, nullable=False) 