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
@action.uses(local_db)              indicates that the action uses the local_db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, local_db, T, auth, and templates are examples of Fixtures.
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

from py4web import Cache, action, request, abort, redirect, URL
from yatl.helpers import A
from .common import local_db, remote_db, read_db, myMailer, session, T, cache, logger, flash

from .common import auth, url_signer_short, url_signer_long
from .models import get_user_email
from .__init__ import __version__

#REMOTE_ADDR when running local container
#HTTP_X_FORWARDED_FOR when running on ECS
cache = Cache(size=5)
USER_IP_KEY_AWS = "HTTP_X_FORWARDED_FOR"
USER_IP_KEY_DOCKER = "REMOTE_ADDR"
POKEDATA = json.loads(read_db(read_db.pokemonTable).select(cacheable=True).as_json())

# Main Home Page
@action('home')
@action('index')
@action.uses('home.html', session, auth.flash, url_signer_long, read_db, auth)
def index():
    # Load the static data of every pokemon 
    return indexDict(read_db, url_signer_long)

# Main Home Page
@action('statichome')
@action.uses('home.html', session, auth.flash, url_signer_long, read_db, auth)
def index():
    # Load the static data of every pokemon 

    return indexDictStatic(read_db, url_signer_long)

# Page that displays all the pokemon.
@action("pokedex")
@action.uses("pokedex.html", session, auth.flash, url_signer_long, read_db, auth, T)
def pokedex():
    allRatings = json.loads(read_db().select(read_db.derived_ratings.ALL, orderby=read_db.derived_ratings.pokemon, cacheable=True).as_json())
    userRatings = json.loads(read_db((read_db.ratings.rater) == get_user_email()).select(read_db.ratings.pokemon, read_db.ratings.rating, orderby=read_db.ratings.pokemon, cacheable=True).as_json())

    return dict(
        dexJSON = json.dumps(POKEDATA),
        allRatings = allRatings,
        userRatings = userRatings,
        get_rating_url = URL('get_rating', signer=url_signer_long),
        set_rating_url = URL('set_rating', signer=url_signer_long),
        remove_rating_url = URL('remove_rating', signer=url_signer_long),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer_long),
        req_delete_url = URL('request_delete', signer=url_signer_long),
        target_poke = "000000",
        __version__ = __version__
    )

