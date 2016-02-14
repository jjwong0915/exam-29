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

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

from handler import *
from fbuser import *
from participant import *
from upload import *

class MainPage(Handler):
    def get(self):
        self.redirect('/index')

class Index(Handler):
    def get(self):
      self.render('home.html')

class FBLogin(Handler):
    def get(self):
        re = self.request.get('re')
        verification_code = self.request.get("code")
        args = dict(client_id=FACEBOOK_APP_ID,
                    redirect_uri=self.request.path_url)
        if verification_code:
            args["client_secret"] = FACEBOOK_APP_SECRET
            args["code"] = verification_code
            response = cgi.parse_qs(urllib.urlopen(
                "https://graph.facebook.com/oauth/access_token?" +
                urllib.urlencode(args)).read())
            access_token = response["access_token"][-1]
            
            # Download the user profile and cache a local instance of the
            # basic profile info
            profile = json.load(urllib.urlopen(
                "https://graph.facebook.com/me?" +
                urllib.urlencode(dict(access_token=access_token))))
            user_find = db.GqlQuery("SELECT * FROM FBUser WHERE id = :id " ,id = str(profile["id"]) ).fetch(None,0)
            if user_find:
                user = FBUser(key_name=str(profile["id"]), id=str(profile["id"]),
                            fbname=profile["name"], access_token=access_token,
                            profile_url=profile["link"],stop=user_find[0].stop,admin=user_find[0].admin)
            else:
                user = FBUser(key_name=str(profile["id"]), id=str(profile["id"]),
                            fbname=profile["name"], access_token=access_token,
                            profile_url=profile["link"],stop=False,admin=False)
            user.put()
            set_cookie(self.response, "fb_user", str(profile["id"]),
                       expires=time.time() + 30 * 86400)
            
            self.redirect('/')
            
        else:
            self.redirect(
                "https://graph.facebook.com/oauth/authorize?" +
                urllib.urlencode(args))

class NoPermission(Handler):
    def get(self):
        self.error(406)
        return

class Stop(Handler):
    def get(self):
        self.error(500)
        return

class Content(Handler):
    def get(self):
        self.render('content.htm')

class Note(Handler):
    def get(self):
        self.render('note.html')

class Signup(Handler):
    def get(self):
        if not self.fb_user:
            self.redirect('/fblogin?re=signup')
        else:
            if self.fb_user.stop:
                self.redirect('/stop')
            else:
                p = db.GqlQuery("SELECT * FROM Participant WHERE fb_id = :id " ,id = str(self.fb_user.id)).fetch(None,0)
                if p:
                    self.redirect('/edit')
                else:
                    fbname = self.fb_user.fbname
                    self.render('signup.html',fbname=fbname,err_class="hide")

    def post(self):
        if not self.fb_user:
            self.redirect('/fblogin')
        else:
            if self.fb_user.stop:
                self.redirect('/stop')
            else:
                p = db.GqlQuery("SELECT * FROM Participant WHERE fb_id = :id " ,id = str(self.fb_user.id)).fetch(None,0)
                name = self.request.get('name')
                gender = self.request.get('gender')
                birthdate = self.request.get('birthdate')
                identification = self.request.get('identification')
                school = self.request.get('school')
                email = self.request.get('email')
                phone = self.request.get('phone')
                address = self.request.get('address')
                meal = self.request.get('meal')
                tshirt = self.request.get('tshirt')
                emergency_contact = self.request.get('emergency_contact')
                emergency_contact_phone = self.request.get('emergency_contact_phone')
                prefix = self.request.get('prefix')
                fb_id = self.fb_user.id
                fb_name = self.fb_user.fbname
                fb_url = 'https://www.facebook.com/'+ self.fb_user.id                
                check = False
                check_prefix = ''
                show = True

                params = dict(name = name, gender=gender,birthdate=birthdate,
                    identification=identification,school=school,email=email,
                    phone=phone,address=address,meal=meal,tshirt=tshirt,
                    emergency_contact=emergency_contact,
                    emergency_contact_phone=emergency_contact_phone,
                    prefix=prefix,fbname=self.fb_user.fbname)
                have_error=False

                if not valid_name(name):
                    params['error_name'] = u"填寫錯誤"
                    have_error = True
                if not valid_gender(gender):
                    params['error_gender'] = u"填寫錯誤"
                    have_error = True
                if not valid_birthdate(birthdate):
                    params['error_birthdate'] = u"填寫錯誤"
                    have_error = True
                if not valid_identification(identification):
                    params['error_identification'] = u"填寫錯誤"
                    have_error = True
                if not valid_school(school):
                    params['error_school'] = u"填寫錯誤"
                    have_error = True
                if not valid_email(email):
                    params['error_email'] = u"填寫錯誤"
                    have_error = True
                if not valid_phone(phone):
                    params['error_phone'] = u"填寫錯誤"
                    have_error = True
                if not valid_address(address):
                    params['error_address'] = u"填寫錯誤"
                    have_error = True
                if not valid_meal(meal):
                    params['error_meal'] = u"填寫錯誤"
                    have_error = True
                if not valid_tshirt(tshirt):
                    params['error_tshirt'] = u"填寫錯誤"
                    have_error = True
                if not valid_emergency_contact(emergency_contact):
                    params['error_emergency_contact'] = u"填寫錯誤"
                    have_error = True
                if not valid_emergency_contact_phone(emergency_contact_phone):
                    params['error_emergency_contact_phone'] = u"填寫錯誤"
                    have_error = True
                if have_error:
                    params['prefix']  = prefix
                    self.render('signup.html', **params)
                else:        
                    p = Participant.add_participant(name=name, gender=gender, birthdate=birthdate, 
                        identification=identification, school=school, email=email, phone=phone, 
                        address=address, meal=meal, tshirt=tshirt, emergency_contact=emergency_contact, 
                        emergency_contact_phone=emergency_contact_phone, prefix=prefix, fb_id=fb_id, 
                        fb_name=fb_name, fb_url=fb_url, check=check, check_prefix=check_prefix, 
                        show=show,post_created=datetime.now()+timedelta(hours=8))
                    p.put()
                    p.last_modified = datetime.now()+timedelta(hours=8)
                    p.put()
                    self.render('success.html')

