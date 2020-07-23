#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
import sys
from sqlalchemy.orm import joinedload
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate=Migrate(app,db) 
defaultdate= datetime.now()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
#shows= db.Table('shows',
#    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
#    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
#    db.Column('start', db.String)
#)
class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres =db.Column(db.String(300))
    website= db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show =db.relationship('Show', backref='venue', lazy=False)
   # artists = db.relationship('Artist', secondary=shows,
   # backref=db.backref('venue', lazy=True))
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(300))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website= db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show =db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start= db.Column(db.String(100))
    artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'))
    venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'))
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
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
#RETRIVE ALL VENUES
@app.route('/venues')
def venues():
  venuerecords=[]
  data=[]
  

  #getdistinct city+state list
  city_state = db.session.query(Venue.city,Venue.state).distinct().all()
  for i in city_state:
    record={
    "city": "",
    "state": "",
    "venues": [] 
   }

    record['city']=i[0]
    record['state']=i[1]
    #result based on city+state
    venueresults=Venue.query.filter_by(city=i[0],state=i[1]).outerjoin(Show).all()
    print(len(venueresults))
    for j in venueresults:
      venue={
      "id": 1,
      "name": "",
      "num_upcoming_shows": 0,
    }
      venue['id']=j.id
      venue['name']=j.name
      for k in j.show:
        if datetime.strptime(k.start,'%Y-%m-%d %H:%M:%S')>= defaultdate:
          venue['num_upcoming_shows']+=1
      record['venues'].append(venue)
    data.append(record)
  #print(record)
  print(data)      


  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=name=request.form.get('search_term')
  exp='%'+search_term+'%'
  print(exp)
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
 
  venueresults=Venue.query.filter(Venue.name.ilike(exp)).outerjoin(Show).all()
  v=[]
  response={}
  for i in venueresults:
    result={
      "id": 0,
      "name": "",
      "num_upcoming_shows": 0,
    }
    count=0
    result['id']=i.id
    result['name']=i.name
    for j in i.show:
       if datetime.strptime(j.start,'%Y-%m-%d %H:%M:%S')>= defaultdate:
          count+=1
    result['num_upcoming_shows']=count
    v.append(result)
    
    response={
    "count": len(venueresults),
    "data": v
  }

  # response={
  #   "count": len(venueresults),
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

