# Inspired by http://code.activestate.com/recipes/491264-mini-fake-dns-server/

import socket

from django.core.management.base import BaseCommand

from dynamicdns.models import DnsRecord


class Command(BaseCommand):
    help = 'Runs the built-in DNS server'

    def handle(self, **options):
        print('django-dynamic-dns built-in dns server')

        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.bind(('', 53))

        try:
            while True:
                data, addr = udps.recvfrom(1024)
                p = DnsQuery(data)
                try:
                    dns_record = DnsRecord.objects.get(domain=p.domain.rstrip('.'))
                    if dns_record.lan_ip and addr[0] == dns_record.ip:
                        ip = dns_record.lan_ip
                    else:
                        ip = dns_record.ip
                except DnsRecord.DoesNotExist:
                    ip = None
                udps.sendto(p.answer(ip), addr)
                print(f'Answer: {p.domain} -> {ip}')
        except KeyboardInterrupt:
            print('Finished')
            udps.close()


class DnsQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''

        tipo = int(data[2]) >> 3    # Opcode bits (what type of query we received)
        if tipo == 0:               # Standard query
            ini = 12
            lon = int(data[ini])
            while lon != 0:
                self.domain += data[ini + 1:ini + lon + 1].decode('utf-8') + '.'
                ini += lon + 1
                lon = int(data[ini])

    def answer(self, ip):
        packet = b''
        if self.domain and ip:
            packet += self.data[:2]                                                     # Transaction ID
            packet += b'\x81\x80'                                                       # Flags: Standard query response, No error
            packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'             # Question and Answer Counts
            packet += self.data[12:].split(b'\x00\x00\x29')[0]                          # Original Domain Name Question
            packet += b'\xc0\x0c'                                                       # Pointer to domain name
            packet += b'\x00\x01'                                                       # Type: A
            packet += b'\x00\x01'                                                       # Class: IN
            packet += b'\x00\x00\x00\x3c'                                               # TTL: 60 seconds
            packet += b'\x00\x04'                                                       # Data length: 4 bytes
            packet += b''.join(list(map(lambda x: bytes([int(x)]), ip.split('.'))))     # 4 bytes of IP
            packet += b'\x00\x00\x29\x05\xac\x00\x00\x00\x00\x00\x00'                   # Remaining bytes
        if not ip:
            packet += self.data[:2] + b'\x81\x80'
            packet += self.data[4:6] + b'\x00\x00' + b'\x00\x00\x00\x00'                # Question and Answer Counts
            packet += self.data[12:]                                                    # Original Domain Name Question
            packet += b'\xc0\x0c'                                                       # Pointer to domain name
        return packet
