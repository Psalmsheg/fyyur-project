past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()   
    # upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
    # past_shows = []
    # upcoming_shows = []
    # for show in past_shows_query:
    #     past_shows.append = (
    #         { "artist_id": show.artist_id, "artist_name": show.artist.name, "artist_image_link": show.artist.image_link,
    #             "start_time": str(show.start_time)}
    #     )    
    # for show in upcoming_shows_query:
    #     upcoming_shows.append(
    #         { "artist_id": show.artist_id, "artist_name": show.artist.name, "artist_image_link": show.artist.image_link,
    #             "start_time": str(show.start_time)}
    #     )