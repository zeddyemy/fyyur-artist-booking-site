# Imports
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120)) # < genres = db.Column(db.PickleType, nullable=True) > 
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean, nullable=True, default=False)
    description  = db.Column(db.String(200))
    shows = db.relationship("Show", backref="venues", lazy=True)

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, genres: {self.genres}, city: {self.city}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # DONE.

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120)) # < genres = db.Column(db.PickleType, nullable=True) > 
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    looking_for_venues = db.Column(db.Boolean, nullable=True, default=False)
    description  = db.Column(db.String(200))
    shows = db.relationship("Show", backref="artists", lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}, show: {self.show}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # DONE.

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
	__tablename__ = "Show"
	id = db.Column(db.Integer, primary_key=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), nullable=False,)
	venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'), nullable=False,)
	start_time = db.Column(db.DateTime, nullable=False)

	artist = db.relationship('Artist')
	venue = db.relationship('Venue')

	def __repr__(self):
		return f'<Show id: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id}'