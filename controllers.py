"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and templates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import json
import random

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, logger, flash

from .common import auth, url_signer
from .models import get_user_email

@action('index')
@action.uses('index.html', session, auth.flash, db, auth)
def index():
    print("User: ", get_user_email())
    return dict()

@action("pokedex") # "Website/Pokerate/pokedex"
@action.uses("pokedex.html", session, auth.flash, url_signer, db, auth, T)
def pokedex():
    with open('apps/pokeRate/static/FullDex.json') as f:
        data = json.load(f)
    return dict(
        dexJSON = json.dumps(data),
        post_url = URL('post'),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer) 
    )

@action("setup")
@action.uses(db)
def setup():
    db(db.ratings).delete()
    db(db.derived_ratings).delete()
    with open('apps/pokeRate/static/FullDex.json') as f:
        data = json.load(f)
    i = 0
    emails = ["colin.orourke@icloud.com", "collin.orourke@icloud.com", "colllin.orourke@icloud.com", "collllin.orourke@icloud.com", "colllllin.orourke@icloud.com"]
    while (i < len(data['Pokemon'])):
    #    j = 0
    #    while (j < 3):
    #        ran = random.randint(1,5)
    #        db.ratings.insert(
    #            pokemon = data['Pokemon'][i]['id'],
    #            rater = emails[j],
    #            rating = ran
    #        )
    #        j += 1
        db.derived_ratings.insert(
            pokemon = data['Pokemon'][i]['id']
        )
        i += 1
    return "ok"

@action("post", method='POST')
def setup():
    print("Posted")
    return "ok"

@action("get_rating")
@action.uses(session, url_signer.verify(), db, auth)
def get_rating():
    pokID = request.params.get('pokID')
    
    userRatingRow = db((db.ratings.pokemon == pokID) & (db.ratings.rater == get_user_email()) & (db.ratings.rating != 6)).select().first()
    userRating = userRatingRow.rating if userRatingRow is not None else 0
    userFavorite = not ( db((db.ratings.pokemon == pokID) & (db.ratings.rater == get_user_email()) & (db.ratings.rating == 6)).isempty() )
    ratings = [0,0,0,0,0,0]
    ratings[0] = db((db.ratings.pokemon == pokID) & (db.ratings.rating == 1)).count()
    ratings[1] = db((db.ratings.pokemon == pokID) & (db.ratings.rating == 2)).count()
    ratings[2] = db((db.ratings.pokemon == pokID) & (db.ratings.rating == 3)).count()
    ratings[3] = db((db.ratings.pokemon == pokID) & (db.ratings.rating == 4)).count()
    ratings[4] = db((db.ratings.pokemon == pokID) & (db.ratings.rating == 5)).count()
    ratings[5] = db((db.ratings.pokemon == pokID) & (db.ratings.rating == 6)).count()
    return dict(
        oneRates = ratings[0],
        twoRates = ratings[1],
        threeRates = ratings[2],
        fourRates = ratings[3],
        fiveRates = ratings[4],
        sixRates = ratings[5],
        userRate = userRating,
        userFavorite = userFavorite
    )

@action("set_rating", method='POST')
@action.uses(session, url_signer.verify(), db, auth.flash, auth.enforce())
def set_rating():
    pokID = request.params.get('pokID')
    rating = request.params.get('rating')
    assert pokID is not None and rating is not None
    if (rating != 6):
        db.ratings.update_or_insert(
            ((db.ratings.pokemon == pokID) & (db.ratings.rater == get_user_email()) & (db.ratings.rating != 6)),
            pokemon = pokID,
            rater = get_user_email(),
            rating=rating,
        )
        return "ok"
    elif (rating == 6):
        #stuff
        mySet = db((db.ratings.rating == 6) & (db.ratings.rater == get_user_email()))
        thisRate = db((db.ratings.rating == 6) & (db.ratings.rater == get_user_email()) & (db.ratings.pokemon == pokID))
        if (mySet.count() < 10):
            if (thisRate.count() == 0):
                db.ratings.insert(
                    pokemon = pokID,
                    rater = get_user_email(),
                    rating = 6
                )
                return "ok"
            else:
                thisRate.delete()
                return "Ok"
        else:
            return "bad"
    return "ok"

@action("get_all_ratings")
@action.uses(session, url_signer.verify(), db, auth)
def get_all_ratings():
    allRatings = db().select(db.ratings.pokemon, db.ratings.rating, orderby=db.ratings.pokemon)
    userRatings = db((db.ratings.rater) == get_user_email()).select(db.ratings.pokemon, db.ratings.rating, orderby=db.ratings.pokemon)
    print(len(allRatings))
    return dict(
        allRatings = allRatings,
        userRatings = userRatings
    )