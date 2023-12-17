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
import math
from datetime import datetime, timedelta
import time
import calendar

import smtplib
from smtplib import SMTP
from email.message import EmailMessage
import os
import ssl

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, myMailer, session, T, cache, logger, flash

from .common import auth, url_signer_short, url_signer_long
from .models import get_user_email
from .__init__ import __version__

#REMOTE_ADDR when running local container
#HTTP_X_FORWARDED_FOR when running on ECS
USER_IP_KEY_AWS = "HTTP_X_FORWARDED_FOR"
USER_IP_KEY_DOCKER = "REMOTE_ADDR"

# Main Home Page
@action('home')
@action('index')
@action.uses('home.html', session, auth.flash, url_signer_long, db, auth)
def index():
    # Load the static data of every pokemon 
    return indexDict(db, url_signer_long)

# Page that displays all the pokemon.
@action("pokedex")
@action.uses("pokedex.html", session, auth.flash, url_signer_long, db, auth, T)
def pokedex():
    # Load the static data of every pokemon 
    data = json.loads(db(db.pokemonTable).select().as_json())

    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer_long),
        set_rating_url = URL('set_rating', signer=url_signer_long),
        remove_rating_url = URL('remove_rating', signer=url_signer_long),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer_long),
        req_delete_url = URL('request_delete', signer=url_signer_long),
        target_poke = "000000",
        __version__ = __version__
    )

@action("userdex")
@action.uses("userdex.html", session, auth.flash, url_signer_long, db, auth, T)
def pokedex():
    # Load the static data of every pokemon 
    data = json.loads(db(db.pokemonTable).select().as_json())

    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer_long),
        set_rating_url = URL('set_rating', signer=url_signer_long),
        remove_rating_url = URL('remove_rating', signer=url_signer_long),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer_long),
        req_delete_url = URL('request_delete', signer=url_signer_long),
        target_poke = "000000",
        __version__ = __version__
    )

# Page that displays all the pokemon.
# Having a number acutomatically launches the modal of a certain pokemon
@action("pokedex/<number>")
@action.uses("pokedex.html", session, auth.flash, url_signer_long, db, auth, T)
def pokedex(number):
    # Load the static data of every pokemon 
    data = json.loads(db(db.pokemonTable).select().as_json())

    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer_long),
        set_rating_url = URL('set_rating', signer=url_signer_long),
        remove_rating_url = URL('remove_rating', signer=url_signer_long),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer_long),
        req_delete_url = URL('request_delete', signer=url_signer_long),
        target_poke = number,
        __version__ = __version__
    )

# Page that displays the ranking data of all the pokemon.
@action("rankings")
@action.uses('data.html', session, auth.flash, url_signer_long, db, auth, T)
def data():
    # Load the static data of every pokemon 
    data = json.loads(db(db.pokemonTable).select().as_json())

    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer_long),
        set_rating_url = URL('set_rating', signer=url_signer_long),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer_long),
        req_delete_url = URL('request_delete', signer=url_signer_long),
        pokedex_url = URL('pokedex'),
        __version__ = __version__
    )

# Page that plays a daily puzzle
@action("puzzle")
@action.uses('puzzle.html', session, auth.flash, url_signer_long, db, auth, T)
def data():
    # Load the static data of every pokemon 
    data = json.loads(db(db.pokemonTable).select().as_json())

    # Select the puzzle pokemon of the day
    seed = dateSeed() * 2
    seed = BlumBlumShub(seed)
    seed = BlumBlumShub(seed)
    targetPoke = data[(int(seed) % len(data))]

    # If selected puzzle pokemon is invalid, select again until one is valid
    while (targetPoke['form'] != "Basic"):
        seed = BlumBlumShub(seed)
        targetPoke = data[(int(seed) % len(data))]

    return dict(
        dexJSON = json.dumps(data),
        myTargetPokemon = json.dumps(targetPoke),
        get_rating_url = URL('get_rating', signer=url_signer_long),
        pokedex_url = URL('pokedex'),
        req_delete_url = URL('request_delete', signer=url_signer_long),
        get_plays_url = URL('get_puzzle_play', signer=url_signer_long),
        post_plays_url = URL('post_puzzle_play', signer=url_signer_long)
    )

