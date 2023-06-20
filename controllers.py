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

coreSQL = "SELECT * FROM pokemonTable"

@action('home')
@action('index')
@action.uses('home.html', session, auth.flash, url_signer, db, auth)
def index():
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
            pokIDs += "" + str(randomPoke['id']) + "," 
            i += 1

    seed = dateSeed()
    seed = BlumBlumShub(seed)
    seed = BlumBlumShub(seed)
    highlightPoke = data[(int(seed) % len(data))]
    while (not highlightPoke['significantForm']):
        seed = BlumBlumShub(seed)
        highlightPoke = data[(int(seed) % len(data))]

    pokIDs += "" + str(highlightPoke['id']) + ""

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

@action("pokedex") # "Website/Pokerate/pokedex"
@action.uses("pokedex.html", session, auth.flash, url_signer, db, auth, T)
def pokedex():
    data = json.loads(db(db.pokemonTable).select().as_json())
    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer),
        req_delete_url = URL('request_delete', signer=url_signer),
        target_poke = "000000"
    )

@action("pokedex/<number>")
@action.uses("pokedex.html", session, auth.flash, url_signer, db, auth, T)
def pokedex(number):
    data = json.loads(db(db.pokemonTable).select().as_json())
    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer),
        req_delete_url = URL('request_delete', signer=url_signer),
        target_poke = number
    )


@action("data")
@action.uses('data.html', session, auth.flash, url_signer, db, auth, T)
def data():
    data = json.loads(db(db.pokemonTable).select().as_json())

    return dict(
        dexJSON = json.dumps(data),
        get_rating_url = URL('get_rating', signer=url_signer),
        set_rating_url = URL('set_rating', signer=url_signer),
        get_all_ratings_url = URL('get_all_ratings', signer=url_signer),
        req_delete_url = URL('request_delete', signer=url_signer),
        pokedex_url = URL('pokedex')
    )

@action("puzzle")
@action.uses('puzzle.html', session, auth.flash, url_signer, db, auth, T)
def data():
    data = json.loads(db(db.pokemonTable).select().as_json())

    seed = dateSeed() * 2
    seed = BlumBlumShub(seed)
    seed = BlumBlumShub(seed)

    targetPoke = data[(int(seed) % len(data))]
    # Have to use number
    # When I pass the whole DEXJSon in the MSG response, true is lowercase
    # But when I pass an individual PokemonJSON in the MSG response, true is uppercase
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
#     emails = ["colin.orourke@me.com", "collin.orourke@icloud.com", "colllin.orourke@icloud.com", "collllin.orourke@icloud.com", "colllllin.orourke@icloud.com"]
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
#         j = 0
#         while (j < 30):
#             ran = random.randint(1,5)
#             db.ratings.insert(
#                 pokemon = refPok,
#                rater = emails[j % 5],
#                rating = ran
#             )
#             j += 1
        
#         i += 1
#     end = time.perf_counter()
#     return str(end - start)

@action("get_rating")
@action.uses(session, url_signer.verify(), db, auth)
def get_rating():
    pokID = request.params.get('id')
    
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
    id = request.params.get('id')
    rating = request.params.get('rating')
    assert id is not None and rating is not None
    if (rating != 6): 
        db.ratings.update_or_insert(
            ((db.ratings.pokemon == id) & (db.ratings.rater == get_user_email()) & (db.ratings.rating != 6)),
            pokemon = id,
            rater = get_user_email(),
            rating=rating,
        )
        return "Rating Received!"
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
        else:
            thisRate.delete()
            return "Favorite removed!"
            
    return "ok"

@action("get_all_ratings")
@action.uses(session, url_signer.verify(), db, auth)
def get_all_ratings():
    allRatings = db().select(db.derived_ratings.ALL, orderby=db.derived_ratings.pokemon)
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

def dateSeed():
    today = datetime.datetime.now()
    uniqueYear = (today.year * 32 % 10000)
    return uniqueYear + (today.month * 100) + today.day


def BlumBlumShub(seed):
    return math.pow(seed, 2) % 50515093