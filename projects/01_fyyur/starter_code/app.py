#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show
from datetime import datetime
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    area = db.session.query(Venue.state, Venue.city).group_by(
        Venue.state, Venue.city).all()
    return v(area)


def v(area):
    let_venue_data = []
    l_venue(area, let_venue_data)
    return render_template('pages/venues.html', areas=let_venue_data)

def l_venue(area, let_venue_data):
    for v in area:
        venues = db.session.query(Venue.id, Venue.name, Venue.upcoming_shows_count).filter(
            Venue.state == v[0], Venue.city == v[1]).all()
        a(let_venue_data, v)
        f_venue(let_venue_data, venues)

def f_venue(let_venue_data, venues):
    for new_venue in venues:
        let_venue_data[-1]["venues"].append(
                {"id": new_venue[0], "name": new_venue[1]})


def a(let_venue_data, v):
    let_venue_data.append({"city": v[0], "state": v[1], "venues": []})


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    return new_search()


def new_search():
    view_results = Venue.query.filter(Venue.name.ilike(
        '%{}%'.format(request.form['search_term']))).all()
    response = {"count": len(view_results), "data": []}
    for venue in view_results:
        response["data"].append({"id": venue.id, "name": venue.name, "num_upcoming_shows": venue.upcoming_shows_count
                                 })
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    request_venue_data = db.session.query(Venue).get(venue_id)
    previous_shows, next_shows = p_n_show(venue_id)
    last_shows = []
    new_shows = []
    for show in previous_shows:
        p_shows(last_shows, show)
    for show in next_shows:
        n_shows(new_shows, show)
    venue_data = {
        "id": request_venue_data.id,
        "name": request_venue_data.name,
        "genres": request_venue_data.genres,
        "address": request_venue_data.address,
        "city": request_venue_data.city,
        "state": request_venue_data.state,
        "phone": request_venue_data.phone,
        "website_link": request_venue_data.website_link,
        "facebook_link": request_venue_data.facebook_link,
        "seeking_talent": request_venue_data.seeking_talent,
        "seeking_description": request_venue_data.seeking_description,
        "image_link": request_venue_data.image_link,
        "past_shows": last_shows,
        "upcoming_shows": new_shows,
        "past_shows_count": len(last_shows),
        "upcoming_shows_count": len(new_shows)
    }
    data = list(filter(lambda d: d['id'] == venue_id, [venue_data]))[0]
    return render_template('pages/show_venue.html', venue=data)


def n_shows(new_shows, show):
    new_shows.append({"artist_id": show.artist_id, "artist_name": show.artist.name,
                      "artist_image_link": show.artist.image_link, "start_time": str(show.start_time)})


def p_shows(last_shows, show):
    last_shows.append({"artist_id": show.artist_id, "artist_name": show.artist.name,
                       "artist_image_link": show.artist.image_link, "start_time": str(show.start_time)})


def p_n_show(venue_id):
    previous_shows = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
    next_shows = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

    return previous_shows, next_shows

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET', 'POST'])
def create_venue_form():
    form = VenueForm()
    if form.validate_on_submit():
        # try:
        contact = form.phone.data
        if contact:
            return create_venue_submission()
        # except:
            # db.session.close()
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        enlist_venue()
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/home.html')


