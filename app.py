import sys
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
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime
from flask_script import Manager
from models import *


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)
  
    app.jinja_env.filters['datetime'] = format_datetime


app = Flask(__name__)
moment = Moment(app)
app.config.from_object("Config")
db = SQLAlchemy(app)
migration = Migrate(app, db)


 
       



#controllers
@app.route('/')
def index():
    return render_template('pages/home.html')
# Venues--------------------


@app.route('/venues')
def venues():
    data = []
    venues = Venue.query.all()

    locations = set()

    for venue in venues:
        locations.add((venue.city, venue.state))

    for location in locations:
        data.append({
        "city": location[0],
        "state": location[1],
        "venues": []
        })

    for venue in venues:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()

        current_date = datetime.now()

    for show in shows:
      if show.start_time > current_date:
          num_upcoming_shows += 1

    for venue_location in data:
        if venue.state == venue_location['state'] and venue.city == venue_location['city']:
            venue_location['venues'].append({
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": num_upcoming_shows
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()
    

    response={
      "count": len(venues),
      "data": []
    }
    for venue in venues:
      response["data"].append({
        'id': venue.id,
        'name' : venue.name,
      })
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id = venue_id).first_or_404()
  past_shows = db.session.query(Artist,Show).join(Show).join(Venue).\
    filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time < datetime.now()
    ).\
    all()
    
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time > datetime.now()
    ).\
    all()
  

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    #"past_shows": past_shows,
    #"upcoming_shows": upcoming_shows,
    #"past_shows_count": len(past_shows),
    #"upcoming_shows_count": len(upcoming_shows)
    "past_shows": [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
    'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=data)




#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)  
    

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False
  try:
    new_venue = Venue(
      name = form.name.data,
      address = form.address.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      website = form.website.data,
      genres=form.genres.data,
      facebook_link = form.facebook_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data,
      image_link = form.image_link.data
      )
    db.session.add(new_venue)
    db.session.commit()
    #on successful db insert, flash success
    flash('Venue'+ form.name.data + 'successfuly added')
  except:
      #on failure , Error = true and will flash ERRORRRR with the venue name
      error = True
      flash('an error occurred. venue' + form.name.data +'ERRORRR!')
  finally:
      #close session and render the template!
      db.session.close()
  return render_template('pages/home.html')  

  



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  venue_id = request.form.get('venue_id')
  deleted_venue = Venue.query.get(venue_id)
  venueName = delete_venue.name
  try:
    db.session.delete(deleted_venue)
    db.session.commit()
    flash('Venue ' + venueName + '  deleted!')  

  except:
    db.session.rollback()
    flash('try again.venue' + venueName + 'Not able to delete')

  finally:
    db.session.close()



  return redirect(url_for('index'))  


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term','')
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()

  response={
    "count": result.count(),
    "data": []
  }
  for artist in results:
    response['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

    

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
      artist = Artist.query.filter_by(id = artist_id).first_or_404
      
      past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
        ).\
        all()
      upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
        ).\
        all()

        
      data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.split(','), 
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description":artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }
      return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  #error if can not find the artist!
  if artist is None:
    raise TypeError("No artist under this ID")
  
  

  artist_data={
      "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link

    
  }
  
     
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.genres = request.form['genres']
  artist.image_link = request.form['image_link']
  artist.website = request.form['website']
  try:
      db.session.commit()
      flash("Artist {} is updated ".format(artist.name))

  except:
    db.session.rollback()
    flash("Artist {} isn't updated successfully".format(artist.name))    

  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue is None:
    return not_found_error(404)
  venue_info={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_info)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.genres = request.form['genres']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + new_venue.name + ' Venue Not updated.')
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
   form = ArtistForm(request.form)
   try:
     
    artist = Artist(name=form.name.data, 
                    city=form.city.data, 
                    state=form.city.data,
                      phone=form.phone.data, 
                      genres=form.genres.data, 
                      image_link=form.image_link.data, 
                      facebook_link=form.facebook_link.data)
    db.session.add(artist)
    db.session.commit()
    
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
   except:
      db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')

   finally:
      db.session.close()
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows_list = db.session.query(Show).join(Artist).join(Venue).all()

  data = []

  for show in shows_list:
    if(show.upcoming):
      data.append({
        "venue_id" : show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
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
  form = ShowForm(request.form)
  try:
    new_show = Show(
      venue_id = request.form['venue_id'],
      artist_id = request.form['artist_id'],
      start_time = request.form['start_time'],
    )
    db.session.add(new_show)
    db.session.commit()
    flash('show was added')
  except:
    db.session.rollback()
    flash('Error occurred')
  
  finally:
    db.session.close()  

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




# Launch.


# Default port:
if __name__ == '__main__':

  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''