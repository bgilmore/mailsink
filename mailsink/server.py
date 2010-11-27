import optparse
import sys

from twisted.internet import protocol, reactor
from twisted.mail.smtp import ESMTP
from twisted.python import log
from twisted.web import server as webserver

from mailsink import handler, webui, __version__

class Sink(object):
    """ specialized ring-buffer for message storage """

    def __init__(self, size=10):
        self._msg_ids  = [None for i in range(size)]
        self._store    = {}
        self._subs     = set()

    def subscribe(self, d):
        self._subs.add(d)

    def unsub(self, d):
        self._subs.discard(d)

    def add(self, item):
        self._store[item.id] = item
        expired = self._msg_ids.pop()
        self._msg_ids.insert(0, item.id)

        if expired is not None:
            del self._store[expired]

        # notify subscribers
        for d in self._subs:
            d.callback(item)

        self._subs.clear()

    def contents(self):
        return [self._store[msgid] for msgid in reversed(self._msg_ids) if msgid is not None]

    def __contains__(self, key):
        return key in self._store

    def __getitem__(self, key):
        return self._store[key]

    def __iter__(self):
        for i in xrange(len(self._store)):
          yield self._store[i]

class Faucet(protocol.ServerFactory):
    """ fills up the sink """

    protocol = ESMTP

    def __init__(self, sink):
        self._sink = sink

    def buildProtocol(self, addr):
        p = protocol.ServerFactory.buildProtocol(self, addr)
        p.deliveryFactory = handler.MessageHandlerFactory(self._sink)
        return p

def run():
    parser = optparse.OptionParser(usage="usage: %prog [options]",
                                   version="%prog " + __version__)

    parser.add_option("-s", "--smtp-port", dest="smtp_port", default=8025, type="int",
                      help="port to use for SMTP server (default: %default)")
    parser.add_option("-w", "--web-port", dest="web_port", default=8080, type="int",
                      help="port to use for Web UI (default: %default)")

    opt, arg = parser.parse_args()
    if len(arg) > 0:
        parser.error("incorrect number of arguments")

    sink = Sink()
    site = webserver.Site(webui.SinkViewer(sink))
    site.requestFactory    = webui.TidyRequest
    site.displayTracebacks = False

    log.startLogging(sys.stdout)
    reactor.listenTCP(opt.smtp_port, Faucet(sink))
    reactor.listenTCP(opt.web_port, site)
    reactor.run()

