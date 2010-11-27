import email
import rfc822
import time
import uuid

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
        self.process(email.message_from_string("\n".join(self._contents)))
        self._sink.add(self)

        d = defer.Deferred()
        reactor.callLater(0, d.callback, "message accepted")
        return d

    def connectionLost(self):
        raise Exception("connectionLost")

    def process(self, message):
        self.id    = str(uuid.uuid4())
        self.parts = {}
        self.meta  = {
                   'id': self.id,
                   'to': message.get('To', self._origin),
                 'from': message.get('From', self._dest),
              'subject': message.get('Subject', None),
           'short_time': time.strftime("%I:%M %p %m/%d"),
            'long_time': time.strftime("%a, %e %b %Y %H:%M:%S"),
                'parts': [],
        }

        # first, store a copy of the undecoded original
        orig_id = str(uuid.uuid4())
        self.meta['parts'].append((orig_id, 'Original Message'))
        self.parts[orig_id] = {
            'cid': None,
            'name': 'Original Message',
            'type': 'text/plain',
            'payload': message.as_string()
        }

        # next, decode and store the message part-by-part
        for part in message.walk():
            if part.is_multipart():
                continue

            part_id = str(uuid.uuid4())
            part = {
                'cid': part['Content-Id'],
                'name': part.get_filename(),
                'type': part.get_content_type(),
                'payload': part.get_payload(decode=True),
            }

            if part['name'] is not None:
                part_desc = "%s (%s)" % (part['name'], part['type'])
            else:
                part_desc = part['type']

            self.meta['parts'].append((part_id, part_desc))
            self.parts[part_id] = part


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
