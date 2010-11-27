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
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Twisted",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Testing",
    ],

    platforms = "any",
    packages = [ "mailsink" ],
    install_requires = [
        "twisted >= 8.2.0"
    ],

    include_package_data = True,
    zip_safe = True,
    entry_points = {
        "console_scripts": [ "mailsinkd = mailsink:run" ]
    },
)

