import requests

from . import DynamicDnsPlugin


class Hetzner(DynamicDnsPlugin):
    """
    Hetzner DNS plugin using the Hetzner Cloud API (api.hetzner.cloud/v1).

    DNS is managed via Hetzner Cloud Console (console.hetzner.com).
    API tokens can be generated at console.hetzner.com under API Tokens.
    """

    API_BASE = 'https://api.hetzner.cloud/v1'

    def update(self, ip):
        """
        Updates an A record in Hetzner Cloud DNS.

        Required config keys:
        - api_token: Hetzner Cloud API token

        Optional config keys:
        - zone_id: DNS zone ID (will be auto-discovered from domain if not provided)
        """
        api_token = self.config['api_token']
        zone_id = self.config.get('zone_id')

        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
        }

        if not zone_id:
            zone_id = self._find_zone_for_domain(headers)

        zone_name = self._get_zone_name(zone_id, headers)
        record_name = self._extract_record_name(zone_name)
        self._upsert_rrset(zone_id, record_name, ip, headers)

    def _find_zone_for_domain(self, headers):
        response = requests.get(f'{self.API_BASE}/zones', headers=headers)

        if response.status_code == 401:
            raise RuntimeError('Invalid Hetzner Cloud API token')
        elif response.status_code != 200:
            raise RuntimeError(
                f'Failed to list Hetzner Cloud DNS zones. HTTP Status: {response.status_code}'
            )

        zones = response.json().get('zones', [])
        best_match = None
        for zone in zones:
            zone_name = zone['name']
            if self.domain == zone_name or self.domain.endswith('.' + zone_name):
                if best_match is None or len(zone_name) > len(best_match['name']):
                    best_match = zone

        if best_match is None:
            raise RuntimeError(f'No Hetzner Cloud DNS zone found for domain {self.domain}')

        return best_match['id']

    def _get_zone_name(self, zone_id, headers):
        response = requests.get(f'{self.API_BASE}/zones/{zone_id}', headers=headers)

        if response.status_code == 404:
            raise LookupError(f'Hetzner Cloud DNS zone {zone_id} not found')
        elif response.status_code == 401:
            raise RuntimeError('Invalid Hetzner Cloud API token')
        elif response.status_code != 200:
            raise RuntimeError(
                f'Failed to get zone info. HTTP Status: {response.status_code}'
            )

        return response.json()['zone']['name']

    def _extract_record_name(self, zone_name):
        if self.domain == zone_name:
            return '@'
        if self.domain.endswith('.' + zone_name):
            return self.domain[:-len(zone_name) - 1]
        raise RuntimeError(f'Domain {self.domain} does not belong to zone {zone_name}')

    def _upsert_rrset(self, zone_id, record_name, ip, headers):
        """
        Update records in an existing RRset, or create the RRset if it doesn't exist.

        PUT /zones/{id}/rrsets/{name}/{type} updates RRset properties (TTL, protection) only.
        POST .../actions/set_records replaces the record values within an RRset.
        POST /zones/{id}/rrsets creates a new RRset.
        """
        url = f'{self.API_BASE}/zones/{zone_id}/rrsets/{record_name}/A/actions/set_records'
        data = {'records': [{'value': ip}]}
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 404:
            # RRset doesn't exist yet — create it
            url = f'{self.API_BASE}/zones/{zone_id}/rrsets'
            data = {
                'name': record_name,
                'type': 'A',
                'ttl': 60,
                'records': [{'value': ip}],
            }
            response = requests.post(url, headers=headers, json=data)

        if response.status_code not in (200, 201):
            try:
                error_msg = response.json().get('error', {}).get('message', response.text)
            except Exception:
                error_msg = response.text
            raise RuntimeError(
                f'Failed to update Hetzner Cloud DNS record for {self.domain}. '
                f'HTTP Status: {response.status_code}, Error: {error_msg}'
            )
