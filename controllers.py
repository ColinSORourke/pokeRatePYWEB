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
import datetime
import time

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, logger, flash

from .common import auth, url_signer
from .models import get_user_email

# Main Home Page
@action('home')
@action('index')
@action.uses('home.html', session, auth.flash, url_signer, db, auth)
def index():
    # Load the static data of every pokemon 
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
        pokedex_url = URL('pokedex')
    )

# Page that displays all the pokemon.
@action("pokedex")
@action.uses("pokedex.html", session, auth.flash, url_signer, db, auth, T)
def pokedex():
    # Load the static data of every pokemon 
    data = json.loads(db(db.pokemonTable).select().as_json())

    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer),
        req_delete_url = URL('request_delete', signer=url_signer),
        target_poke = "000000"
    )

# Page that displays all the pokemon.
# Having a number acutomatically launches the modal of a certain pokemon
@action("pokedex/<number>")
@action.uses("pokedex.html", session, auth.flash, url_signer, db, auth, T)
def pokedex(number):
    # Load the static data of every pokemon 
    data = json.loads(db(db.pokemonTable).select().as_json())

    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer),
        req_delete_url = URL('request_delete', signer=url_signer),
        target_poke = number
    )

# Page that displays the ranking data of all the pokemon.
@action("rankings")
@action.uses('data.html', session, auth.flash, url_signer, db, auth, T)
def data():
    # Load the static data of every pokemon 
    data = json.loads(db(db.pokemonTable).select().as_json())

    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer),
        req_delete_url = URL('request_delete', signer=url_signer),
        pokedex_url = URL('pokedex')
    )

# Page that plays a daily puzzle
@action("puzzle")
@action.uses('puzzle.html', session, auth.flash, url_signer, db, auth, T)
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
        get_rating_url = URL('get_rating', signer=url_signer),
        pokedex_url = URL('pokedex'),
        req_delete_url = URL('request_delete', signer=url_signer),
    )

#----------------------------------------#
# SETUP URL IS PURELY FOR DATABASE ADMINISTRATION PURPOSES
# THIS URL SHOULD NEVER BE LIVE IN THE PRODUCTION CONTAINER
# ONLY LIVE ON AN ADMINISTRATORS LOCAL MACHINE
#----------------------------------------#

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


# Get rating returns the rating data of an individual pokemon
@action("get_rating")
@action.uses(session, url_signer.verify(), db, auth)
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
        userFavorite = userFavorite
    )

# Set rating Post funciotn
@action("set_rating", method='POST')
@action.uses(session, url_signer.verify(), db, auth.flash, auth.enforce())
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

# Returns rating data for every pokemon
@action("get_all_ratings")
@action.uses(session, url_signer.verify(), db, auth)
def get_all_ratings():
    # All general ratings
    allRatings = db().select(db.derived_ratings.ALL, orderby=db.derived_ratings.pokemon)

    # All user ratings
    userRatings = db((db.ratings.rater) == get_user_email()).select(db.ratings.pokemon, db.ratings.rating, orderby=db.ratings.pokemon)

    return dict(
        allRatings = allRatings,
        userRatings = userRatings
    )

@action("request_delete")
@action.uses('home.html', session, auth.flash, url_signer, url_signer.verify(), db, auth.enforce())
def request_delete():
    print("USE THIS LINK TO DELETE YOUR DATA")
    print(URL("delete_confirm", signer=url_signer))
    auth.flash.set("Check your email for link to delete")
    data = json.loads(db(db.pokemonTable).select().as_json())
    i = 0
    randomPokes = []
    highlightPoke = None
    pokIDs = ""
    while (i < 4):
        randomInd = random.randint(0, len(data) - 1)
        randomPoke = data[randomInd]
        if (randomPoke['significantForm']):
            randomPokes.append(randomPoke)
            pokIDs += "'" + randomPoke['pokID'] + "'," 
            i += 1

    highlightPoke = data[181]
    pokIDs += "'" + highlightPoke['pokID'] + "'"

    sqlA = "SELECT * FROM derived_ratings WHERE pokemon IN ("  + pokIDs + ")"
    sqlB = "SELECT pokemon, rating FROM ratings WHERE pokemon IN (" + pokIDs + ") AND rater='" + str(get_user_email()) + "'"

    pokeRatings = db.executesql(sqlA)
    userRatings = db.executesql(sqlB)

    return dict(
        randomJSON = json.dumps(randomPokes),
        highlightJSON = json.dumps(highlightPoke),
        pokeRatings = json.dumps(pokeRatings),
        userRatings = json.dumps(userRatings),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer),
        req_delete_url = URL('request_delete', signer=url_signer),
        pokedex_url = URL('pokedex')
    )

@action("delete_confirm")
@action.uses('home.html', session, auth.flash, url_signer, url_signer.verify(), db, auth.enforce())
def delete_confirm():
    print("Deleting all data of " + get_user_email())
    userRatings = db((db.ratings.rater) == get_user_email())
    userRatings.delete()
    auth.flash.set("Your Info has been deleted")
    data = json.loads(db(db.pokemonTable).select().as_json())
    i = 0
    randomPokes = []
    highlightPoke = None
    pokIDs = ""
    while (i < 4):
        randomInd = random.randint(0, len(data) - 1)
        randomPoke = data[randomInd]
        if (randomPoke['significantForm']):
            randomPokes.append(randomPoke)
            pokIDs += "'" + randomPoke['pokID'] + "'," 
            i += 1

    highlightPoke = data[181]
    pokIDs += "'" + highlightPoke['pokID'] + "'"

    sqlA = "SELECT * FROM derived_ratings WHERE pokemon IN ("  + pokIDs + ")"
    sqlB = "SELECT pokemon, rating FROM ratings WHERE pokemon IN (" + pokIDs + ") AND rater='" + str(get_user_email()) + "'"

    pokeRatings = db.executesql(sqlA)
    userRatings = db.executesql(sqlB)

    return dict(
        randomJSON = json.dumps(randomPokes),
        highlightJSON = json.dumps(highlightPoke),
        pokeRatings = json.dumps(pokeRatings),
        userRatings = json.dumps(userRatings),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer),
        req_delete_url = URL('request_delete', signer=url_signer),
        pokedex_url = URL('pokedex')
    )


# Date seed function that converts every date to a unique integer seed
def dateSeed():
    today = datetime.datetime.now()
    uniqueYear = (today.year * 32 % 10000)
    return uniqueYear + (today.month * 100) + today.day

# BlumBlumShub Pseudorandom algorithm
def BlumBlumShub(seed):
    return math.pow(seed, 2) % 50515093