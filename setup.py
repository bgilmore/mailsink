from setuptools import setup
from mailsink import __version__

setup(
    name = "mailsink",
    version = __version__,
    description = "a mock SMTP server",
    url = "http://github.com/bgilmore/mailsink",

    maintainer = "Brandon Gilmore",
    maintainer_email = "brandon@mg2.org",
    license = "BSD",

    platforms = "any",
    packages = [ "mailsink" ],

    entry_points = {
        "console_scripts": [ "mailsinkd = mailsink:run" ]
    },
)

