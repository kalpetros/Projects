#!/usr/bin/env python

"""
main.py -- Udacity conference server-side Python App Engine
    HTTP controller handlers for memcache & task queue access

$Id$

created by wesc on 2014 may 24
updated by Petros Kalogiannakis on 2016 feb 02
"""

__author__ = 'Wesley Chun, Petros Kalogiannakis'

import webapp2
from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.api import memcache
from conference import ConferenceApi
from models import Session
from models import Speaker

class SetAnnouncementHandler(webapp2.RequestHandler):
    def get(self):
        """Set Announcement in Memcache."""
        ConferenceApi._cacheAnnouncement()
        self.response.set_status(204)

class SendConfirmationEmailHandler(webapp2.RequestHandler):
    def post(self):
        """Send email confirming Conference creation."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You created a new Conference!',            # subj
            'Hi, you have created a following '         # body
            'conference:\r\n\r\n%s' % self.request.get(
                'conferenceInfo')
        )

class SpeakerCheck(webapp2.RequestHandler):
    def post(self):
        """When a new session is added to a conference, check the speaker."""
        common_speakers = []
        featured_speakers = []
        speaker_counter {}
        # Get conference object from request
        conf_key = ndb.Key(urlsafe=self.request.get('c_keySt'))

        # Get conference's sessions
        sessions = Session.query(ancestor=conf_key)
        # Get speakers
        speakers = Speaker.query()

        # Add all speakers in the array
        for session in sessions:
            if session.speaker:
                common_speakers.append(session.speaker)

        # Find most common speakers using a dict
        for speaker in common_speakers:
            if speaker in speaker_counter:
                speaker_counter[speaker] += 1
            else:
                speaker_counter[speaker] = 1

        # Sort speakers by their sessions (speakers with most sessions are shown first)
        popular_speakers = sorted(speaker_counter, key = speaker_counter.get, reverse = True)

        # Add speakers with more than 2 session in the featured_speakers array
        for word, key in speaker_counter.iteritems():
            if key > 2:
                featured_speakers.append(word)

        MEMCACHE_CONFERENCE_KEY = "FEATURED: %s" % conf_key.urlsafe()
        # Add featured speakers in memcache
        for speaker in featured_speakers:
            memcache.set(MEMCACHE_CONFERENCE_KEY, speaker)

app = webapp2.WSGIApplication([
    ('/crons/set_announcement', SetAnnouncementHandler),
    ('/tasks/send_confirmation_email', SendConfirmationEmailHandler),
    ('/tasks/speaker_check', SpeakerCheck)
], debug=True)
