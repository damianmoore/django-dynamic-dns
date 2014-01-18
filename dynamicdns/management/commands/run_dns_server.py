# Inspired by http://code.activestate.com/recipes/491264-mini-fake-dns-server/

import socket

from django.core.management.base import NoArgsCommand

from dynamicdns.models import DnsRecord


class Command(NoArgsCommand):
    help = 'Runs the built-in DNS server'

    def handle(self, **options):

        print 'django-dynamic-dns built-in dns server'

        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.bind(('', 53))

        try:
            while True:
                data, addr = udps.recvfrom(1024)
                p = DnsQuery(data)
                try:
                    dns_record = DnsRecord.objects.get(domain=p.domain.rstrip('.'))
                    if dns_record.lan_ip and addr == dns_record.ip:
                        ip = dns_record.lan_ip
                    else:
                        ip = dns_record.ip
                except DnsRecord.DoesNotExist:
                    ip = None
                udps.sendto(p.answer(ip), addr)
                print 'Answer: %s -> %s' % (p.domain, ip)
        except KeyboardInterrupt:
            print 'Finished.'
            udps.close()


class DnsQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''

        tipo = (ord(data[2]) >> 3) & 15   # Opcode bits
        if tipo == 0:                     # Standard query
            ini = 12
            lon = ord(data[ini])
            while lon != 0:
                self.domain += data[ini + 1:ini + lon + 1] + '.'
                ini += lon + 1
                lon = ord(data[ini])

    def answer(self, ip):
        packet = []
        if self.domain and ip:
            packet += self.data[:2]                                             # Transaction ID
            packet += '\x81\x80'                                                # Flags: Standard query response, No error
            packet += self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x01'      # Question and Answer Counts
            packet += self.data[12:].split('\x00\x00\x29')[0]                   # Original Domain Name Question
            packet += '\xc0\x0c'                                                # Pointer to domain name
            packet += '\x00\x01'                                                # Type: A
            packet += '\x00\x01'                                                # Class: IN
            packet += '\x00\x00\x00\x01'                                        # TTL: 1 second
            packet += '\x00\x04'                                                # Data length: 4 bytes
            packet += ''.join(map(lambda x: chr(int(x)), ip.split('.')))        # 4 bytes of IP
            packet += '\x00\x00\x29'                                            # Additional record <Root>: type OPT
            packet += self.data[12:].split('\x00\x00\x29')[1]
        if not ip:
            packet += self.data[:2] + '\x81\x80'
            packet += self.data[4:6] + '\x00\x00' + '\x00\x00\x00\x00'          # Question and Answer Counts
            packet += self.data[12:]                                            # Original Domain Name Question
            packet += '\xc0\x0c'                                                # Pointer to domain name
        return ''.join(packet)
