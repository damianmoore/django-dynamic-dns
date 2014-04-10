import os
from setuptools import setup

setup(
    name = "django-dynamic-dns",
    version = "0.1.3",
    author = "Damian Moore",
    author_email = "django-dynamic-dns@epixstudios.co.uk",
    description = ("Machines on dynamic IPs can call this service at regular intervals (e.g. via cron) and when the server notices an address change it makes the relevant API call to update the DNS provider. Alternatively a simple DNS server is included which can be run instead of using an external DNS provider."),
    license = "BSD",
    keywords = "django dynamic dns server ip domain service",
    url = "https://github.com/damianmoore/django-dynamic-dns",
    download_url = 'https://github.com/damianmoore/django-dynamic-dns/archive/0.1.3.zip',
    packages = [
        'dynamicdns',
    ],
)
