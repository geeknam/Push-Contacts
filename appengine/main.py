#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Written by - NGO MINH NAM (emoinrp@gmail.com)
# Third-party application server for C2DM on Google App Engine rewritten from Java to Python
# Original implementation from ChromToPhone (http://code.google.com/p/chrometophone/source/browse/#svn/trunk/appengine)

# Features: - Store/remove C2DM registration_id in/from datastore
#           - Send POST request to C2DM server to be pushed to the Android phone
# Notes:    - delay_while_idle and sendWithRetry is not implemented

from os import path

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.template import render
from google.appengine.api.labs import taskqueue

import urllib
import pusherapp

class Info(db.Model):
    registration_id = db.StringProperty(multiline=True)

class MainHandler(webapp.RequestHandler):
    def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			tmpl = path.join(path.dirname(__file__), 'static/html/main.html')
			context = {'user': user.nickname()}
			self.response.out.write(render(tmpl,context))

class RegisterHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        devregid = self.request.get('devregid')
        if not devregid:
            self.error(400)
            self.response.out.write('Must specify devregid')
        else:
            user = users.get_current_user()
            if user:
		        #Store registration_id and an unique key_name with email value
	            info = Info(key_name=user.email())
	            info.registration_id = devregid   
	            info.put()
	            self.response.out.write('OK')
            else:
                self.response.out.write('Not authorized')

class UnregisterHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        devregid = self.request.get('devregid')
        if not devregid:
            self.error(400)
            self.response.out.write('Must specify devregid')
        else:
	        user = users.get_current_user()
	        if user:
		        #Remove entry with the associated email value
	            info =  Info.get_by_key_name(user.email())
	            info.delete()
	            self.response.out.write('OK')
	        else:
		        self.response.out.write('Not authorized') 

class SmsHandler(webapp.RequestHandler):
    def post(self):
        phone_number = self.request.get('phone')
        sms = self.request.get('sms')
        
        user = users.get_current_user()
        if user:
	        data = {"data.sms" : sms,
	                "data.phone_number" : phone_number}
	        sendToPhone(self,data, user.email())
        else:
	        self.redirect(users.create_login_url(self.request.uri))

class SendHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        #URL decode params
        contact_name = urllib.unquote(self.request.get('name'))  
        phone_number = urllib.unquote(self.request.get('phone'))
        
        if not contact_name or not phone_number:
            self.error(400)
            self.response.out.write('error_params')
        else:
            user = users.get_current_user()
            if user:
	            #Send the message to C2DM server
                data = {"data.contact_name" : contact_name,
                        "data.phone_number" : phone_number}
                sendToPhone(self,data, user.email())
            else:
	            #User is not logged in
                self.redirect(users.create_login_url(self.request.uri))

#Helper method to send params to C2DM server
def sendToPhone(self,data,email):
	info = Info.get_by_key_name(email)
	if not info:
		self.response.out.write('error_register')
	else:
	    registration_id = info.registration_id

	    #Get authentication token pre-stored on datastore with ID 1
	    #Alternatively, it's possible to store your authToken in a txt file and read from it (CTP implementation)
	    info = Info.get_by_id(1)
	    authToken = info.registration_id
	    form_fields = {
	        "registration_id": registration_id,
	        "collapse_key": hash(email), #collapse_key is an arbitrary string (implement as you want)
	    }
	    form_fields.update(data)
	    form_data = urllib.urlencode(form_fields)
	    url = "https://android.clients.google.com/c2dm/send"
    
	    #Make a POST request to C2DM server
	    result = urlfetch.fetch(url=url,
	                            payload=form_data,
	                            method=urlfetch.POST,
	                            headers={'Content-Type': 'application/x-www-form-urlencoded',
	                                     'Authorization': 'GoogleLogin auth=' + authToken})
	    if result.status_code == 200:
		    self.response.out.write("OK")
	    else:
		    self.response.out.write('error_c2dm')

class PushHandler(webapp.RequestHandler):
    def post(self):
	    user = self.request.get('user')
	    phone = self.request.get('phone')
	    sms   = self.request.get('sms')
	    taskqueue.add(url='/worker/%s' % (user), params={'phone': phone, 'sms': sms})

class WorkerHandler(webapp.RequestHandler):

    pusher_api_key = "b83d2cada7ffe791153b"
    pusher_app_id  = "1718"
    pusher_secret  = "c21d24f1c95430e0aacb"
    
    def post(self, channel):
	    pusher = pusherapp.Pusher(app_id=self.pusher_app_id, key=self.pusher_api_key, secret=self.pusher_secret)
	    phone = self.request.get('phone')
	    sms   = self.request.get('sms')
	
	    data = {'phone': phone, 'sms': sms}
	    result = pusher[channel].trigger('my_event', data=data)    

	        
def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/register', RegisterHandler),
                                          ('/unregister', UnregisterHandler),
                                          ('/send', SendHandler),
                                          ('/sms', SmsHandler),
                                          ('/push', PushHandler),
                                          (r'/worker/(.*)', WorkerHandler)
                                          ],
                                          debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
