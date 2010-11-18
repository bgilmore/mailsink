import email
import rfc822
import time

from twisted.internet import defer, reactor
from twisted.mail.smtp import IMessage, IMessageDelivery, IMessageDeliveryFactory
from zope.interface import implements


class Message:
    implements(IMessage)

    def __init__(self, sink, origin, dest):
        self._sink     = sink
        self._origin   = origin
        self._dest     = dest
        self._contents = []

    def __call__(self):
        return self

    def lineReceived(self, line):
        self._contents.append(line)

    def eomReceived(self):
        msg = email.message_from_string("\n".join(self._contents))

        self._sink.add({
                   'to': msg.get('To', self._origin),
                 'from': msg.get('From', self._dest),
              'subject': msg.get('Subject', None),
                 'body': msg.as_string(True),
            'timestamp': time.strftime("%I:%M %p"),
        })

        d = defer.Deferred()
        reactor.callLater(0, d.callback, "message accepted")
        return d

    def connectionLost(self):
        raise Exception("connectionLost")


class MessageHandler:
    implements(IMessageDelivery)

    def __init__(self, sink):
        self._sink = sink
        self._stamp = rfc822.formatdate()

    def receivedHeader(self, helo, origin, recipients):
        return "Recieved: from %s (%s)\n  by mail.sink with SMTP; %s" % (helo[0], helo[1], self._stamp,)

    def validateTo(self, user):
        return Message(self._sink, self._origin, user)

    def validateFrom(self, user, origin):
        self._origin = origin
        return origin


class MessageHandlerFactory:
    implements(IMessageDeliveryFactory)

    def __init__(self, sink):
        self._sink = sink

    def getMessageDelivery(self):
        return MessageHandler(self._sink)



# graveyard
#         for part in msg.walk():
#             type = part.get_content_type()
# 
#             if type == 'text/plain':
#                 print "--- text ---"
#                 print dir(part)
#                 print ""
#                 print part
#                 print "---\n"
#             elif type == 'text/html':
#                 print "--- html ---"
#                 print dir(part)
#                 print ""
#                 print part
#                 print "---\n"
#             else:
#                 print "--- non-viewable part (%s) ---" % (type,)
#                 if 'Content-Id' in part:
#                     print "CID:", part['Content-Id']
#                     print part.get_payload()
#                 else:
#                     print "NO CID"
# 
#                 print dir(part)
#                 print "---\n"
# 
