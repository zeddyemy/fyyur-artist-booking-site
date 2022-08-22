#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import babel
import logging
import dateutil.parser
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_migrate import Migrate # Imported Migrate from flask_migrate.
import sys
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show
import config
import collections
collections.Callable = collections.abc.Callable

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app) # changed from db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
# DONE: I connected to local postgres db in config.py



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


#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
	# TODO: replace with real venues data.
	#       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

	# Query venues from db
	queriedVenues = Venue.query.order_by(Venue.state, Venue.city).all()
	data = []
	
	# for each venue in the queried venues
	for eachVenue in queriedVenues:
		venues = Venue.query.filter_by(city=eachVenue.city, state=eachVenue.state).all()
		formatted_venues = []
		for venue in venues:
			show_count = Show.query.join(Venue).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).count()
			formatted_venues.append({
				"id": venue.id,
				"name": venue.name,
				"num_upcoming_shows": show_count
			})
			
		
		getCityState = {
			"city": eachVenue.city,
			"state": eachVenue.state,
			"venues": formatted_venues
		}
		data.append(getCityState)
		
	return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
	# TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
	# search for Hop should return "The Musical Hop".
	# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

	# get search keyword from the form
	search_term = request.form.get('search_term', '')
	
	# using 'ilike' in sqlalchemy.
	# Reference link below: 
	# http://docs.sqlalchemy.org/en/latest/orm/internals.html?highlight=ilike#sqlalchemy.orm.attributes.QueryableAttribute.ilike

	# Query All venues That Have The Search Keyword In Their Name
	found_venues = Venue.query.filter(
		Venue.name.ilike('%{}%'.format(search_term))
	).all()
	
	data = []
	# for each venue in the queried venues, get the id, name, and number of shows
	for eachVenue in found_venues:
		venue = {
			'id': eachVenue.id,
			'name': eachVenue.name
		}
		data.append(venue)
	
	response = {
		'count': len(data),
		'data': data
	}
		
	return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id

	# query venue by venue_id
	venue = Venue.query.get(venue_id)
	
	# if the queried result is empty render a 404 page
	if not venue:
		return render_template('errors/404.html')
	
	shows = venue.shows # shows associated with the queried venue
	upcoming_shows = []
	past_shows = []
	
	# for each of the show in shows, get the artist name, image link and start time
	for show in shows:
		getArtistInfo = Show.query.join(Artist).with_entities(
			Show.artist_id,
			Artist.name,
			Artist.image_link,
			Show.start_time
		).filter(Show.venue_id==venue_id).first()
		
		artistInfo ={
            "artist_id": getArtistInfo[0],
            "artist_name": getArtistInfo[1],
            "artist_image_link": getArtistInfo[2],
            "start_time": getArtistInfo[3]
        }
		
		if show.start_time >= datetime.now():
			upcoming_shows.append(artistInfo)
		else:
			past_shows.append(artistInfo)
	
	venue.upcoming_shows = upcoming_shows
	venue.upcoming_shows_count = len(upcoming_shows)
	venue.past_shows = past_shows
	venue.past_shows_count = len(past_shows)
	
	
	return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
	# TODO: insert form data as a new Venue record in the db, instead
	# TODO: modify data to be the data object returned from db insertion
	error = False
	form = VenueForm(request.form)
	if form.validate():
		try:
			# get form data
			name = form.name.data
			city = form.city.data
			state = form.state.data
			address = form.address.data
			phone = form.phone.data
			genres = ",".join(form.genres.data)
			facebook_link = form.facebook_link.data
			image_link = form.image_link.data
			website_link = form.website_link.data
			seeking_talent = form.seeking_talent.data
			description = form.seeking_description.data

			aVenue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, looking_for_talent=seeking_talent, description=description)
			db.session.add(aVenue)
			db.session.commit()
		except:
			error = True
			db.session.rollback()
		finally:
			db.session.close()
		if error:
			# TODO: on unsuccessful db insert, flash an error instead.
			flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
			# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
			abort(500)
		else:
			# on successful db insert, flash success
			flash('Venue ' + request.form['name'] + ' was successfully listed!')
	else:
		print("\n\n", form.errors)
		flash("Venue was not listed successfully.")

	return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
	# TODO: Complete this endpoint for taking a venue_id, and using
	# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
	error = False
	try:
		venue = Venue.query.get(venue_id)
		db.session.delete(venue)
		db.session.commit()
	except:
		error = True
		db.session.rollback()
	finally:
		db.session.close()
	if error:
		# on unsuccessful delete, flash an error
		flash("Venue was not deleted successfully.")
	else:
		# on successful delete, flash success
		flash("Venue " + venue.name + " was deleted successfully!")

	# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
	# clicking that button delete it from the db then redirect the user to the homepage
	return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	# TODO: replace with real data returned from querying the database
	artists = db.session.query(Artist.id, Artist.name).order_by(desc('id')).all()
	return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
	# search for "band" should return "The Wild Sax Band".
	
	# get search keyword from the form
	search_term = request.form.get('search_term', '')
	
	# using 'ilike' in sqlalchemy.
	# Reference link below: 
	# http://docs.sqlalchemy.org/en/latest/orm/internals.html?highlight=ilike#sqlalchemy.orm.attributes.QueryableAttribute.ilike
	
	# Query All artists That Have The Search Keyword In Their Name
	found_artists = Artist.query.filter(
		Artist.name.ilike('%{}%'.format(search_term))
	).all()

	data = []
	# for each artist in the queried artists, get the id, name, and number of shows
	for eachArtist in found_artists:
		artist = {
			'id': eachArtist.id,
			'name': eachArtist.name
		}
		data.append(artist)
	
	response = {
		'count': len(data),
		'data': data
	}
	
	return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	# shows the artist page with the given artist_id
	# TODO: replace with real artist data from the artist table, using artist_id
	
	# query artist by artist_id
	artist = Artist.query.get(artist_id)
	
	# if the queried result is empty render a 404 page
	if not artist:
		return render_template('errors/404.html')
	
	shows = artist.shows # shows associated with the queried artist
	upcoming_shows = []
	past_shows = []
	
	# for each of the show in shows, get the venue name, image link and start time
	for show in shows:
		getVenueInfo = Show.query.join(Venue).with_entities(
            Show.venue_id,
            Venue.name,
            Venue.image_link,
            Show.start_time
		).filter(Show.artist_id==artist_id).first()

		venueInfo ={
			"venue_id": getVenueInfo[0],
			"venue_name": getVenueInfo[1],
			"venue_image_link": getVenueInfo[2],
			"start_time": format_datetime(str(getVenueInfo[3])), 
        }
		
		if show.start_time >= datetime.now():
			upcoming_shows.append(venueInfo)
		else:
			past_shows.append(venueInfo)
	
	artist.upcoming_shows = upcoming_shows
	artist.upcoming_shows_count = len(upcoming_shows)
	artist.past_shows = past_shows
	artist.past_shows_count = len(past_shows)

	return render_template('pages/show_artist.html', artist=artist)

