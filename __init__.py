# check compatibility
import py4web

assert py4web.check_compatible("0.1.20190709.1")

# by importing db you expose it to the _dashboard/dbadmin
from .models import db, spam_db

# by importing controllers you expose the actions defined in it
from . import controllers

# optional parameters
__version__ = "0.9.1"
__author__ = "Colin O'Rourke <Colin.orourke@icloud.com>"
__license__ = "anything you want"
