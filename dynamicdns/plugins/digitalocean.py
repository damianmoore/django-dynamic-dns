import json

import requests

from . import DynamicDnsPlugin


class DigitalOcean(DynamicDnsPlugin):
    def update(self, ip):
        client_id = self.config['client_id']
        api_key = self.config['api_key']
        prefix, fqdn = self.domain.split('.', 1)
        subdomain = False

        # Get domain ID
        url = 'https://api.digitalocean.com/domains?client_id={}&api_key={}'.format(client_id, api_key)
        content = json.loads(requests.get(url).content)
        domain_id = None
        if 'domains' not in content:
            raise LookupError('Error connecting to DigitalOcean API. Status: {}'.format(content['status']))
        for domain in content['domains']:
            if domain['name'] in [self.domain, fqdn]:
                domain_id = domain['id']
                if domain['name'] == fqdn:
                    subdomain = True
                break
        if not domain_id:
            raise LookupError('Domain ID for {} not found in DigitalOcean API call \'/domains\''.format(self.domain))

        # Get domain records
        url = 'https://api.digitalocean.com/domains/{}/records?client_id={}&api_key={}'.format(domain_id, client_id, api_key)
        content = json.loads(requests.get(url).content)
        record_id = None
        for record in content['records']:
            if record['record_type'] == 'A' and ((subdomain and record['name'] == prefix) or (not subdomain and record['name'] == '@')):
                record_id = record['id']
                break
        if not record_id:
            raise LookupError('\'A\' record for {} not found in DigitalOcean API call \'/domains/{}/records\''.format(self.domain, domain_id))

        # Update record with new IP
        url = 'https://api.digitalocean.com/domains/{}/records/{}/edit?client_id={}&api_key={}&data={}'.format(domain_id, record_id, client_id, api_key, ip)
        content = json.loads(requests.get(url).content)
        if content['status'] == 'OK':
            raise RuntimeError('Couldn\'t update IP address in DigitalOcean DNS record via API call \'/domains/{}/records/{}/edit?data={}\''.format(domain_id, record_id, ip))
