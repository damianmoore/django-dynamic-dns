class DynamicDnsPlugin(object):
    def __init__(self, domain, config):
        self.domain = domain
        self.config = config

    def update(self, ip):
        pass


from .dummy import Dummy
from .rackspace import Rackspace
from .digitalocean import DigitalOcean
