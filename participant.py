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

import webapp2
import jinja2


from handler import *
from fbuser import *

#participant
def participants_key(group = 'default'):
    return db.Key.from_path('participants', group)

class Participant(db.Model):
    name = db.StringProperty(required = True)
    gender = db.StringProperty(required = True)
    birthdate = db.StringProperty(required = True)
    identification = db.StringProperty(required = True)
    school = db.StringProperty(required = True)
    email = db.StringProperty(required = True)    
    phone = db.StringProperty(required = True)
    address = db.StringProperty(required = True)
    meal = db.StringProperty(required = True)
    tshirt = db.StringProperty(required = True)
    emergency_contact = db.StringProperty(required = True)
    emergency_contact_phone = db.StringProperty(required = True)
    prefix = db.StringProperty()
    fb_id = db.StringProperty(required = True)
    fb_name = db.StringProperty(required = True)
    fb_url = db.StringProperty(required = True)
    check = db.BooleanProperty(required = True)
    check_prefix = db.StringProperty()
    show = db.BooleanProperty(required=True)
    post_created = db.DateTimeProperty(required=True)
    last_modified = db.DateTimeProperty(required=True , auto_now_add = True)

    def render(self):
        return render_str("console_participant_post.html", participant = self)

    def per_render(self):
        self.prefix  = self.prefix
        return render_str("console_participant_per_post.html", participant = self)

    @classmethod
    def add_participant(cls, name, gender, birthdate, identification, school, email, phone, address, meal,
        tshirt, emergency_contact, emergency_contact_phone, prefix, fb_id, fb_name, fb_url, check, check_prefix, show, post_created):
        return Participant(parent = participants_key(),
                    name = name,
                    gender = gender,
                    birthdate = birthdate,
                    identification = identification,
                    school = school,
                    email = email,
                    phone = phone,
                    address = address,
                    meal = meal,
                    tshirt = tshirt,
                    emergency_contact = emergency_contact,
                    emergency_contact_phone = emergency_contact_phone,
                    prefix = prefix,
                    fb_id = fb_id,
                    fb_name = fb_name,
                    fb_url = fb_url,
                    check = check,
                    check_prefix = check_prefix,
                    show = show,
                    post_created=post_created)

    
