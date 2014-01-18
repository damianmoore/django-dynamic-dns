from django.conf import settings


def update_dns_record(dns_record, ip):
    if dns_record.provider:
        config = settings.DYNAMICDNS_PROVIDERS[dns_record.provider]
        mod_path, mod_name = config['plugin'].rsplit('.', 1)
        exec('from {} import {} as DnsPlugin'.format(mod_path, mod_name))
        dns_plugin = DnsPlugin(dns_record.domain, config)
        dns_plugin.update(ip)