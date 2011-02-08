import unittest
from webtest import TestApp
from google.appengine.ext import webapp
from google.appengine.ext import db
import model

class RegisterModelTest(unittest.TestCase):
    def setUp(self):
        info = model.Info(key_name="test@gmail.com")
        info.registration_id = "testdevregid"   
        info.put()
    def tearDown(self):
        info = model.Info.get_by_key_name("test@gmail.com")
        info.delete()
    def test_new_entity(self):
        info = model.Info.get_by_key_name("test@gmail.com")
        self.assertEqual('testdevregid', info.registration_id)

class TokenModelTest(unittest.TestCase):
    def setUp(self):
        info = model.Info()
        info.registration_id = "mytoken"   
        info.put()
    def test_token(self):
        info = model.Info.get_by_id(1)
        authToken = info.registration_id
        self.assertEqual('mytoken',authToken)
    