#----------------------------------------#
# SETUP URL IS PURELY FOR DATABASE ADMINISTRATION PURPOSES
# THIS URL SHOULD NEVER BE LIVE IN THE PRODUCTION CONTAINER
# ONLY LIVE ON AN ADMINISTRATORS LOCAL MACHINE
# SAME GOES FOR ADD URL
#----------------------------------------#

# @action("puzzletest")
# @action.uses(db)
# def puzzletest():
#     db.puzzle_plays.insert(
#         date = "nonsense",
#         user = "nonsense",
#         guesses = "nonsense",
#         guessCount = "6",
#         success = False
#     )

# @action("setup")
# @action.uses(db)
# def setup():
#     start = time.perf_counter()
#     db(db.pokemonTable).delete()
#     db(db.ratings).delete()
#     db(db.derived_ratings).delete()
#     with open('apps/_default/static/FullDex.json') as f:
#         data = json.load(f)
#     i = 0
#     while (i < len(data)):
#         refPok = db.pokemonTable.insert(
#             name = data[i]['name'],
#             fullName = data[i]['fullname'],
#             form = data[i]['form'],
#             significantForm = data[i]['significantForm'],
#             species = data[i]['species'],
#             generation = data[i]['generation'],
#             number = data[i]['number'],
#             pokID = data[i]['pokID'],
#             bst = data[i]['bst'],
#             dbLink = data[i]['dblink'],
#             types = data[i]['types'],
#             formList = data[i]['formList'],
#             category = data[i]['category'],
#         )
#         i += 1
#     end = time.perf_counter()
#     return str(end - start)

# @action("update")
# @action.uses(db)
# def update():
#     start = time.perf_counter()
#     with open('apps/_default/static/newPokemon.json') as f:
#         data = json.load(f)
#     i = 0
#     while (i < len(data)):
#         refPok = db.pokemonTable.update_or_insert(
#             db.pokemonTable.pokID == data[i]['pokID'],
#             name = data[i]['name'],
#             fullName = data[i]['fullname'],
#             form = data[i]['form'],
#             significantForm = data[i]['significantForm'],
#             species = data[i]['species'],
#             generation = data[i]['generation'],
#             number = data[i]['number'],
#             pokID = data[i]['pokID'],
#             bst = data[i]['bst'],
#             dbLink = data[i]['dblink'],
#             types = data[i]['types'],
#             formList = data[i]['formList'],
#             category = data[i]['category'],
#         )
#         i += 1
#     end = time.perf_counter()
#     return str(end - start)

# Get rating returns the rating data of an individual pokemon
@action("get_rating")
@action.uses(session, url_signer_long.verify(), db, auth)
def get_rating():
    pokID = request.params.get('id')
    
    # Get the users ratings about this pokemon
    userFavorite = False
    userRating = 0
    userRatingRows = db((db.ratings.pokemon == pokID) & (db.ratings.rater == get_user_email())).select()
    for row in userRatingRows:
        if (row.rating == 6):
            userFavorite = True
        else:
            userRating = row.rating

    # Get the general ratings about this pokemon
    ratings = [0,0,0,0,0,0]
    ratingRow = db(db.derived_ratings.pokemon == pokID).select().first()
    ratings[0] = ratingRow.onestar
    ratings[1] = ratingRow.twostar
    ratings[2] = ratingRow.threestar
    ratings[3] = ratingRow.fourstar
    ratings[4] = ratingRow.fivestar
    ratings[5] = ratingRow.favorites

    return dict(
        oneRates = ratings[0],
        twoRates = ratings[1],
        threeRates = ratings[2],
        fourRates = ratings[3],
        fiveRates = ratings[4],
        sixRates = ratings[5],
        userRate = userRating,
        userFavorite = userFavorite,
        __version__ = __version__
    )

