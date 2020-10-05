import importlib

from django.conf import settings


def update_dns_record(dns_record, ip):
    if dns_record.provider:
        config = settings.DYNAMICDNS_PROVIDERS[dns_record.provider]
        mod_path, mod_name = config['plugin'].rsplit('.', 1)
        DnsPlugin = getattr(importlib.import_module(mod_path, package=mod_name), mod_name)
        dns_plugin = DnsPlugin(dns_record.domain, config)
        dns_plugin.update(ip)
