"""
This file defines the database models
"""

import uuid
from .common import local_db, remote_db, read_db, Field
from pydal.validators import *
from .common import auth

def get_user_email():
    if (auth):
        return auth.current_user.get('email').lower() if auth.current_user else None
    else:
        return None

def calcInsert(row, id):
    fields = ["onestar", "twostar", "threestar", "fourstar", "fivestar", "favorites"]
    set = remote_db( (remote_db.derived_ratings.pokemon == row.pokemon) )
    increment = 1
    if (row.rating == 6):
        increment = 0
    myupdate = {
        fields[row.rating - 1]: set.select()[0][fields[row.rating - 1]] + 1,
        "ratingcount": set.select()[0].ratingcount + increment
        }
    set.update(**myupdate)

def addDerivedPokemon(row, id):
    remote_db.derived_ratings.insert(
        pokemon = id
    )

def calcUpdate(set, rowTo):
    rowFrom = set.select()[0]
    oneRates = remote_db( (remote_db.ratings.pokemon == rowFrom.pokemon) & (remote_db.ratings.rating == 1) ).count()
    twoRates = remote_db( (remote_db.ratings.pokemon == rowFrom.pokemon) & (remote_db.ratings.rating == 2) ).count()
    threeRates = remote_db( (remote_db.ratings.pokemon == rowFrom.pokemon) & (remote_db.ratings.rating == 3) ).count()
    fourRates = remote_db( (remote_db.ratings.pokemon == rowFrom.pokemon) & (remote_db.ratings.rating == 4) ).count()
    fiveRates = remote_db( (remote_db.ratings.pokemon == rowFrom.pokemon) & (remote_db.ratings.rating == 5) ).count()
    derived_set = remote_db( (remote_db.derived_ratings.pokemon == rowFrom.pokemon) )
    myupdate = {
        "onestar": oneRates,
        "twostar": twoRates,
        "threestar": threeRates,
        "fourstar": fourRates,
        "fivestar": fiveRates
    }
    derived_set.update(**myupdate)

def calcDelete(set):
    fields = ["onestar", "twostar", "threestar", "fourstar", "fivestar", "favorites"]
    for row in set.select():
        derived_set = remote_db( (remote_db.derived_ratings.pokemon == row.pokemon) )
        increment = 1
        if (row.rating == 6):
            increment = 0
        myupdate = {
            fields[row.rating - 1]: derived_set.select()[0][fields[row.rating - 1]] - 1,
            "ratingcount": derived_set.select()[0].ratingcount - increment
        }
        derived_set.update(**myupdate)

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

def definePokemon(mydb):
    mydb.define_table('pokemonTable',
                Field("name"),
                Field("fullName"),
                Field("form"),
                Field("significantForm", "boolean"),
                Field("species"),
                Field("generation"),
                Field("number"),
                Field("pokID"),
                Field("bst", "integer"),
                Field("dbLink"),
                Field("types", "list:string"),
                Field("formList", "list:string"),
                Field("category"),
                Field("uuid"),
                )
    mydb.pokemonTable.uuid.default = lambda:str(uuid.uuid4()) 

    mydb.define_table('ratings',
                Field("pokemon", "reference pokemonTable"),
                Field("rating", 'integer', default=0),
                Field("rater"),
                Field("uuid"),
                )
    mydb.ratings.uuid.default = lambda:str(uuid.uuid4())    

    mydb.define_table('derived_ratings',
                Field("pokemon", "reference pokemonTable"),
                Field("onestar", "integer", default=0),
                Field("twostar", "integer", default=0),
                Field("threestar", "integer", default=0),
                Field("fourstar", "integer", default=0),
                Field("fivestar", "integer", default=0),
                Field("favorites", "integer", default=0),
                Field("ratingcount", "integer", default=0),
                Field("uuid"),
                )
    mydb.derived_ratings.uuid.default = lambda:str(uuid.uuid4())

    mydb.define_table('puzzle_plays',
                Field('date'),
                Field('user'),
                Field('success', "boolean"),
                Field('guesses'),
                Field('guessCount', "integer"),
                Field("uuid"),
                )
    mydb.puzzle_plays.uuid.default = lambda:str(uuid.uuid4())

def defineSpam(mydb):
    mydb.define_table("emails",
                     Field("email"),
                     Field("codessent", "integer", default=0),
                     Field("lastcodesent", "integer"),
                     Field("codesused", "integer", default=0),
                     Field("lastcodeused", "integer"),
                     Field("codeswithoutresponse", "integer",  default=0)
                     )

    mydb.define_table("ips",
                     Field("ip"),
                     Field("codessent", "integer", default=0),
                     Field("lastcodesent", "integer"),
                     Field("codesused", "integer", default=0),
                     Field("lastcodeused", "integer"),
                     Field("codeswithoutresponse", "integer",  default=0)
                     )

    mydb.define_table("daily",
                     Field("day"),
                     Field("codessent", "integer", default=0)
                     )

definePokemon(read_db)
definePokemon(remote_db)
defineSpam(local_db)

class myVirtualFields:
    def averageRating(self):
        sumRatings = (self.derived_ratings.onestar * 1) + (self.derived_rating.twostar * 2) + (self.derived_ratings.threestar * 3) + (self.derived_ratings.fourstar * 4) + (self.derived_ratings.fivestar * 5)
        return sumRatings / self.derived_ratings.ratingcount

read_db.derived_ratings.virtualfields.append(myVirtualFields())

remote_db.pokemonTable._after_insert.append(addDerivedPokemon)
remote_db.ratings._after_insert.append(calcInsert)
remote_db.ratings._after_update.append(calcUpdate)
remote_db.ratings._before_delete.append(calcDelete)

local_db.commit()
read_db.commit()
remote_db.commit()