# Set rating Post funciotn
@action("set_rating", method='POST')
@action.uses(session, url_signer_long.verify(), db, auth.flash, auth.enforce())
def set_rating():
    id = request.params.get('id')
    rating = request.params.get('rating')

    # assert post is valid
    assert id is not None and rating is not None

    # If it's a regular rating we can just update/insert
    if (rating != 6): 
        db.ratings.update_or_insert(
            ((db.ratings.pokemon == id) & (db.ratings.rater == get_user_email()) & (db.ratings.rating != 6)),
            pokemon = id,
            rater = get_user_email(),
            rating=rating,
        )
        return "Rating Received!"
    
    # If it's a favorite, we need to check if user has reached their favorites max.
    elif (rating == 6):
        #stuff
        mySet = db((db.ratings.rating == 6) & (db.ratings.rater == get_user_email()))
        thisRate = db((db.ratings.rating == 6) & (db.ratings.rater == get_user_email()) & (db.ratings.pokemon == id))
        if (thisRate.count() == 0):
            if (mySet.count() < 10):
                db.ratings.insert(
                    pokemon = id,
                    rater = get_user_email(),
                    rating = 6,
                )
                return "Favorite Received!"
            else:
                return "10 favorites already!"
        # If it's a second favorite on the same pokemon, we remove that favorite.
        else:
            thisRate.delete()
            return "Favorite removed!"
            
    return "ok"

@action("remove_rating", method="POST")
@action.uses(session, url_signer_long.verify(), db, auth.flash, auth.enforce())
def remove_rating():
    id = request.params.get('id')

    # assert post is valid
    assert id is not None

    db((db.ratings.rater == get_user_email()) & (db.ratings.pokemon == id)).delete()
    return "Rating removed!"

@action("get_puzzle_play")
@action.uses(session, url_signer_long.verify(), db, auth.flash)
def get_puzzle_play():
    sql = "SELECT date, success, guesses, guessCount FROM puzzle_plays WHERE user='" + str(get_user_email()) + "' ORDER BY date DESC"
    userPlays = db.executesql(sql)
    return dict(
        userPlays = userPlays,
    )

@action("post_puzzle_play", method="POST")
@action.uses(session, url_signer_long.verify(), db, auth.flash)
def post_puzzle_play():
    date = mydatetime = (datetime.now() - timedelta(hours=5))
    date = mydatetime.date()
    user = get_user_email()
    if (user == None):
        user = "Unknown"
    guesses = request.params.get('guesses')

    # Select the puzzle pokemon of the day
    data = json.loads(db(db.pokemonTable).select().as_json())
    seed = dateSeed() * 2
    seed = BlumBlumShub(seed)
    seed = BlumBlumShub(seed)
    targetPoke = data[(int(seed) % len(data))]

    # If selected puzzle pokemon is invalid, select again until one is valid
    while (targetPoke['form'] != "Basic"):
        seed = BlumBlumShub(seed)
        targetPoke = data[(int(seed) % len(data))]

    guessList = guesses.split("---")
    success = False
    if (guessList[-1] == targetPoke['name']):
        success = True

    db.puzzle_plays.update_or_insert(
        ((db.puzzle_plays.date == date) & (db.puzzle_plays.user == user) & (db.puzzle_plays.guesses == guesses)),
        date = date,
        user = user,
        guesses = guesses,
        guessCount = len(guessList),
        success = success
    )

# Returns rating data for every pokemon
@action("get_all_ratings")
@action.uses(session, url_signer_long.verify(), db, auth)
def get_all_ratings():
    # All general ratings
    allRatings = db().select(db.derived_ratings.ALL, orderby=db.derived_ratings.pokemon)

    # All user ratings
    userRatings = db((db.ratings.rater) == get_user_email()).select(db.ratings.pokemon, db.ratings.rating, orderby=db.ratings.pokemon)

    return dict(
        allRatings = allRatings,
        userRatings = userRatings,
        __version__ = __version__
    )

