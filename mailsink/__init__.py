import optparse

from mailsink import server, webui
from twisted.internet import reactor
from twisted.web import server as webserver

version_info = (0, 0, 1)
__version__  = ".".join(map(str, version_info))

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

    sink = server.Sink()

    reactor.listenTCP(opt.smtp_port, server.Faucet(sink))
    reactor.listenTCP(opt.web_port, webserver.Site(webui.SinkViewer(sink)))
    reactor.run()