def getArtist(artist_id):
  return Artist.query.filter(Artist.id==artist_id).first()
   

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 
  past_shows=[]
  upcoming_shows=[]
  upcoming_shows_count=0
  past_shows_count=0

  venue= Venue.query.filter(Venue.id==venue_id).first()
  #print('/venues/<int:venue_id> ',venue_id,' ',venue)
  for show in venue.show:
    if datetime.strptime(show.start,'%Y-%m-%d %H:%M:%S')>= defaultdate:
      upcoming_shows_count+=1
      a=getArtist(show.artist_id)
      artistData={"artist_id": a.id,
      "artist_name": a.name,
      "artist_image_link":a.image_link,
      "start_time": show.start
      }
      upcoming_shows.append(artistData)  
        
    else:
      past_shows_count+=1
      a=getArtist(show.artist_id)
      artistData={"artist_id": a.id,
      "artist_name": a.name,
      "artist_image_link":a.image_link,
      "start_time": show.start
      }
      past_shows.append(artistData)
        
      
  
  data1={
    "id":venue.id,
    "name": venue.name,
    "genres":convertString(venue.genres),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------
def convertlist(items_list):
    str=""
    for item in items_list:
        if len(str) == 0:
            str = item
        else:
            str = str + "," + item    
            return str

def convertString(str):
 list = str.split(",")
 return list

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
  error = False
  try:
    name=request.form.get('name')
    city=request.form.get('city')
    state=request.form.get('state')
    address=request.form.get('address')
    facebook_link=request.form.get('facebook_link')
    genres=convertlist(request.form.getlist('genres'))
    phone=request.form.get('phone')
    venu = Venue(name=name,city=city,state=state,address=address,facebook_link=facebook_link,genres=genres,
    phone=phone)
    db.session.add(venu)
    db.session.commit()
      # on successful db insert, flash success
    flash('Venue ' + name+ ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
     # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue=Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue with id = ' + venue_id+ ' was successfully Deleted!')
  except:
    error = True
    db.session.rollback()
    #print(sys.exc_info())
    flash('An error occurred. Venue with id= ' + venue_id + ' could not be Deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data=[]
  artist=Artist.query.all()
  for a in artist:
    artist={
    "id": 0,
    "name": ""
    }
    artist['id']=a.id
    artist['name']=a.name
    data.append(artist)
  # TODO: replace with real data returned from querying the database
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=name=request.form.get('search_term')
  exp='%'+search_term+'%'
  print(exp)
  artistresults=Artist.query.filter(Artist.name.ilike(exp)).outerjoin(Show).all()
  v=[]
  response={}
  for i in artistresults:
    result={
      "id": 0,
      "name": "",
      "num_upcoming_shows": 0,
    }
    count=0
    result['id']=i.id
    result['name']=i.name
    for j in i.show:
       if datetime.strptime(j.start,'%Y-%m-%d %H:%M:%S')>= defaultdate:
          count+=1
    result['num_upcoming_shows']=count
    v.append(result)
    
    response={
    "count": len(artistresults),
    "data": v
  }


  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
def getVenue(id):
  return Venue.query.filter(Venue.id==id).first()


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows=[]
  upcoming_shows=[]
  upcoming_shows_count=0
  past_shows_count=0

  artist= Artist.query.filter(Artist.id==artist_id).first()
  for show in artist.show:
    if datetime.strptime(show.start,'%Y-%m-%d %H:%M:%S')>= defaultdate:
      upcoming_shows_count+=1
      v=getVenue(show.venue_id)
      
      venueData={
      "venue_id": v.id,
      "venue_name": v.name,
      "venue_image_link":v.image_link,
      "start_time": show.start
      }
      upcoming_shows.append(venueData)  
        
    else:
      past_shows_count+=1
      v=getVenue(show.venue_id)
      venueData={
      "venue_id": v.id,
      "venue_name": v.name,
      "venue_image_link":v.image_link,
      "start_time": show.start
      }
      past_shows.append(venueData)

  data1={
    "id": artist.id,
    "name": artist.name,
    "genres": convertString(artist.genres),
    "city": artist.city,
    "state":artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue":artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link":artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  
  data = list(filter(lambda d: d['id'] == artist_id, [data1]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist= Artist.query.filter(Artist.id==artist_id).first()
  form = ArtistForm()
  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": convertString(v.genres),
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
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  v= Venue.query.filter(Venue.id==venue_id).first()
  
  venue={
    "id": v.id,
    "name": v.name,
    "genres": convertString(v.genres),
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description":v.seeking_description,
    "image_link": v.image_link
  }
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # TODO: insert form data as a new Venue record in the db, instead
  error = False
  try:
    name=request.form.get('name')
    city=request.form.get('city')
    state=request.form.get('state')
    address=request.form.get('address')
    facebook_link=request.form.get('facebook_link')
    genres=convertlist(request.form.getlist('genres'))
    phone=request.form.get('phone')
    artist = Artist(name=name,city=city,state=state,address=address,facebook_link=facebook_link,genres=genres,
    phone=phone)
    db.session.add(artist)
    db.session.commit()
      # on successful db insert, flash success
    flash('Artist ' + name+ ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
     # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
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
  data=[]
  show=Show.query.all()
  for s in show:
    v=getVenue(s.venue_id)
    a=getArtist(s.artist_id)
    print(v)
    print(a)
    record = {
      "venue_id": 0,
      "venue_name": "",
      "artist_id": 0,
      "artist_name": "",
      "artist_image_link": "",
      "start_time": ""
    }
    record['venue_id'] = v.id
    record['venue_name'] = v.name
    record['artist_id'] = a.id
    record['artist_name']=a.name
    record['artist_image_link']=a.image_link
    record['start_time']=s.start
    data.append(record)
  
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
  error = False
  try:
    start=request.form.get('start_time')
    artist_id=request.form.get('artist_id')
    venue_id=request.form.get('venue_id')
    show = Show(start=start,artist_id=artist_id,venue_id=venue_id)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('show was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
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