@action("request_delete")
@action.uses('home.html', session, myMailer, auth.flash, url_signer_short, url_signer_long.verify(), db, auth.enforce())
def request_delete():
    #print("USE THIS LINK TO DELETE YOUR DATA")
    myMailer.active()
    userip = request.environ.get(USER_IP_KEY_AWS)
    if (userip == None):
        userip = request.environ.get(USER_IP_KEY_DOCKER)
    if (myMailer.canEmail(get_user_email(), userip)):
        myLink = URL("delete_confirm", signer=url_signer_short)
        myMailer.sendDeleteEmail(get_user_email(), myLink, userip)
        #print(myLink)
        auth.flash.set("Check your email for link to delete")
    else:
        auth.flash.set("Too many emails sent recently!")
    return indexDict(db, url_signer_long)

@action("delete_confirm")
@action.uses('home.html', session, auth.flash, url_signer_short, url_signer_short.verify(), db, auth.enforce())
def delete_confirm():
    #print("Deleting all data of " + get_user_email())
    userRatings = db((db.ratings.rater) == get_user_email())
    userRatings.delete()
    userPuzzle = db((db.puzzle_plays.user) == get_user_email())
    userPuzzle.delete()
    auth.flash.set("Your Info has been deleted")
    myMailer.codeUsed(get_user_email())
    userip = request.environ.get(USER_IP_KEY_AWS)
    if (userip == None):
        userip = request.environ.get(USER_IP_KEY_DOCKER)
    myMailer.codeUsedIP(userip)
    return indexDict(db, url_signer_long)


# Date seed function that converts every date to a unique integer seed
def dateSeed():
    today = datetime.now() - timedelta(hours=5)
    uniqueYear = (today.year * 32 % 10000)
    return uniqueYear + (today.month * 100) + today.day

# BlumBlumShub Pseudorandom algorithm
def BlumBlumShub(seed):
    return math.pow(seed, 2) % 50515093

def indexDict(db, url_signer):
    data = json.loads(db(db.pokemonTable).select().as_json())

    # Select 4 random pokemon
    i = 0
    randomPokes = []
    highlightPoke = None
    pokIDs = ""
    while (i < 4):
        randomInd = random.randint(0, len(data) - 1)
        randomPoke = data[randomInd]
        if (randomPoke['significantForm']):
            randomPokes.append(randomPoke)
            pokIDs += "" + str(randomPoke['id']) + "," 
            i += 1

    # Select the highlight pokemon of the day
    seed = dateSeed()
    seed = BlumBlumShub(seed)
    seed = BlumBlumShub(seed)
    highlightPoke = data[(int(seed) % len(data))]
    while (not highlightPoke['significantForm']):
        seed = BlumBlumShub(seed)
        highlightPoke = data[(int(seed) % len(data))]
    pokIDs += "" + str(highlightPoke['id']) + ""

    mydatetime = (datetime.now() - timedelta(hours=5))
    date = mydatetime.date()
    dailyPlayers = db((db.puzzle_plays.date == date)).count()


    # Query the database to receive the ratings of the 5 pokemon to display on the page
    sqlA = "SELECT * FROM derived_ratings WHERE pokemon IN ("  + pokIDs + ")"
    sqlB = "SELECT pokemon, rating FROM ratings WHERE pokemon IN (" + pokIDs + ") AND rater='" + str(get_user_email()) + "'"
    pokeRatings = db.executesql(sqlA)
    userRatings = db.executesql(sqlB)

    # Return that info to the user
    return dict(
        randomJSON = json.dumps(randomPokes),
        highlightJSON = json.dumps(highlightPoke),
        pokeRatings = json.dumps(pokeRatings),
        userRatings = json.dumps(userRatings),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer),
        req_delete_url = URL('request_delete', signer=url_signer),
        pokedex_url = URL('pokedex'),
        daily_plays = dailyPlayers,
        __version__ = __version__
    )