class Edit(Handler):
    def get(self):
        if not self.fb_user:
            self.redirect('/fblogin?re=signup')
        else:
            if self.fb_user.stop:
                self.redirect('/stop')
            else:
                p = db.GqlQuery("SELECT * FROM Participant WHERE fb_id = :id " ,id = str(self.fb_user.id)).fetch(None,0)
                if p:
                    name = p[0].name
                    gender = p[0].gender
                    birthdate = p[0].birthdate
                    identification = p[0].identification
                    school = p[0].school
                    email = p[0].email
                    phone = p[0].phone
                    address = p[0].address
                    meal = p[0].meal
                    tshirt = p[0].tshirt
                    emergency_contact = p[0].emergency_contact
                    emergency_contact_phone = p[0].emergency_contact_phone
                    prefix = p[0].prefix

                    params = dict(name = name, gender=gender,birthdate=birthdate,
                        identification=identification,school=school,email=email,
                        phone=phone,address=address,meal=meal,tshirt=tshirt,
                        emergency_contact=emergency_contact,
                        emergency_contact_phone=emergency_contact_phone,
                        prefix=prefix,fbname=self.fb_user.fbname)
                    params['prefix']  = prefix
                    self.render('signup.html',**params)
                else:
                    self.redirect('/signup')

    def post(self):
        if not self.fb_user:
            self.redirect('/fblogin')
        else:
            if self.fb_user.stop:
                self.redirect('/stop')
            else:
                name = self.request.get('name')
                gender = self.request.get('gender')
                birthdate = self.request.get('birthdate')
                identification = self.request.get('identification')
                school = self.request.get('school')
                email = self.request.get('email')
                phone = self.request.get('phone')
                address = self.request.get('address')
                meal = self.request.get('meal')
                tshirt = self.request.get('tshirt')
                emergency_contact = self.request.get('emergency_contact')
                emergency_contact_phone = self.request.get('emergency_contact_phone')
                prefix = self.request.get('prefix')

                params = dict(name = name, gender=gender,birthdate=birthdate,
                    identification=identification,school=school,email=email,
                    phone=phone,address=address,meal=meal,tshirt=tshirt,
                    emergency_contact=emergency_contact,
                    emergency_contact_phone=emergency_contact_phone,
                    prefix=prefix,fbname=self.fb_user.fbname)
                have_error=False

                if not valid_name(name):
                    params['error_name'] = u"填寫錯誤"
                    have_error = True
                if not valid_gender(gender):
                    params['error_gender'] = u"填寫錯誤"
                    have_error = True
                if not valid_birthdate(birthdate):
                    params['error_birthdate'] = u"填寫錯誤"
                    have_error = True
                if not valid_identification(identification):
                    params['error_identification'] = u"填寫錯誤"
                    have_error = True
                if not valid_school(school):
                    params['error_school'] = u"填寫錯誤"
                    have_error = True
                if not valid_email(email):
                    params['error_email'] = u"填寫錯誤"
                    have_error = True
                if not valid_phone(phone):
                    params['error_phone'] = u"填寫錯誤"
                    have_error = True
                if not valid_address(address):
                    params['error_address'] = u"填寫錯誤"
                    have_error = True
                if not valid_meal(meal):
                    params['error_meal'] = u"填寫錯誤"
                    have_error = True
                if not valid_tshirt(tshirt):
                    params['error_tshirt'] = u"填寫錯誤"
                    have_error = True
                if not valid_emergency_contact(emergency_contact):
                    params['error_emergency_contact'] = u"填寫錯誤"
                    have_error = True
                if not valid_emergency_contact_phone(emergency_contact_phone):
                    params['error_emergency_contact_phone'] = u"填寫錯誤"
                    have_error = True
                if have_error:
                    params['prefix']  = prefix
                    self.render('signup.html', **params)
                else:        
                    p = greetings = db.GqlQuery("SELECT * FROM Participant WHERE fb_id = :fb_id " ,fb_id = self.fb_user.id ).fetch(None,0)
                    p_id=p[0].key().id()
                    key = db.Key.from_path('Participant', int(p_id), parent=participants_key())
                    p = db.get(key)
                    p.name = name
                    p.gender = gender
                    p.birthdate = birthdate
                    p.identification=identification
                    p.school = school
                    p.email = email
                    p.phone = phone
                    p.address = address
                    p.meal = meal
                    p.tshirt = tshirt
                    p.emergency_contact = emergency_contact
                    p.emergency_contact_phone = emergency_contact_phone
                    p.prefix = prefix
                    p.put()
                    p.last_modified = datetime.now()+timedelta(hours=8)
                    p.put()
                    self.render('success.html')
                
