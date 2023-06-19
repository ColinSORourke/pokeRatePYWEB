"""
This file defines the database models
"""

import datetime
from .common import db, Field
from pydal.validators import *
from .common import auth

def get_user_email():
    if (auth):
        return auth.current_user.get('email').lower() if auth.current_user else None
    else:
        return None

def get_time():
    return datetime.datetime.utcnow()

def calcInsert(row, id):
    fields = ["onestar", "twostar", "threestar", "fourstar", "fivestar", "favorites"]
    set = db( (db.derived_ratings.pokemon == row.pokemon) )
    increment = 1
    if (row.rating == 6):
        increment = 0
    myupdate = {
        fields[row.rating - 1]: set.select()[0][fields[row.rating - 1]] + 1,
        "ratingcount": set.select()[0].ratingcount + increment
        }
    set.update(**myupdate)


def calcUpdate(set, rowTo):
    fields = ["onestar", "twostar", "threestar", "fourstar", "fivestar", "favorites"]
    rowFrom = set.select()[0]
    derived_set = db( (db.derived_ratings.pokemon == rowFrom.pokemon) )
    myupdate = {
        fields[rowFrom.rating - 1]: derived_set.select()[0][fields[rowFrom.rating - 1]] - 1,
        fields[rowTo.rating - 1]: derived_set.select()[0][fields[rowTo.rating - 1]] + 1
    }
    derived_set.update(**myupdate)

def calcDelete(set):
    fields = ["onestar", "twostar", "threestar", "fourstar", "fivestar", "favorites"]
    for row in set.select():
        derived_set = db( (db.derived_ratings.pokemon == row.pokemon) )
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

db.define_table('pokemonTable',
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
                )

db.define_table('ratings',
                Field("pokemon"),
                Field("rating", 'integer', default=0),
                Field("rater")
                )

db.define_table('derived_ratings',
                Field("pokemon"),
                Field("onestar", "integer", default=0),
                Field("twostar", "integer", default=0),
                Field("threestar", "integer", default=0),
                Field("fourstar", "integer", default=0),
                Field("fivestar", "integer", default=0),
                Field("favorites", "integer", default=0),
                Field("ratingcount", "integer", default=0)
                )

class myVirtualFields:
    def averageRating(self):
        sumRatings = (self.derived_ratings.onestar * 1) + (self.derived_rating.twostar * 2) + (self.derived_ratings.threestar * 3) + (self.derived_ratings.fourstar * 4) + (self.derived_ratings.fivestar * 5)
        return sumRatings / self.derived_ratings.ratingcount

db.derived_ratings.virtualfields.append(myVirtualFields())

db.commit()

