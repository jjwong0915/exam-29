import os
import re
import random
import hashlib
import hmac
from string import letters
from time import strftime
import codecs 
from google.appengine.ext import db
from datetime import datetime, timedelta

import webapp2
import jinja2

from handler import *

class FBUser(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    fbname = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    stop = db.BooleanProperty(required=True)
    admin = db.BooleanProperty(required=True)
