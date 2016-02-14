# -*- coding: utf-8 -*-
import os
import re
import random
import hashlib
import hmac
from string import letters
from time import strftime
import codecs 
from datetime import datetime, timedelta

import webapp2
import jinja2

import base64
import cgi
import Cookie
import email.utils
import logging
import os.path
import time
import urllib
import wsgiref.handlers

import json
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from fbuser import *
from upload import *


template_dir = os.path.join(os.path.dirname(__file__), 'Summer/template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

FACEBOOK_APP_ID = "1050747804947825"
FACEBOOK_APP_SECRET = "0e275da6d2372950228b8d43ec9e109a"

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    @property
    def fb_user(self):
        """Returns the logged in Facebook user, or None if unconnected."""
        if not hasattr(self, "_fb_user"):
            self._fb_user = None
            user_id = parse_cookie(self.request.cookies.get("fb_user"))
            if user_id:
                self._fb_user = FBUser.get_by_key_name(user_id)
        return self._fb_user

#FB Cookie
def set_cookie(response, fbname, value, domain=None, path="/", expires=None):
    """Generates and signs a cookie for the give name/value"""
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(value, timestamp)
    cookie = Cookie.BaseCookie()
    cookie[fbname] = "|".join([value, timestamp, signature])
    cookie[fbname]["path"] = path
    if domain:
        cookie[fbname]["domain"] = domain
    if expires:
        cookie[fbname]["expires"] = email.utils.formatdate(
            expires, localtime=False, usegmt=True)
    response.headers.add("Set-Cookie", cookie.output()[12:])

def parse_cookie(value):
    """Parses and verifies a cookie value from set_cookie"""
    if not value:
        return None
    parts = value.split("|")
    if len(parts) != 3:
        return None
    if cookie_signature(parts[0], parts[1]) != parts[2]:
        logging.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 30 * 86400:
        logging.warning("Expired cookie %r", value)
        return None
    try:
        return base64.b64decode(parts[0]).strip()
    except:
        return None


def cookie_signature(*parts):
    """Generates a cookie signature.

    We use the Facebook app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(FACEBOOK_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts:
        hash.update(part)
    return hash.hexdigest()

def valid_name(name):
    if name:
        return True

def valid_gender(gender):
    if(gender==u'男' or gender==u'女'):
        return True

def valid_birthdate(birthdate):
    if birthdate:
        return True

IDENTIFICATION_RE  = re.compile(r'^[A-Z]{1}[0-9]{8}$')
def valid_identification(identification):
    if identification and IDENTIFICATION_RE.match(identification):
        return True

def valid_school(school):
    if school:
        return True

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    if email and EMAIL_RE.match(email):
        return True

PHONE_RE  = re.compile(r'^\d[7,10]$')
def valid_phone(phone):
    if phone and PHONE_RE.match(phone):
        return True

def valid_address(address):
    if address:
        return True

def valid_meal(meal):
    if(meal==u'葷'or meal==u'素'or meal==u'其他'):
        return True

def valid_tshirt(tshirt):
    if(tshirt==u'L'or tshirt==u'M' or tshirt==u'S' or tshirt==u'XS'or tshirt==u'XL'):
        return True
    else:
        return False

def valid_emergency_contact(emergency_contact):
    if emergency_contact:
        return True

def valid_emergency_contact_phone(emergency_contact_phone):
    if emergency_contact_phone and PHONE_RE.match(emergency_contact_phone):
        return True