@action("userdex")
@action.uses("userdex.html", session, auth.flash, url_signer_long, read_db, auth, T)
def pokedex():
    # Load the static data of every pokemon 
    # data = json.loads(read_db(read_db.pokemonTable).select().as_json())

    allRatings = json.loads(read_db().select(read_db.derived_ratings.ALL, orderby=read_db.derived_ratings.pokemon, cacheable=True).as_json())
    userRatings = json.loads(read_db((read_db.ratings.rater) == get_user_email()).select(read_db.ratings.pokemon, read_db.ratings.rating, orderby=read_db.ratings.pokemon, cacheable=True).as_json())

    return dict(
        dexJSON = json.dumps(POKEDATA),
        allRatings = allRatings,
        userRatings = userRatings,
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
@action.uses("pokedex.html", session, auth.flash, url_signer_long, read_db, auth, T)
def pokedex(number):
    allRatings = json.loads(read_db().select(read_db.derived_ratings.ALL, orderby=read_db.derived_ratings.pokemon, cacheable=True).as_json())
    userRatings = json.loads(read_db((read_db.ratings.rater) == get_user_email()).select(read_db.ratings.pokemon, read_db.ratings.rating, orderby=read_db.ratings.pokemon, cacheable=True).as_json())

    return dict(
        dexJSON = json.dumps(POKEDATA),
        allRatings = allRatings,
        userRatings = userRatings,
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
@action.uses('data.html', session, auth.flash, url_signer_long, read_db, auth, T)
def data():
    return dict(
        dexJSON = json.dumps(POKEDATA),
        get_rating_url = URL('get_rating', signer=url_signer_long),
        set_rating_url = URL('set_rating', signer=url_signer_long),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer_long),
        req_delete_url = URL('request_delete', signer=url_signer_long),
        pokedex_url = URL('pokedex'),
        __version__ = __version__
    )

# Page that plays a daily puzzle
@action("puzzle")
@action.uses('puzzle.html', session, auth.flash, url_signer_long, read_db, auth, T)
def puzzle():
    # Select the puzzle pokemon of the day
    seed = dateSeed() * 2
    seed = BlumBlumShub(seed)
    seed = BlumBlumShub(seed)
    targetPoke = POKEDATA[(int(seed) % len(POKEDATA))]

    # If selected puzzle pokemon is invalid, select again until one is valid
    while (targetPoke['form'] != "Basic"):
        seed = BlumBlumShub(seed)
        targetPoke = POKEDATA[(int(seed) % len(POKEDATA))]

    return dict(
        dexJSON = json.dumps(POKEDATA),
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
# @action.uses(remote_db)
# def puzzletest():
#     remote_db.puzzle_plays.insert(
#         date = "nonsense",
#         user = "nonsense",
#         guesses = "nonsense",
#         guessCount = "6",
#         success = False
#     )

# @action("setup")
# @action.uses(remote_db)
# def setup():
#     start = time.perf_counter()
#     remote_db(remote_db.pokemonTable).delete()
#     remote_db(remote_db.ratings).delete()
#     remote_db(remote_db.derived_ratings).delete()
#     with open('apps/_default/static/FullDex.json') as f:
#         data = json.load(f)
#     i = 0
#     while (i < len(data)):
#         refPok = remote_db.pokemonTable.insert(
#             name = data[i]['name'],
#             fullName = data[i]['fullname'],
#             form = data[i]['form'],
#             significantForm = data[i]['significantForm'],
#             species = data[i]['species'],
#             generation = data[i]['generation'],
#             number = data[i]['number'],
#             pokID = data[i]['pokID'],
#             bst = data[i]['bst'],
#             remote_dbLink = data[i]['remote_dblink'],
#             types = data[i]['types'],
#             formList = data[i]['formList'],
#             category = data[i]['category'],
#         )
#         i += 1
#     end = time.perf_counter()
#     return str(end - start)

# @action("update")
# @action.uses(remote_db)
# def update():
#     start = time.perf_counter()
#     with open('apps/_default/static/NewPokemon.json') as f:
#         data = json.load(f)
#     i = 0
#     while (i < len(data)):
#         refPok = remote_db.pokemonTable.update_or_insert(
#             remote_db.pokemonTable.pokID == data[i]['pokID'],
#             name = data[i]['name'],
#             fullName = data[i]['fullname'],
#             form = data[i]['form'],
#             significantForm = data[i]['significantForm'],
#             species = data[i]['species'],
#             generation = data[i]['generation'],
#             number = data[i]['number'],
#             pokID = data[i]['pokID'],
#             bst = data[i]['bst'],
#             remote_dbLink = data[i]['remote_dblink'],
#             types = data[i]['types'],
#             formList = data[i]['formList'],
#             category = data[i]['category'],
#         )
#         i += 1
#     end = time.perf_counter()
#     return str(end - start)

# Get rating returns the rating data of an individual pokemon
@action("get_rating")
@action.uses(session, url_signer_long.verify(), read_db, auth)
def get_rating():
    pokID = request.params.get('id')
    
    # Get the users ratings about this pokemon
    userFavorite = False
    userRating = 0
    userRatingRows = read_db((read_db.ratings.pokemon == pokID) & (read_db.ratings.rater == get_user_email())).select(cacheable=True)
    for row in userRatingRows:
        if (row.rating == 6):
            userFavorite = True
        else:
            userRating = row.rating

    # Get the general ratings about this pokemon
    ratings = [0,0,0,0,0,0]
    ratingRow = read_db(read_db.derived_ratings.pokemon == pokID).select(cacheable=True).first()
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
@action.uses(session, url_signer_long.verify(), remote_db, auth.flash, auth.enforce())
def set_rating():
    id = request.params.get('id')
    rating = request.params.get('rating')

    # assert post is valid
    assert id is not None and rating is not None

    # If it's a regular rating we can just update/insert
    if (rating != 6): 
        remote_db.ratings.update_or_insert(
            ((remote_db.ratings.pokemon == id) & (remote_db.ratings.rater == get_user_email()) & (remote_db.ratings.rating != 6)),
            pokemon = id,
            rater = get_user_email(),
            rating=rating,
        )
        return "Rating Received!"
    
    # If it's a favorite, we need to check if user has reached their favorites max.
    elif (rating == 6):
        #stuff
        mySet = remote_db((remote_db.ratings.rating == 6) & (remote_db.ratings.rater == get_user_email()))
        thisRate = remote_db((remote_db.ratings.rating == 6) & (remote_db.ratings.rater == get_user_email()) & (remote_db.ratings.pokemon == id))
        if (thisRate.count() == 0):
            if (mySet.count() < 10):
                remote_db.ratings.insert(
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
@action.uses(session, url_signer_long.verify(), remote_db, auth.flash, auth.enforce())
def remove_rating():
    id = request.params.get('id')

    # assert post is valid
    assert id is not None

    remote_db((remote_db.ratings.rater == get_user_email()) & (remote_db.ratings.pokemon == id)).delete()
    return "Rating removed!"

@action("get_puzzle_play")
@action.uses(session, url_signer_long.verify(), read_db, auth.flash)
def get_puzzle_play():
    sql = "SELECT date, success, guesses, guessCount FROM puzzle_plays WHERE user='" + str(get_user_email()) + "' ORDER BY date DESC"
    userPlays = read_db.executesql(sql)
    return dict(
        userPlays = userPlays,
    )

@action("post_puzzle_play", method="POST")
@action.uses(session, url_signer_long.verify(), remote_db, auth.flash)
def post_puzzle_play():
    date = mydatetime = (datetime.now() - timedelta(hours=5))
    date = mydatetime.date()
    user = get_user_email()
    if (user == None):
        user = "Unknown"
    guesses = request.params.get('guesses')

    seed = dateSeed() * 2
    seed = BlumBlumShub(seed)
    seed = BlumBlumShub(seed)
    targetPoke = POKEDATA[(int(seed) % len(POKEDATA))]

    # If selected puzzle pokemon is invalid, select again until one is valid
    while (targetPoke['form'] != "Basic"):
        seed = BlumBlumShub(seed)
        targetPoke = POKEDATA[(int(seed) % len(POKEDATA))]

    guessList = guesses.split("---")
    success = False
    if (guessList[-1] == targetPoke['name']):
        success = True

    remote_db.puzzle_plays.update_or_insert(
        ((remote_db.puzzle_plays.date == date) & (remote_db.puzzle_plays.user == user) & (remote_db.puzzle_plays.guesses == guesses)),
        date = date,
        user = user,
        guesses = guesses,
        guessCount = len(guessList),
        success = success
    )
    

# Returns rating data for every pokemon
@action("get_all_ratings")
@action.uses(session, url_signer_long.verify(), read_db, auth)
def get_all_ratings():
    # All general ratings
    allRatings = read_db().select(read_db.derived_ratings.ALL, orderby=read_db.derived_ratings.pokemon, cacheable=True)

    # All user ratings
    userRatings = read_db((read_db.ratings.rater) == get_user_email()).select(read_db.ratings.pokemon, read_db.ratings.rating, orderby=read_db.ratings.pokemon, cacheable=True)

    return dict(
        allRatings = allRatings,
        userRatings = userRatings,
        __version__ = __version__
    )

@action("request_delete")
@action.uses('home.html', session, myMailer, auth.flash, url_signer_short, url_signer_long.verify(), read_db, auth.enforce())
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
    return indexDict(read_db, url_signer_long)

@action("delete_confirm")
@action.uses('home.html', session, auth.flash, url_signer_short, url_signer_short.verify(), remote_db, auth.enforce())
def delete_confirm():
    #print("Deleting all data of " + get_user_email())
    userRatings = remote_db((remote_db.ratings.rater) == get_user_email())
    userRatings.delete()
    userPuzzle = remote_db((remote_db.puzzle_plays.user) == get_user_email())
    userPuzzle.delete()
    auth.flash.set("Your Info has been deleted")
    myMailer.codeUsed(get_user_email())
    userip = request.environ.get(USER_IP_KEY_AWS)
    if (userip == None):
        userip = request.environ.get(USER_IP_KEY_DOCKER)
    myMailer.codeUsedIP(userip)
    return indexDict(read_db, url_signer_long)


# Date seed function that converts every date to a unique integer seed
def dateSeed():
    today = datetime.now() - timedelta(hours=5)
    uniqueYear = (today.year * 32 % 10000)
    return uniqueYear + (today.month * 100) + today.day

# BlumBlumShub Pseudorandom algorithm
def BlumBlumShub(seed):
    return math.pow(seed, 2) % 50515093

def randomPokemon(count = 4):
    i = 0
    randomPokes = []
    
    while (i < count):
        randomInd = random.randint(0, len(POKEDATA) - 1)
        randomPoke = POKEDATA[randomInd]
        if (randomPoke['significantForm']):
            randomPokes.append(randomPoke)
            i += 1
    return randomPokes

def highlightPokemon():
    seed = dateSeed()
    seed = BlumBlumShub(seed)
    seed = BlumBlumShub(seed)
    highlightPoke = POKEDATA[(int(seed) % len(POKEDATA))]
    while (not highlightPoke['significantForm']):
        seed = BlumBlumShub(seed)
        highlightPoke = POKEDATA[(int(seed) % len(POKEDATA))]
    return highlightPoke

def indexDict(read_db, url_signer):
    randomPokes = randomPokemon(4)
    highlightPoke = highlightPokemon()
    pokIDs = ""
    pokIDs += "" + str(randomPokes[0]['id']) + ","
    pokIDs += "" + str(randomPokes[1]['id']) + "," 
    pokIDs += "" + str(randomPokes[2]['id']) + "," 
    pokIDs += "" + str(randomPokes[3]['id']) + ","  
    pokIDs += "" + str(highlightPoke['id']) + ""

    mydatetime = (datetime.now() - timedelta(hours=5))
    date = mydatetime.date()
    dailyPlayers = read_db((read_db.puzzle_plays.date == date)).count()    
    sqlA = "SELECT * FROM derived_ratings WHERE pokemon IN ("  + pokIDs + ")"
    sqlB = "SELECT pokemon, rating FROM ratings WHERE pokemon IN (" + pokIDs + ") AND rater='" + str(get_user_email()) + "'"
    pokeRatings = read_db.executesql(sqlA)
    userRatings = read_db.executesql(sqlB)

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

@cache.memoize(expiration=28800)
def indexDictStatic(read_db, url_signer):
    return indexDict(read_db, url_signer)