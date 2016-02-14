# -*- coding: utf-8 -*-
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

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

import webapp2
import jinja2


from handler import *
from fbuser import *

#upload
def files_key(group = 'default'):
    return db.Key.from_path('files', group)

class File(db.Model):
    user = db.StringProperty(required = True)
    file_name = db.StringProperty(required = True)
    upload_key = blobstore.BlobReferenceProperty(required = True)

    @classmethod
    def add_file(cls, user,upload_key):
        return File(parent = files_key(),
                    user = user,
                    file_name = file_name,
                    upload_key = upload_key)