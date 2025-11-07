# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django Dynamic DNS is a flexible dynamic DNS service written in Python using Django. It allows machines on dynamic IPs to call the service at regular intervals, and when an IP address change is detected, it updates the DNS provider via API. The project includes a built-in DNS server as an alternative to external DNS providers.

## Key Architecture

### Plugin System

The project uses a plugin architecture for DNS providers located in `dynamicdns/plugins/`:

- **Base class**: `DynamicDnsPlugin` in [dynamicdns/plugins/__init__.py](dynamicdns/plugins/__init__.py) defines the interface
- **Plugin loading**: [dynamicdns/utils.py](dynamicdns/utils.py) `update_dns_record()` function dynamically imports and instantiates plugins using `importlib`
- **Available plugins**: Dummy (testing), Rackspace, DigitalOcean, AWS Route53
- Each plugin receives `domain` and `config` (from settings) and implements `update(ip)` method

### DNS Update Flow

1. Client POSTs to `/dynamicdns/update/<domain>/` with secret key
2. [dynamicdns/views.py](dynamicdns/views.py) `dynamic_dns_update()` validates the key and determines IP
3. If IP changed, `DnsRecord.save()` in [dynamicdns/models.py](dynamicdns/models.py) is called
4. Model's `save()` method calls `update_dns_record()` which loads the appropriate plugin
5. Plugin makes external API call to update DNS provider

### Built-in DNS Server

[dynamicdns/management/commands/run_dns_server.py](dynamicdns/management/commands/run_dns_server.py) implements a minimal DNS server:

- Listens on UDP port 53
- Queries `DnsRecord` model for domain lookups
- Has smart LAN/WAN IP routing: returns `lan_ip` if requester matches the domain's WAN IP
- Uses 60-second TTL for fast updates
- Runs as Django management command: `python manage.py run_dns_server`

### Project Configurations

Two example configurations are provided:

- **sampleproject/**: Minimal Django project for integrating into existing Django apps
- **standalone/**: Docker-ready standalone deployment with PostgreSQL support and environment-based configuration

The standalone version supports both SQLite and PostgreSQL, with database selection based on `POSTGRES_HOST` environment variable.

## Development Commands

### Setting up development environment

```bash
# Install package in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt

# Run with sample project
cd sampleproject
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Run with standalone project
cd standalone
python manage.py migrate
python manage.py runserver
```

### Testing DNS server locally

```bash
# Run DNS server (requires root/sudo for port 53)
sudo python manage.py run_dns_server

# Test with dig
dig @127.0.0.1 a.example.com.
```

### Docker deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Access at http://localhost:8008
# DNS server available on UDP port 8053
```

### Database migrations

```bash
python manage.py makemigrations dynamicdns
python manage.py migrate
```

## Configuration

### Required settings.py additions

```python
INSTALLED_APPS = (
    ...
    'dynamicdns',
)

DYNAMICDNS_PROVIDERS = {
    'dummy': {
        'plugin': 'dynamicdns.plugins.Dummy',
    },
    'rackspace': {
        'plugin': 'dynamicdns.plugins.Rackspace',
        'username': 'YOUR_USERNAME',
        'api_key': 'YOUR_API_KEY',
    },
    'digitalocean': {
        'plugin': 'dynamicdns.plugins.DigitalOcean',
        'client_id': 'YOUR_CLIENT_ID',
        'api_key': 'YOUR_API_KEY',
    },
    'aws': {
        'plugin': 'dynamicdns.plugins.AWS',
        'aws_access_key_id': 'YOUR_AWS_ACCESS_KEY_ID',
        'aws_secret_access_key': 'YOUR_AWS_SECRET_ACCESS_KEY',
        'aws_region': 'us-east-1',  # Optional, defaults to us-east-1
        'hosted_zone_id': 'YOUR_HOSTED_ZONE_ID',
    },
}
```

### Environment variable configuration (standalone/Docker)

The standalone project supports configuring DNS providers via environment variables:

- **AWS Route53**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` (optional, defaults to us-east-1), `AWS_HOSTED_ZONE_ID`
- **Rackspace**: `RACKSPACE_USERNAME`, `RACKSPACE_API_KEY`
- **DigitalOcean**: `DIGITALOCEAN_CLIENT_ID`, `DIGITALOCEAN_API_KEY`

Make sure to update `.env.example` whenever new environment variables are used in the project.

### URLs configuration

Add to project's urls.py:
```python
path('dynamicdns/', include('dynamicdns.urls')),
```

## Creating New DNS Provider Plugins

1. Create new file in `dynamicdns/plugins/`
2. Inherit from `DynamicDnsPlugin` base class
3. Implement `update(self, ip)` method
4. Import in `dynamicdns/plugins/__init__.py`
5. Add configuration to `DYNAMICDNS_PROVIDERS` in settings

Example structure:
```python
from . import DynamicDnsPlugin

class NewProvider(DynamicDnsPlugin):
    def update(self, ip):
        # Make API call to update DNS record
        # Access self.domain and self.config
        pass
```

## Security Considerations

- Always use HTTPS in production to prevent MITM attacks
- Secret keys are auto-generated for each DNS record if not provided
- Basic rate-limiting (2-second delay) on authentication failures
- Domain existence is not revealed on authentication failures
- IP detection uses `HTTP_X_FORWARDED_FOR` or `REMOTE_ADDR` headers

## API Endpoints

- `GET /dynamicdns/read/<domain>/` - Read current IP for domain (returns JSON)
- `POST /dynamicdns/update/<domain>/` - Update domain IP with `key` parameter and optional `ip` parameter
