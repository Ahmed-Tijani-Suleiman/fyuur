#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask_migrate import Migrate
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy, models_committed
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
import sys
from forms import *
from models import Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
#-----------------------------------------------------------------------------#
#Models
#------------------------------------------------------------------------------#



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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

@app.route('/venues', methods=['GET'])
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
 
  data_agg= db.session.query(func.count(Venue.id), Venue.state, Venue.city).group_by(Venue.state, Venue.city).all()
  data=[]
  for i in data_agg:
    data_set = Venue.query.filter_by(state=i.state).filter_by(city=i.city).all()
    venue_data = []
    for venue in data_set:
      venue_data.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(Show.query.filter(Show.start_time>datetime.now()).all())
      })
    data.append({
      "city": i.city,
      "state": i.state, 
      "venues": venue_data
    })
  return render_template('pages/venues.html', areas=data)

  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  values = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike(f'%{values}%')).all()
  
  response = {
        "count": len(data),
        "data": data
    }

  return render_template('pages/search_venues.html', results=response, search_term=values)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    data= Venue.query.get(venue_id)

    past_shows = db.session.query(Show).filter(data.id==Show.venue_id).filter(Show.start_time < datetime.now()).all()
    past_shows_data = []
    for show in past_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            past_shows_data.append(show_data)

    upcoming_shows = db.session.query(Show).filter(data.id==Show.venue_id).filter(Show.start_time >= datetime.now()).all()
    upcoming_shows_data = []
    for show in upcoming_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            upcoming_shows_data.append(show_data)

    data_values = {
            "id": data.id,
            "name": data.name,
            "genres": data.genres,
            "address": data.address,
            "city": data.city,
            "state": data.state,
            "phone": data.phone,
           
            "facebook_link": data.facebook_link,
            "seeking_talent": data.seeking_talent,
            "image_link": data.image_link,
            "past_shows": past_shows_data,
            "upcoming_shows": upcoming_shows_data,
            "past_shows_count": len(past_shows_data),
            "upcoming_shows_count": len(upcoming_shows_data),
        }


    return render_template('pages/show_venue.html', venue=data_values)

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
    try:
        venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            website_link =request.form['website_link'],
            seeking_talent= True if 'seeking_talent' in request.form else False,
            seeking_description=request.form['seeking_description']
        )
        db.session.add(venue)
        db.session.commit()
    # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be added')
        
    finally:
        db.session.close()
    
  
    return render_template('pages/home.html')
   
  
  
  
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue = Venue.query.get(venue_id)
  try:
        venue.delete()
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted!')
  except SQLAlchemyError as e:
        print(e.__traceback__)
        db.session.rollback()
        flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
        
  finally:
        db.session.close()


  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = Artist.query.order_by('name').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  user_input = request.form.get('search_term')
  data= Artist.query.filter(Artist.name.ilike(f'%{user_input}%')).all()
  
  response = {
        "count": len(data),
        "data": data
    }


  return render_template('pages/search_artists.html', results=response, search_term=user_input)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    data= Artist.query.get(artist_id)

    past_shows = db.session.query(Show).filter(data.id==Show.artist_id).filter(Show.start_time < datetime.now()).all()
    past_shows_data = []
    for show in past_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            past_shows_data.append(show_data)

    upcoming_shows = db.session.query(Show).filter(data.id==Show.artist_id).filter(Show.start_time >= datetime.now()).all()
    upcoming_shows_data = []
    for show in upcoming_shows:
            artist = Artist.query.get(show.artist_id)
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
            upcoming_shows_data.append(show_data)
    

    response = {
        "id": data.id,
        "name": data.name,
        "genres": data.genres,
        "city": data.city,
        "state": data.state,
        "phone": data.phone,
        "website": data.website_link,
        "facebook_link": data.facebook_link,
        "seeking_description": data.seeking_description,
        "image_link": data.image_link,
        "past_shows": past_shows_data,
        "upcoming_shows": upcoming_shows_data,
        "past_shows_count": len(past_shows_data),
        "upcoming_shows_count": len(upcoming_shows_data),
    }
    return render_template('pages/show_artist.html', artist=response)
  
  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id> -completed
  return render_template('forms/edit_artist.html', form=form, artist=artist)
  

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)

  try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        db.session.commit()
        flash('Artist ' + artist.name + '\'s data was successfully updated')
  except SQLAlchemyError as e:
        print(e.__traceback__)
        db.session.rollback()
        flash('An error occurred. Artist ' + artist.name + '\'s data could not be updated.')
      
  finally:
        db.session.close()
  

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  updated = True

  try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        db.session.commit()
  except SQLAlchemyError as e:
        print(e.__traceback__)
        db.session.rollback()
        updated = False
  finally:
        db.session.close()

  if updated:
        flash('Venue ' + venue.name + '\'s data was successfully updated')
  else:
        flash('An error occurred. Venue ' + venue.name + '\'s data could not be updated.')

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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  artist = Artist(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        genres=request.form.getlist('genres'),
        image_link=request.form['image_link'],
        facebook_link=request.form['facebook_link'],
        website=request.form['website_link'],
        seeking_description=request.form['seeking_description']
        
       
        
    )
  saved = True

  try:
        db.session.add(artist)
        db.session.commit()
  except SQLAlchemyError as e:
        print(e.__traceback__)
        db.session.rollback()
        saved = False
  finally:
        db.session.close()

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead -completed
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  if saved:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
        flash('An error occurred. Artist ' + request.form['name'] + 'could not be listed.')

    
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  shows = Show.query.join(Artist).join(Venue).all()
  print(shows)
  if not shows: 
    flash('no shows exists') 
    return render_template('pages/shows.html')
  for show in shows:
    data.append({
     "venue_id": show.venue_id,
     "venue_name": show.Venue.name,
     "artist_id": show.artist_id,
     "artist_name": show.Artist.name,
     "artist_image_link": show.Artist.image_link,
     "start_time": str(show.start_time)
   })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  failed = False
  try: 
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed')
  except: 
    flash('An error occurred. Show could not be listed.')
    failed = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead -completed
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
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
