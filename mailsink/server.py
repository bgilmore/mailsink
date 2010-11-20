from twisted.internet import protocol
from twisted.mail.smtp import ESMTP
from mailsink.handler import MessageHandlerFactory

class Sink(object):
    """ specialized ring-buffer for message storage """

    def __init__(self, size=10):
        self._store = [None for i in range(size)]
        self._subs  = set()

    def subscribe(self, d):
        self._subs.add(d)

    def unsub(self, d):
        self._subs.discard(d)

    def add(self, item):
        self._store.pop()
        self._store.insert(0, item)

        # notify subscribers
        for d in self._subs:
            d.callback(item)

        self._subs.clear()

    def contents(self):
        return [message for message in reversed(self._store) if message is not None]

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
        p.deliveryFactory = MessageHandlerFactory(self._sink)
        return p

