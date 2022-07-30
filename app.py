#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean(), default = False)
    seeking_description = db.Column(db.String(120))
    show = db.relationship('Show', backref = 'venue', lazy = True)

    def __repr__(self):
      return f'<Venue {self.name} {self.city}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default = False)
    seeking_description = db.Column(db.String(200))
    show = db.relationship('Show', backref = 'artist', lazy = True)

    def __repr__(self):
      return f'<Artist {self.name} {self.city}'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key = True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable = False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
  start_time = db.Column(db.DateTime(), nullable = False)

  def __repr__(self):
    return f'<Show {self.venue}>'
  

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  data = Venue.query.all()
  return render_template('pages/venues.html', areas=data, venues=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venue = request.form.get('search_term')
  response= Venue.query.filter((Venue.name.ilike('%' + venue + '%')))


  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)
  upcoming_shows_all = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time > datetime.utcnow()).all()
  past_shows_all = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time <= datetime.utcnow()).all()

  data.upcoming_shows = upcoming_shows_all
  data.past_shows = past_shows_all
  data.upcoming_shows_count = len(upcoming_shows_all)
  data.past_shows_count = len(past_shows_all)
  return render_template('pages/show_venue.html', venue=data)

#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  if form.validate():
    try:
      new_venue = Venue(
        name = request.form.get('name'), city = request.form.get('city'), 
        state = request.form.get('state'), address = request.form.get('address'),
        phone = request.form.get('phone'), image_link = request.form.get('image_link'),
        genres = request.form.getlist('genres'), facebook_link = request.form.get('facebook_link'), 
        website_link = request.form.get('website_link'), looking_for_talent = True if request.form.get('seeking_talent') == 'y' else False,
        seeking_description = request.form.get('seeking_description')
      )
      db.session.add(new_venue)
      db.session.commit()
        # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      return redirect(url_for('index'))
  else:
    flash('An error occurred with the form. Please make sure the values entered are valid')
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
#Show Artists

@app.route('/artists')
def artists():
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

#Search for Artists
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artist = request.form.get('search_term')
  response= Artist.query.filter((Artist.name.ilike('%' + artist + '%')))

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#Show Specific Artist
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.get(artist_id)
  upcoming_shows_all = Show.query.join(Artist, Show.artist_id == artist_id).filter(Show.start_time > datetime.utcnow()).all()
  past_shows_all = Show.query.join(Artist, Show.artist_id == artist_id).filter(Show.start_time <= datetime.utcnow()).all()

  data.upcoming_shows = upcoming_shows_all
  data.past_shows = past_shows_all
  data.upcoming_shows_count = len(upcoming_shows_all)
  data.past_shows_count = len(past_shows_all)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue.name = request.form.get('name')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.address = request.form.get('address')
  venue.phone = request.form.get('phone')
  venue.image_link = request.form.get('image_link')
  venue.genres = request.form.getlist('genres')
  venue.facebook_link = request.form.get('facebook_link')
  venue.website_link = request.form.get('website_link')
  venue.looking_for_talent = True if request.form.get('seeking_talent') == 'y' else False,
  venue.seeking_description = request.form.get('seeking_description')

  db.session.add(venue)
  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  if form.validate():
    try:
      new_artist = Artist(
        name = request.form.get('name'), city = request.form.get('city'), 
        state = request.form.get('state'), phone = request.form.get('phone'),
        image_link = request.form.get('image_link'), genres = request.form.getlist('genres'), 
        facebook_link = request.form.get('facebook_link'), website_link = request.form.get('website_link'),
        seeking_venue = True if request.form.get('seeking_talent') == 'y' else False, seeking_description = request.form.get('seeking_description')
      )
      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      # TODO: on unsuccessful db insert, flash an error instead.
      db.session.rollback()
      flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    finally:
      return redirect(url_for('index'))
  else:
    flash('Error. Please check the form and ensure the values entered are valid')
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  if form.validate():
    try:
      new_show = Show(artist_id = request.form.get('artist_id'), venue_id = request.form.get('venue_id'),
        start_time = request.form.get('start_time')
      )
      db.session.add(new_show)
      db.session.commit()
        # on successful db insert, flash success
      flash('Show was successfully listed!')
    except:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      return render_template('pages/home.html')
  else:
    flash('Show could not be created. Please make sure valid values are entered in the form')
    return redirect(url_for('index'))

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
