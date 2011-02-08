#!/usr/bin/env python
#
# Copyright 2010 Ngo Minh Nam
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

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import xmpp
from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.ext.webapp import util
from model import Info, Incoming

import urllib, logging


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

# Used by Chrome Extension to check for logged in users
class CheckLoginHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        user = users.get_current_user()
        if user:
            self.response.out.write('LOGGED_IN')
        else:
            self.response.out.write('NOT_LOGGED_IN')

# Handle pushing SMS to phone  
class SmsHandler(webapp.RequestHandler):
    def post(self):
        phone_number = self.request.get('phone')
        sms = handle_unicode(self.request.get('sms'))
        
        user = users.get_current_user()
        if user:
            data = {"data.sms" : sms,
                    "data.phone_number" : phone_number}
            sendToPhone(self, data, user.email())

# Handle pushing a contact to phone
class ContactHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        #URL decode params
        contact_name = urllib.unquote(self.request.get('name'))  
        phone_number = urllib.unquote(self.request.get('phone'))
        
        if not contact_name or not phone_number:
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

# Handle notifying the received SMS through GTalk
class PushHandler(webapp.RequestHandler):
    def post(self):
        user  = self.request.get('user')
        phone = self.request.get('phone')
        sender= handle_unicode(self.request.get('sender')) #sender's name
        sms   = handle_unicode(self.request.get('sms'))
        if user:
            user_address = '%s@gmail.com' % (user)
            #Store the most recent sender
            incoming = Incoming(key_name=user_address)
            incoming.last_sender = phone   
            incoming.put()    
            # Send the received SMS to GTalk
            chat_message_sent = False
            if xmpp.get_presence(user_address):
                msg = "%s : %s" % (sender,sms)
                status_code = xmpp.send_message(user_address, msg)
                chat_message_sent = (status_code != xmpp.NO_ERROR)
            logging.debug(chat_message_sent) 

# Handle replies from GTalk to send SMS to the latest sender
class XMPPHandler(xmpp_handlers.CommandHandler):
    def text_message(self, message):
        #Get sender's email
        idx   = message.sender.index('/')
        email = message.sender[0:idx]
        #Get the latest sender's phone number
        incoming = Incoming.get_by_key_name(email)
        sender   = incoming.last_sender #sender's phone number - number
        sms      = handle_unicode(message.arg)
        data = {"data.sms" : sms,
                "data.phone_number" : sender}
        sendToPhone(self, data, email)
    def sms_command(self, message=None):
        idx_email = message.sender.index('/')
        email = message.sender[0:idx_email]
        idx_phone = message.arg.index(':')
        phone = message.arg[0:idx_phone]
        sms = handle_unicode(message.arg[idx_phone+1:])
        data = {"data.sms" : sms,
                "data.phone_number" : phone}
        sendToPhone(self, data, email)
        message.reply("SMS has been sent")

#Helper method to send params to C2DM server
def sendToPhone(self,data,email):
    #Get the registration entry
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
            self.response.out.write("error_c2dm")
        logging.debug(result.status_code)   

def handle_unicode(arg):
    if isinstance(arg, str):
        arg = unicode(arg, 'utf-8')
    return arg.encode('utf-8')
            
def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/register', RegisterHandler),
                                          ('/unregister', UnregisterHandler),
                                          ('/checklogin', CheckLoginHandler),
                                          ('/send', ContactHandler),
                                          ('/sms', SmsHandler),
                                          ('/push', PushHandler),
                                          ('/_ah/xmpp/message/chat/', XMPPHandler)
                                          ],
                                          debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
