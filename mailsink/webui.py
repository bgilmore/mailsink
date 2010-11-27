from pkg_resources import resource_filename
from posixpath import normpath as normalize

from twisted.internet import defer, reactor
from twisted.web import resource, server, static

try:
    import json
except ImportError:
    import simplejson as json


class TidyRequest(server.Request):
    """ normalizes request path before rendering """
    def process(self):
        self.path = normalize(self.path)
        return server.Request.process(self)


class Error(resource.Resource):
    isLeaf = True

    def __init__(self, code, message):
        resource.Resource.__init__(self)
        self._code    = code
        self._message = message

    def render_GET(self, request):
        request.setResponseCode(self._code, self._message)
        request.setHeader("Content-Type", "text/html")
        return "<html><body><h1>%d %s</h1></body></html>" % (self._code, self._message,)

class Message(resource.Resource):

    def __init__(self, root):
        resource.Resource.__init__(self)
        self._root = root

    def getChild(self, name, request):
        if name in self._root._sink:
            return MessageComponent(self._root._sink[name])
        else:
            return Error(410, "Message no longer available")

class MessageComponent(resource.Resource):
    isLeaf = True

    def __init__(self, message):
        resource.Resource.__init__(self)
        self.message = message

    def render_GET(self, request):
        part = self.message.parts[request.postpath[0]]
        type = part.get("type", "text/plain")
        request.setHeader("Content-Type", type)

        if 'html' in type:
            body = part['payload']
            for pid, p in self.message.parts.items():
                if p['cid'] is not None:
                    old_uri = 'cid:' + p['cid'][1:-1]
                    new_uri = '/message/%s/%s' % (self.message.id, pid)
                    body = body.replace(old_uri, new_uri)
            return body
        else:
            return part['payload']

class SinkContents(resource.Resource):
    isLeaf = True

    def __init__(self, root):
        resource.Resource.__init__(self)
        self._root = root

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json")
        return json.dumps([message.meta for message in self._root._sink.contents()])


class SinkStreamer(resource.Resource):
    isLeaf = True

    def __init__(self, root):
        resource.Resource.__init__(self)
        self._sink = root._sink

    def render_GET(self, request):
        self._d = defer.Deferred().addCallback(self._update, request)
        timeout = reactor.callLater(10.0, self._timed_out, request)
        self._sink.subscribe(self._d)

        request.notifyFinish().addBoth(self._finalize, timeout)
        return server.NOT_DONE_YET

    def _update(self, message, request):
        # send activity to client
        request.write(json.dumps(message.meta))
        request.finish()

    def _timed_out(self, request):
        # timed out with no activity
        self._sink.unsub(self._d)
        request.setResponseCode(204, "No Content")

        request.finish()
        
    def _finalize(self, err, timeout):
        if err is not None:
            self._sink.unsub(self._d)

        if timeout.active():
            timeout.cancel()

class SinkViewer(resource.Resource):

    _static   = {
        # core app
        '':         static.File(resource_filename(__name__, 'static/index.html')),
        'sink.js':  static.File(resource_filename(__name__, 'static/sink.js')),
        'sink.css': static.File(resource_filename(__name__, 'static/sink.css')),

        # extra media
        'jquery.js':   static.File(resource_filename(__name__, 'static/jquery-1.4.4.min.js')),
        'favicon.ico': static.File(resource_filename(__name__, 'static/mail16.ico')),
        'icon.png':    static.File(resource_filename(__name__, 'static/mail512.png')),
    }

    _dispatch = {
        'messages.json': SinkContents,
        'updates.json': SinkStreamer,
        'message': Message,
    }

    def __init__(self, sink):
        resource.Resource.__init__(self)
        self._sink = sink

    def getChild(self, name, request):
        if name in self._dispatch:
            return self._dispatch[name](self)
        elif name in self._static:
            return self._static[name]
        else:
            return Error(404, "Not Found")
        
