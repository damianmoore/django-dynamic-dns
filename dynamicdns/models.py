from datetime import datetime
import string
import random

from django.conf import settings
from django.db import models

from .utils import update_dns_record


PROVIDER_CHOICES = [(name, name) for name in settings.DYNAMICDNS_PROVIDERS.keys()]


class DnsRecord(models.Model):
    domain = models.CharField(max_length=50, unique=True, help_text='Domain/subdomain name')
    ip = models.CharField(max_length=16, blank=True)
    lan_ip = models.CharField(max_length=16, blank=True, help_text='Only required when using the internal DNS server as a provider')
    key = models.CharField(max_length=50, blank=True, help_text='Optional - Autogenerated if left blank')
    provider = models.CharField(max_length=25, choices=PROVIDER_CHOICES, blank=True)
    last_change = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.domain

    def generate_key(self, size=50, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    def save(self):
        if not self.key:
            self.key = self.generate_key()
        update_dns_record(self, self.ip)
        self.last_change = datetime.now()
        super(DnsRecord, self).save()
