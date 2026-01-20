import requests

from . import DynamicDnsPlugin


class Hetzner(DynamicDnsPlugin):
    """
    Hetzner Cloud DNS plugin using the Cloud API (api.hetzner.cloud/v1).

    This plugin uses the new Hetzner Cloud DNS API integrated into Hetzner Console.
    API tokens can be generated at https://console.hetzner.cloud > Security > API tokens
    """

    API_BASE = 'https://api.hetzner.cloud/v1'

    def update(self, ip):
        """
        Updates an A record in Hetzner Cloud DNS using the RRset API.

        Required config keys:
        - api_token: Hetzner Cloud API token (from Console > Security > API Tokens)

        Optional config keys:
        - zone_id: DNS zone ID (will be auto-discovered from domain if not provided)
        """
        api_token = self.config['api_token']
        zone_id = self.config.get('zone_id')

        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
        }

        # Auto-discover zone_id if not provided
        if not zone_id:
            zone_id = self._find_zone_for_domain(headers)

        # Determine record name relative to zone
        record_name = self._get_record_name(zone_id, headers)

        # Update or create the A record using RRset PUT endpoint
        self._update_rrset(zone_id, record_name, ip, headers)

    def _find_zone_for_domain(self, headers):
        """
        Find the zone ID for the given domain by listing all zones
        and finding the one that matches.
        """
        url = f'{self.API_BASE}/zones'
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise RuntimeError('Invalid Hetzner Cloud API token')
        elif response.status_code != 200:
            raise RuntimeError(
                f'Failed to list zones from Hetzner Cloud DNS. '
                f'HTTP Status: {response.status_code}'
            )

        zones = response.json().get('zones', [])

        # Find the zone that matches the domain
        # Try to find the most specific match (longest zone name)
        best_match = None
        for zone in zones:
            zone_name = zone['name']
            if self.domain == zone_name or self.domain.endswith('.' + zone_name):
                if best_match is None or len(zone_name) > len(best_match['name']):
                    best_match = zone

        if best_match is None:
            raise RuntimeError(
                f'No zone found for domain {self.domain} in Hetzner Cloud DNS'
            )

        return best_match['id']

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

    def _update_rrset(self, zone_id, record_name, ip, headers):
        """
        Update or create an A record using the RRset API.

        PUT /zones/{zone_id}/rrsets/{name}/{type} updates existing record.
        POST /zones/{zone_id}/rrsets creates a new record.
        """
        # First try PUT to update existing record
        url = f'{self.API_BASE}/zones/{zone_id}/rrsets/{record_name}/A'

        data = {
            'ttl': 300,
            'records': [{'value': ip}],
        }

        response = requests.put(url, headers=headers, json=data)

        # If record doesn't exist (404), create it with POST
        if response.status_code == 404:
            url = f'{self.API_BASE}/zones/{zone_id}/rrsets'
            data = {
                'name': record_name,
                'type': 'A',
                'ttl': 300,
                'records': [{'value': ip}],
            }
            response = requests.post(url, headers=headers, json=data)

        if response.status_code not in (200, 201):
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', response.text)
            except Exception:
                error_msg = response.text
            raise RuntimeError(
                f'Failed to update Hetzner DNS record for {self.domain}. '
                f'HTTP Status: {response.status_code}, Error: {error_msg}'
            )