def enlist_venue():
    db.session.add(Venue(
        name=request.form.get('name'),
        city=request.form.get('city'),
        state=request.form.get('state'),
        address=request.form.get('address'),
        phone=request.form.get('phone'),
        image_link=request.form.get('image_link'),
        facebook_link=request.form.get('facebook_link'),
        website_link=request.form.get('website_link'),
        genres=request.form.getlist('genres'),
        seeking_description=request.form.get('seeking_description'),
        seeking_talent=request.form.get('seeking_talent')
    ))


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using

    try:
        get_name = del_venue()
        flash('Venue ' + get_name + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('please try again. Venue ' + get_name + ' could not be deleted.')
    finally:
        db.session.close()
        # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

        # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
        # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')


def del_venue():
    venue_id = request.form.get('venue_id')
    removed_venue = Venue.query.get(venue_id)
    get_name = removed_venue.name
    db.session.delete(removed_venue)
    db.session.commit()
    return get_name

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # data = Artist.query.with_entities(Artist.id, Artist.name).all()
    data = db.session.query(Artist).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artist_search_results = db.session.query(Artist).filter(
        Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()
    # artist_search_results = Artist.query.filter(
    #     Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()
    try:
        response = {"count": len(artist_search_results), "data": []}
        for a in artist_search_results:
            response['data'].append(
                {"id": a.id, "name": a.name, "num_upcoming_shows": a.upcoming_shows_count})
    except:
        db.session.rollback()
        flash('Error! No data found')
    finally:
        db.session.close()
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    request_artist_data = db.session.query(Artist).get(artist_id)
    previous_shows, next_shows, last_shows = show_existing_artist(artist_id)
    new_shows = []
    get_artist_data(previous_shows, next_shows, last_shows, new_shows)
    artist_data = {
        "id": request_artist_data.id,
        "name": request_artist_data.name,
        "genres": request_artist_data.genres,
        "city": request_artist_data.city,
        "state": request_artist_data.state,
        "phone": request_artist_data.phone,
        "website_link": request_artist_data.website_link,
        "facebook_link": request_artist_data.facebook_link,
        "seeking_venue": request_artist_data.seeking_venue,
        "seeking_description": request_artist_data.seeking_description,
        "image_link": request_artist_data.image_link,
        "past_shows": last_shows,
        "upcoming_shows": new_shows,
        "past_shows_count": len(last_shows),
        "upcoming_shows_count": len(new_shows)
    }
    data = list(filter(lambda d: d['id'] == artist_id, [artist_data]))[0]
    return render_template('pages/show_artist.html', artist=data)


def get_artist_data(previous_shows, next_shows, last_shows, new_shows):
    for show in previous_shows:
        last_shows.append({"venue_id": show.venue_id, "venue_name": show.venue.name,
                          "venue_image_link": show.venue.image_link, "start_time": str(show.start_time)})
    for show in next_shows:
        new_shows.append({"venue_id": show.venue_id, "venue_name": show.venue.name,
                         "venue_image_link": show.venue.image_link, "start_time": str(show.start_time)})


def show_existing_artist(artist_id):
    previous_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
    next_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    last_shows = []
    return previous_shows, next_shows, last_shows


@app.route('/artists/delete', methods=['POST'])
def delete_artist():
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    a_id = request.form.get('artist_id')
    removed_artist = Artist.query.get(a_id)
    get_name = removed_artist.name
    try:
        db.session.delete(removed_artist)
        db.session.commit()
        flash('Artist ' + get_name + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('please try again. Venue ' + get_name + ' could not be deleted.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    artists = Artist.query.get(artist_id)
    artist = {
        "id": artists.id,
        "name": artists.name,
        "genres": artists.genres,
        "city": artists.city,
        "state": artists.state,
        "phone": artists.phone,
        "website_link": artists.website_link,
        "facebook_link": artists.facebook_link,
        "seeking_venue": artists.seeking_venue,
        "seeking_description": artists.seeking_description,
        "image_link": artists.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.genres = request.form['genres']
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']
    try:
        db.session.commit()
        flash("Artist {} is updated successfully".format(artist.name))
    except:
        db.session.rollback()
        flash("Artist {} isn't updated successfully".format(artist.name))
    finally:
        db.session.close()
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venues = Venue.query.get(venue_id)
    venue = {
        "id": venues.id,
        "name": venues.name,
        "genres": venues.genres,
        "address": venues.address,
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "website_link": venues.website_link,
        "facebook_link": venues.facebook_link,
        "seeking_talent": venues.seeking_talent,
        "seeking_description": venues.seeking_description,
        "image_link": venues.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venues)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.genres = request.form['genres']
    venue.image_link = request.form['image_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = request.form['seeking_talent']
    venue.seeking_description = request.form['seeking_description']
    try:
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be updated.')
    finally:
        db.session.close()

    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=('GET', 'POST'))
def create_artist_form():
    form = ArtistForm()
    if form.validate_on_submit():
        contact = form.phone.data
        if contact:
            return create_artist_submission()
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    try:

        n_artist()
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Error! Artist ' + request.form['name'] + ' could not be added')
    finally:
        db.session.close()
       # TODO: on unsuccessful db insert, flash an error instead.

    return render_template('pages/home.html')


def n_artist():
    db.session.add(Artist(
        name=request.form.get('name'),
        city=request.form.get('city'),
        state=request.form.get('state'),
        phone=request.form.get('phone'),
        image_link=request.form.get('image_link'),
        facebook_link=request.form.get('facebook_link'),
        website_link=request.form.get('website_link'),
        genres=request.form.getlist('genres'),
        seeking_description=request.form.get('seeking_description'),
        seeking_venue=request.form.get('seeking_venue'))
    )

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    list_of_shows = Show.query.all()
    data = []
    for new_show in list_of_shows:
        n_show(data, new_show)
    return render_template('pages/shows.html', shows=data)


def n_show(data, new_show):
    data.append({"venue_id": new_show.venue_id,
                 "venue_name": new_show.venue.name,
                 "artist_id": new_show.artist_id,
                "artist_name": new_show.artist.name,
                 "artist_image_link": new_show.artist.image_link,
                 "start_time": str(new_show.start_time)})


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    if form.validate_on_submit():
        artist = request.artist_id.data
        venue = request.venue_id.data
        if venue and artist:
            return create_show_submission()
    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    try:
        enlist_show = e_show()
        db.session.add(enlist_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
        flash('Show could not be listed. please make sure that your ids are correct')
    finally:
        db.session.close()
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


def e_show():
    enlist_show = Show(artist_id=request.form['artist_id'],
                       venue_id=request.form['venue_id'],
                       start_time=request.form['start_time'])

    return enlist_show


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
