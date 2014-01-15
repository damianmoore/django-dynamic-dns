from django.contrib import admin
from models import DnsRecord


class DnsRecordAdmin(admin.ModelAdmin):
    list_display = ('domain', 'ip', 'key', 'provider', 'last_change',)
    ordering = ('domain',)
    list_filter = ('provider', 'last_change')

admin.site.register(DnsRecord, DnsRecordAdmin)
