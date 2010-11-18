from twisted.internet import protocol
from twisted.mail.smtp import ESMTP
from mailsink.handler import MessageHandlerFactory

class Faucet(protocol.ServerFactory):
    """ fills up the sink """

    protocol = ESMTP

    def __init__(self, sink):
        self._sink = sink

    def buildProtocol(self, addr):
        p = protocol.ServerFactory.buildProtocol(self, addr)
        p.deliveryFactory = MessageHandlerFactory(self._sink)
        return p