#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	form = ArtistForm()
	artist = Artist.query.filter(Artist.id == artist_id).first()

	form.name.data = artist.name
	form.city.data = artist.city
	form.state.data = artist.state
	form.phone.data = artist.phone
	form.genres.data = artist.genres
	form.facebook_link.data = artist.facebook_link
	form.image_link.data = artist.image_link
	form.website_link.data = artist.website_link
	form.seeking_venue.data = artist.looking_for_venues
	form.seeking_description.data = artist.description
	
	# TODO: populate form with fields from artist with ID <artist_id>
	return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	# TODO: take values from the form submitted, and update existing
	# artist record with ID <artist_id> using the new attributes
	error = False

	if form.validate():
		try:
			# get form data
			name = request.form['name']
			city = request.form['city']
			state = request.form['state']
			phone = request.form['phone']
			genres = request.form.getlist('genres')
			facebook_link = request.form['facebook_link']
			image_link = request.form['image_link']
			website_link = request.form['website_link']
			seeking_venue = True if 'seeking_venue' in request.form else False
			description = request.form['seeking_description']
			
			updateArtist = Artist.query.get(artist_id)
			
			updateArtist.name = name
			updateArtist.city = city
			updateArtist.state = state
			updateArtist.phone = phone
			updateArtist.genres = genres
			updateArtist.facebook_link = facebook_link
			updateArtist.image_link = image_link
			updateArtist.website_link = website_link
			updateArtist.looking_for_venues = seeking_venue
			updateArtist.description = description
			
			db.session.commit()
		except:
			error = True
			db.session.rollback()
		finally:
			db.session.close()
		if error:
			flash('Oops! An error occurred. Artist ' + name + ' could not be Edited.')
			abort(500)
		else:
			flash('Artist ' + name + ' was successfully Edited!')
	else:
		print("\n\n", form.errors)
		flash("Artist was not edited successfully.")

	return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	form = VenueForm()
	venue = Venue.query.filter(Venue.id == venue_id).first()
	
	form.name.data = venue.name
	form.city.data = venue.city
	form.state.data = venue.state
	form.address.data = venue.address
	form.phone.data = venue.phone
	form.genres.data = venue.genres
	form.facebook_link.data = venue.facebook_link
	form.image_link.data = venue.image_link
	form.website_link.data = venue.website_link
	form.seeking_talent.data = venue.looking_for_talent
	form.seeking_description.data = venue.description
	
	# TODO: populate form with values from venue with ID <venue_id>
	return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	# TODO: take values from the form submitted, and update existing
	# venue record with ID <venue_id> using the new attributes
	error = False

	if form.validate():
		try:
			# get form data
			name = request.form['name']
			city = request.form['city']
			state = request.form['state']
			address = request.form['address']
			phone = request.form['phone']
			genres = request.form.getlist('genres')
			facebook_link = request.form['facebook_link']
			image_link = request.form['image_link']
			website_link = request.form['website_link']
			seeking_talent = True if 'seeking_talent' in request.form else False
			description = request.form['seeking_description']
			
			updateVenue = Venue.query.get(venue_id)

			updateVenue.name = name
			updateVenue.city = city
			updateVenue.state = state
			updateVenue.address = address
			updateVenue.phone = phone
			updateVenue.genres = genres
			updateVenue.facebook_link = facebook_link
			updateVenue.image_link = image_link
			updateVenue.website_link = website_link
			updateVenue.looking_for_talent = seeking_talent
			updateVenue.description = description
			
			db.session.commit()
		except:
			error = True
			db.session.rollback()
		finally:
			db.session.close()
		if error:
			flash('Oops! An error occurred. Venue ' + name + ' could not be Edited.')
			abort(500)
		else:
			flash('Venue ' + name + ' was successfully Edited!')
	else:
		print("\n\n", form.errors)
		flash("Venue was not edited successfully.")
	
	return redirect(url_for('show_venue', venue_id=venue_id))

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
	form = ArtistForm()
	return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
	# called upon submitting the new artist listing form
	# TODO: insert form data as a new Venue record in the db, instead
	# TODO: modify data to be the data object returned from db insertion
	error = False
	form = ArtistForm(request.form)
	
	if form.validate():
		try:
			# get form data
			name = form.name.data
			city = form.city.data
			state = form.state.data
			phone = form.phone.data
			genres = ",".join(form.genres.data)
			facebook_link = form.facebook_link.data
			image_link = form.image_link.data
			website_link = form.website_link.data
			seeking_venue = form.seeking_venue.data
			description = form.seeking_description.data

			anArtist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, looking_for_venues=seeking_venue, description=description)
			db.session.add(anArtist)
			db.session.commit()
		except:
			error = True
			db.session.rollback()
		finally:
			db.session.close()
		if error:
			# TODO: on unsuccessful db insert, flash an error instead.
			flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
			# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
			abort(500)
			print(sys.exc_info())
		else:
			# on successful db insert, flash success
			flash('Artist ' + request.form['name'] + ' was successfully listed!')
	else:
		print("\n\n", form.errors)
		flash("Artist was not successfully listed.")
	
	return render_template('pages/home.html')


#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
	# displays list of shows at /shows
	# TODO: replace with real venues data.
	
	shows = Show.query.order_by(desc('id')).all()
	for show in shows:
		show.venue_name = show.venue.name
		show.artist_name = show.artist.name
		show.artist_image_link = show.artist.image_link
	
	return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
	# renders form. do not touch.
	form = ShowForm()
	return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	# called to create new shows in the db, upon submitting new show listing form
	# TODO: insert form data as a new Show record in the db, instead
	error = False
	form = ShowForm(request.form)

	if form.validate():
		try:
			# get form data
			artist_id = request.form.get('artist_id')
			venue_id = request.form.get('venue_id')
			start_time = request.form.get('start_time')

			aShow = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
			db.session.add(aShow)
			db.session.commit()
		except:
			error = True
			db.session.rollback()
		finally:
			db.session.close()
		if error:
			# TODO: on unsuccessful db insert, flash an error instead.
			flash('An error occurred. Show could not be listed.')
			# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
			abort(500)
		else:
			# on successful db insert, flash success
			flash('The Show was successfully listed!')
	else:
		print("\n\n", form.errors)
		flash("Show was not successfully listed.")
	
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
    app.debug = True
    app.run(host="0.0.0.0")

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
