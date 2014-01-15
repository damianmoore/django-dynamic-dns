import clouddns

from . import DynamicDnsPlugin


class Rackspace(DynamicDnsPlugin):
    def update(self, ip):
        dns = clouddns.connection.Connection(self.config['username'], self.config['api_key'])
        fqdn = self.domain.split('.', 1)[1]
        domain = dns.get_domain(name=fqdn)
        record = domain.get_record(name=self.domain)
        record.update(data=ip)