from restclient import rest_invoke
from cabochonserver import ServerInstaller
from cabochon.tests.functional import CabochonTestServer
from simplejson import loads as fromjson
import os
import time
from paste.util.multidict import MultiDict

def test_server():
    test_server = CabochonTestServer()
    test_server.start()
    server_fixture = test_server.server_fixture

    server_url = "http://localhost:24532"

    status, body = rest_invoke(server_url + "/event/", method="GET", resp=True)
    if status['status'] != '200':
        raise RuntimeError("You need a Cabochon server running on port 24532")

    event_name = "cabochon_server_library_test_event"

    installer = ServerInstaller(".servers")
    installer.addEvent(server_url, event_name, "http://localhost:10424/example/1")
    installer.save()

    #get the fire url

    urls = fromjson(rest_invoke(server_url + "/event/", method="POST", params={'name':event_name}))
    fire_url = urls['fire']

    #fire the event
    rest_invoke(server_url + fire_url, method="POST", params={'morx':'fleem'})

    #wait a second
    time.sleep(1)

    #insure that we got it
    assert server_fixture.requests_received == [{'path': '/example/1', 'params': MultiDict([('morx', 'fleem')]), 'method': 'POST'}]            

    installer2 = ServerInstaller(".servers")

    os.remove(".servers")
