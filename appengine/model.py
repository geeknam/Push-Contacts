from google.appengine.ext import db

class Info(db.Model):
    registration_id = db.StringProperty(multiline=True)

class Incoming(db.Model):
    last_sender = db.StringProperty(multiline=True)