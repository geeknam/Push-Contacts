# -*- coding: utf-8 -*-

import unittest
from webtest import TestApp
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import xmpp
import main

class RegisterHandlerTest(unittest.TestCase):  
    def setUp(self):
        self.application = webapp.WSGIApplication([('/register', main.RegisterHandler)], debug=True)
    def test_default(self):
        app = TestApp(self.application)
        response = app.get('/register')
        self.assertEqual('200 OK', response.status)
        self.assertTrue('Must specify devregid' in response)
    def test_with_param(self):
        app = TestApp(self.application)
        response = app.get('/register?devregid=testdevregid')
        self.assertEqual('200 OK', response.status)
        self.assertTrue('OK' in response)

class UnregisterTest(unittest.TestCase):
    def setUp(self):
        self.application = webapp.WSGIApplication([('/unregister', main.RegisterHandler)], debug=True)
    def test_default(self):
        app = TestApp(self.application)
        response = app.get('/unregister')
        self.assertEqual('200 OK', response.status)
        self.assertTrue('Must specify devregid' in response)
    def test_with_param(self):
        app = TestApp(self.application)
        response = app.get('/unregister?devregid=testdevregid')
        self.assertEqual('200 OK', response.status)
        self.assertTrue('OK' in response)

class ContactHandlerTest(unittest.TestCase):
    def setUp(self):
        self.application = webapp.WSGIApplication([('/send', main.ContactHandler)], debug=True)
    def test_lack_param(self):
        app = TestApp(self.application)
        response = app.get('/send?name=Ngo%20Minh%20Nam')
        self.assertTrue('error_params' in response)
    def test_not_registered(self):
        app = TestApp(self.application)
        response = app.get('/send?name=Ngo%20Minh%20Nam&phone=94457319')
        self.assertTrue('error_register' in response)
    def test_c2dm_error(self):
        token_entry = main.Info()
        token_entry.registration_id = "mytoken"
        token_entry.put()
        user_entry = main.Info(key_name="test@example.com")
        user_entry.registration_id = "testdevregid"   
        user_entry.put()

        app = TestApp(self.application)
        response = app.get('/send?name=Ngo%20Minh%20Nam&phone=94457319')
        self.assertTrue('error_c2dm' in response)

class SmsHandlerTest(unittest.TestCase):
    data = {"phone":"94457319","sms": "normal sms"}
    def setUp(self):
        self.application = webapp.WSGIApplication([('/sms', main.SmsHandler)], debug=True)
    def test_not_registered(self):
        app = TestApp(self.application)
        response = app.post('/sms', self.data)
        self.assertTrue('error_register' in response)
    def test_c2dm_error(self):
        token_entry = main.Info()
        token_entry.registration_id = "mytoken"
        token_entry.put()
        user_entry = main.Info(key_name="test@example.com")
        user_entry.registration_id = "testdevregid"   
        user_entry.put()
        app = TestApp(self.application)
        response = app.post('/sms', self.data)
        self.assertTrue('error_c2dm' in response)

# class PushHandlerTest(unittest.TestCase):
#     params = {"user":"emoinrp","sender":"Ngo Minh Nam","phone":"94457319","sms":"sms test case"}
#     def setUp(self):
#         self.application = webapp.WSGIApplication([('/push', main.PushHandler)], debug=True)
#         from google.appengine.api import apiproxy_stub_map
#         from google.appengine.api import datastore_file_stub
#         #from google.appengine.api import xmpp_stub
#         apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
#         apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3',datastore_file_stub.DatastoreFileStub('pushcontacts', '/dev/null', '/dev/null'))
#         #apiproxy_stub_map.apiproxy.RegisterStub('xmpp', urlfetch_stub.URLFetchServiceStub())
# 
#     def test_xmpp(self):
#         app = TestApp(self.application)
#         response = app.post('/push', self.params)
#         incoming = main.Incoming.get_by_key_name("emoinrp@gmail.com")
#         self.assertEqual(incoming.last_sender, self.params["phone"])

class StaticMethodTest(unittest.TestCase):
    def test_handle_unicode(self):
        result = main.handle_unicode("nåm")
        self.assertEqual("n\xc3\xa5m", result)
    def test_no_unicode(self):
        result = main.handle_unicode("nam")
        self.assertEqual("nam", result)




