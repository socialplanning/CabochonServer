from restclient import rest_invoke
from simplejson import loads as fromjson

class ServerInstaller:
    def __init__(self, config_file):
        self.config_file = config_file
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
                self.events.append (tuple(line.split(",")))
        except:
            pass #no existing events file

    def save(self):
        f = open(self.config_file, "w")
        for event in self.events:
            f.write(",".join(event))
        f.close()
        
    def addEvent(self, server, event, url, method="POST"):
        self.events.append((server, event, url, method))

        #create the event
        urls = fromjson(rest_invoke(server + "/event", method="POST", params={"name" : event}))
        subscribe_url = urls['subscribe']

        rest_invoke(server + subscribe_url, method="POST", params={'url' : url, 'method' : method})

    def removeEvent(self, server, event, url):
        rm = []
        for candidate in self.events:
            if candidate[0:3] == (server, event, url):
                rm.append(candidate)

        for candidate in rm:
            (server, event, url) = candidate
            rest_invoke(server + "unsubscribe_by_event", method="POST", params={'url' : url, 'event' : event})
            events.remove(candidate)


    def removeAll(self):
        for e in self.events:
            (server, event, url) = e
            rest_invoke(server + "unsubscribe_by_event", method="POST", params={'url' : url, 'event' : event})
            events.remove(e)
