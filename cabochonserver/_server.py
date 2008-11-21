from restclient import rest_invoke
from simplejson import loads, dumps
from random import random
from datetime import datetime
from sha import sha
from wsseauth import wsse_header

def fromjson(json):
    try:
        return loads(json)
    except:
        print "Failed to load json from", json
        raise

class Event(object):
    """bag to hold event data"""
    def __init__(self, server, event, url, method="POST"):
        self.server = server.rstrip('/')
        self.event = event
        self.url = url
        self.method = method
    def __eq__(self, rhs):
        return (self.server == rhs.server and
                self.event == rhs.event and
                self.url == rhs.url)
    def __ne__(self, rhs):
        return not (self == rhs)
    def __str__(self):
        return ','.join([
            self.server,
            self.event,
            self.url,
            self.method]
            )

class ServerError(Exception):
    def __init__(self, reason, orig = None):
        self.original_exception = orig
        Exception.__init__(self, reason)

class ServerInstaller:
    def __init__(self, config_file, username='', password=''):
        self.config_file = config_file
        self.username = username
        self.password = password
        self.events = []
        try:
            f = open(config_file, "r")
            for line in f:
                if line.startswith("#"):
                    continue
                if not "," in line:
                    continue
                if line.endswith("\n"):
                    line = line[:-1]         
                e = Event(*line.split(','))
                self.events.append(e)
        except:
            pass #no existing events file

    def rest_invoke(self, *args, **kwargs):
        if self.username:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = 'WSSE profile="UsernameToken"'
            headers['X-WSSE'] = wsse_header(self.username, self.password)

            kwargs['headers'] = headers
        kwargs['params'] = dict((key, dumps(value)) for key, value in kwargs['params'].items())                
        try:
            return rest_invoke(*args, **kwargs)
        except socket.error, e:
            raise ServerError("Couldn't connect to server", e)

    def save(self):
        if not self.events:
            return
        f = open(self.config_file, "w")
        f.write('\n'.join(str(e) for e in self.events))
        f.close()
        
    def addEvent(self, server, event, url, method="POST"):
        self.events.append(Event(server, event, url, method))
        #create the event
        try:
            urls = fromjson(self.rest_invoke(server + "/event/", method="POST", params={"name" : event}))
        except ValueError:
            raise ServerError("Server returned non-json", e)
        if not 'subscribe' in urls:
            raise ServerError("Server returned a result without a subscribe url")            
        subscribe_url = urls['subscribe']

        try:
            result = self.rest_invoke(server + subscribe_url, method="POST", params={'url' : url, 'method' : method})
        except ValueError:
            raise ServerError("Server returned non-json", e)
        if not 'unsubscribe' in result:
            raise ServerError("Server returned an unexpected result")


    def removeEvent(self, server, event, url):
        remove_event = Event(server, event, url)
        rm = [e for e in self.events
              if e == remove_event]

        results = []
        for candidate in rm:
            server = candidate.server
            event = candidate.event
            url = candidate.url
            status = self.rest_invoke(server + "/unsubscribe_by_event", method="POST", params={'url' : url, 'event' : event})
            results.append(status)
            self.events.remove(candidate)
        return '\n'.join(results)


    def removeAll(self):
        results = []
        for e in self.events:
            server = e.server
            event = e.event
            url = e.url
            status = self.rest_invoke(server + "/unsubscribe_by_event", method="POST", params={'url' : url, 'event' : event})
            results.append(status)
        self.events = []
        return '\n'.join(results)
