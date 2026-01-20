import requests

from . import DynamicDnsPlugin


class Hetzner(DynamicDnsPlugin):
    """
    Hetzner Cloud DNS plugin using the new Console API (api.hetzner.cloud).

    This plugin uses the new Hetzner Cloud DNS API, not the deprecated
    dns.hetzner.com API. The new API is available under Console > Networking > DNS.
    """

    API_BASE = 'https://api.hetzner.cloud/v1'

    def update(self, ip):
        """
        Updates an A record in Hetzner Cloud DNS.

        Required config keys:
        - api_token: Hetzner Cloud API token (from Console > Security > API Tokens)
        - zone_id: DNS zone ID (from Console > Networking > DNS)
        """
        api_token = self.config['api_token']
        zone_id = self.config['zone_id']

        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
        }

        # Determine record name relative to zone
        # e.g., for "home.example.com" in zone "example.com", record name is "home"
        # For the zone apex "example.com", record name is "@"
        record_name = self._get_record_name(zone_id, headers)

        # Try to update existing record via PUT, create if not found
        try:
            self._update_record(zone_id, record_name, ip, headers)
        except LookupError:
            # Record doesn't exist, create it
            self._create_record(zone_id, record_name, ip, headers)

    def _get_record_name(self, zone_id, headers):
        """
        Determine the record name relative to the zone.

        Returns the subdomain part, or "@" for zone apex.
        """
        # Get zone info to determine the zone name
        url = f'{self.API_BASE}/zones/{zone_id}'
        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            raise LookupError(f'Zone {zone_id} not found in Hetzner Cloud DNS')
        elif response.status_code == 401:
            raise RuntimeError('Invalid Hetzner Cloud API token')
        elif response.status_code != 200:
            raise RuntimeError(
                f'Failed to get zone info from Hetzner Cloud DNS. '
                f'HTTP Status: {response.status_code}'
            )

        zone_data = response.json()
        zone_name = zone_data['zone']['name']

        # Determine record name
        if self.domain == zone_name:
            return '@'
        elif self.domain.endswith('.' + zone_name):
            return self.domain[:-len(zone_name) - 1]
        else:
            raise RuntimeError(
                f'Domain {self.domain} does not belong to zone {zone_name}'
            )

    def _update_record(self, zone_id, record_name, ip, headers):
        """
        Update an existing A record using the RRSet endpoint.
        """
        url = f'{self.API_BASE}/zones/{zone_id}/records/{record_name}/A'

        data = {
            'ttl': 300,
            'records': [{'value': ip}],
        }

        response = requests.put(url, headers=headers, json=data)

        if response.status_code == 404:
            raise LookupError(f'A record for {self.domain} not found')
        elif response.status_code not in (200, 201):
            error_msg = response.json().get('error', {}).get('message', response.text)
            raise RuntimeError(
                f'Failed to update Hetzner DNS record for {self.domain}. '
                f'HTTP Status: {response.status_code}, Error: {error_msg}'
            )

    def _create_record(self, zone_id, record_name, ip, headers):
        """
        Create a new A record using the RRSet endpoint.
        """
        url = f'{self.API_BASE}/zones/{zone_id}/records'

        data = {
            'name': record_name,
            'type': 'A',
            'ttl': 300,
            'records': [{'value': ip}],
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code not in (200, 201):
            error_msg = response.json().get('error', {}).get('message', response.text)
            raise RuntimeError(
                f'Failed to create Hetzner DNS record for {self.domain}. '
                f'HTTP Status: {response.status_code}, Error: {error_msg}'
            )
