import requests

from . import DynamicDnsPlugin


class Rackspace(DynamicDnsPlugin):
    def update(self, ip):
        fqdn = self.domain.split('.', 1)[1]

        # Authenticate to get token and tenent IDs
        data = {'auth': {'RAX-KSKEY:apiKeyCredentials': {'username': self.config['username'], 'apiKey': self.config['api_key']}}}
        response = requests.post('https://identity.api.rackspacecloud.com/v2.0/tokens', json=data).json()
        token_id = response['access']['token']['id']
        tenant_id = response['access']['token']['tenant']['id']

        # Get domain ID for fetching/updateing records of
        headers = {'X-Auth-Token': token_id}
        response = requests.get(f'https://dns.api.rackspacecloud.com/v1.0/{tenant_id}/domains?name={fqdn}', headers=headers).json()
        domain_id = response['domains'][0]['id']

        # Get record for the subdomain
        response = requests.get(f'https://dns.api.rackspacecloud.com/v1.0/{tenant_id}/domains/{domain_id}/records?type=A&name={self.domain}', headers=headers).json()
        record_id = response['records'][0]['id']

        # Update existing record
        record_data = {
            'records': [
                {
                    'name': self.domain,
                    'id': record_id,
                    'data': ip,
                    'ttl': 300
                }
            ]
        }
        requests.put(f'https://dns.api.rackspacecloud.com/v1.0/{tenant_id}/domains/{domain_id}/records', headers=headers, json=record_data).json()
