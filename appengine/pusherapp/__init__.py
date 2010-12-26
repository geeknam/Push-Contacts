#!/usr/bin/env python

"""
A Google App Engine wrapper for the pusherapp service (http://www.pusherapp.com).

Typical usage (e.g. using a taskqueue, see: http://code.google.com/appengine/docs/python/taskqueue/):

    import pusherapp
    
    from google.appengine.api import urlfetch
    from google.appengine.api.labs import taskqueue
    from google.appengine.ext import webapp
    
    class MyWebAppRequestHandler(webapp.RequestHandler):
        
        def get(self):
            # ...
        
        def post(self):
            # ...
            
            # Trigger some event, using a taskqueue
            taskqueue.add(url='/worker/push/channel/event', params={'msg': 'Hello world!'})
            
            # ...
        
    class WorkerPushRequestHandler(webapp.RequestHandler):
        
        def post(self, channel, event):
        
            # Construct pusher...
            pusher = pusherapp.Pusher(key=self.pusher_api_key)
            
            # Construct data from request parameters...
            data = dict([(arg, self.request.get(arg)) for arg in self.request.arguments()])
            
            # Trigger the event...
            result = pusher[channel].trigger(event, data=data)
            
            # Handle success/failure...
            if result.status_code >= 200 and result.status_code <= 299:
                self.response.headers["Content-Type"] = "text/plain"
                self.response.out.write("OK")
                #self.response.out.write("\nchannel: %s, event: %s, data: %s" % (channel, event, str(data)))
            else:
                self.error(result.status_code)

"""

import hashlib, hmac, logging, md5, sys, time, urllib

from django.utils import simplejson as json
from google.appengine.api import urlfetch

host   = 'api.pusherapp.com'
port   = 80
app_id = False
key    = False
secret = False

class Pusher():
    __app_id = False
    __key = False
    __secret = False
    __channels = {}
    __globals = {}

    def __init__(self, **kwargs):
        # Read in globals...
        self.__globals = globals()
        
        # Get (required) app_id...
        if kwargs.has_key('app_id'):
            self.__app_id = kwargs['app_id']
        elif self.__globals['app_id']:
            self.__app_id = self.__globals['app_id']
        else:
            # app_id is required but not specified, raise exception
            raise NameError('AppIdRequired', 'App id is required, but not specified')

        # Get (required) key...
        if kwargs.has_key('key'):
            self.__key = kwargs['key']
        elif self.__globals['key']:
            self.__key = self.__globals['key']
        else:
            # Key is required but not specified, raise exception
            raise NameError('KeyRequired', 'Key is required, but not specified')
            
        # Get (required) secret...
        if kwargs.has_key('secret'):
            self.__secret = kwargs['secret']
        elif self.__globals['secret']:
            self.__secret = self.__globals['secret']
        else:
            # secret is required but not specified, raise exception
            raise NameError('SecretRequired', 'Secret is required, but not specified')

        # Get (optional) channel
        if kwargs.has_key('channel'):
            self.__make_channel(kwargs['channel'])
    
    def __getitem__(self, key):
        if not self.__channels.has_key(key):
            # if channel doesn't exist, make one...
            return self.__make_channel(key)
        return self.get_channel(key)
        
    def __make_channel(self, channel):
        self.__channels[channel] = self.Channel(channel, self)
        return self.__channels[channel]
        
    def add_channel(self, channel):
        return self.__make_channel(channel)
    
    def get_channel(self, channel):
        return self.__channels[channel]
    
    def get_app_id(self):
        return self.__app_id
    
    def get_key(self):
        return self.__key
    
    def get_secret(self):
        return self.__secret
    
    class Channel():
        __pusher = False
        __name = False
        
        def __init__(self, channel, pusher):
            self.__pusher = pusher
            self.__name = channel
            
        def trigger(self, event, data={}):
            host = globals()['host']
            app_id = self.__pusher.get_app_id()
            key = self.__pusher.get_key()
            
            # JSON-encode the data...
            data = json.dumps(data)
            body_md5 = md5.new(data).hexdigest()

            # Construct the pusher path...
            pusher_path = '/apps/%s/channels/%s/events' % (app_id, self.__name)
            
            # Construt the pusher end point...
            pusher_end_point = 'http://%s%s' % (host, pusher_path)
            
            # Construct query string
            pusher_qs = {
                'name':event,
                'auth_key': key,
                'auth_timestamp': '%d' % time.time(),
                'auth_version': '1.0',
                'body_md5':body_md5
            }
            
            # Sign the request... (see: http://www.pusherapp.com/docs/rest_api)

            # Sort pusher_qs by key
            #keys = sorted(pusher_qs)
            #vals = [pusher_qs[key] for key in keys]
            #pusher_qs = dict(zip(keys, vals))
            
            # Concatenate keys, values
            #pusher_qs_joined = '&'.join([key + '=' + str(pusher_qs[key]) for key in pusher_qs])
            pusher_qs_joined = 'auth_key=%s&auth_timestamp=%d&auth_version=%s&body_md5=%s&name=%s' % (key, time.time(), '1.0', body_md5, event)
            # The signature is generated by signing the following string...
            string_to_sign = "POST\n%s\n%s" % (pusher_path, pusher_qs_joined)
            
            # This should be signed by generating the HMAC SHA256 hex digest with secret key...
            # (See: http://goo.gl/JZyt)
            auth_signature = hmac.new(self.__pusher.get_secret(), string_to_sign, hashlib.sha256).hexdigest()
            
            # Complete query string
            pusher_qs['auth_signature'] = auth_signature
            
            pusher_end_point = '%s?%s' % (pusher_end_point, urllib.urlencode(pusher_qs))
            
            
            # Log this event...
            logging.debug("Triggering %s on the %s channel (%s, %s)\n" % (event, self.__name, pusher_end_point, data))
            
            # Fire the event, RESTfully...
            return urlfetch.fetch(
                url=pusher_end_point,
                payload=data,
                method=urlfetch.POST,
                headers={'Content-Type': 'application/json'},
                deadline=10
            )