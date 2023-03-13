"""
This file defines the database models
"""

import datetime
from .common import db, Field
from pydal.validators import *
from .common import auth

def get_user_email():
    return auth.current_user.get('email').lower() if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

db.define_table('ratings',
                Field("pokemon"),
                Field("rating", 'integer', default=0),
                Field("rater", default=get_user_email)
                )

db.commit()