class Contact(Handler):
    def get(self):
        self.render('contact.html')

class Console(Handler):
    def get(self):
        self.render('console.html')
    def post(self):
        pwd = self.request.get('passw')
        if pwd == 'exam-29-jizzed':
            self.redirect('/console/participant')
        else:
            self.redirect('/nopermission')

class ConsoleParticipant(Handler):
    def get(self):
        participants = greetings = db.GqlQuery("SELECT * FROM Participant WHERE show = :show", show=True).fetch(None, 0)
        self.render('console_participant.html', participants=participants, name="admin")

class ConsoleParticipant_PostPage(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Participant', int(post_id), parent=participants_key())
        participant = db.get(key)
        if not participant:
            self.error(404)
            return
        self.render("console_participant_per.html", participant = participant, name='admin' )

class ConsoleParticipant_Delete(Handler):
    def get(self):        
        get_id = self.request.get('id')
        if not get_id.isdigit():
            get_id = '0'
        post_id = int(get_id)
        key = db.Key.from_path('Participant', int(post_id), parent=participants_key())
        participant = db.get(key)
        if not participant:
            self.error(404)
        else:
            participant.show = False
            participant.put()
            self.redirect('/console')

class Picture(Handler):
    def get(self):
        self.render('picture.html')

class Subject(Handler):
    def get(self):
        self.render('subject.html')

app = webapp2.WSGIApplication([('/', MainPage),
                                ('/index' , Index),
                                ('/fblogin',FBLogin),
                                ('/nopermission' , NoPermission),
                                ('/stop' , Stop),
                                ('/content',Content),
                                ('/signip', Signup),
                                ('/edit',Edit),
                                ('/console',Console),
                                ('/console/participant', ConsoleParticipant),
                                ('/console/participant/([0-9]+)' , ConsoleParticipant_PostPage),
                                ('/console/participant/delete' , ConsoleParticipant_Delete),
                                ('/note', Note), 
                                ('/subject', Subject),
                                ],
                                debug=True)
