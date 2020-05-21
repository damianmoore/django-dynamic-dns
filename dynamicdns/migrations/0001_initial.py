# Generated by Django 3.0.6 on 2020-05-21 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DnsRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(help_text='Domain/subdomain name', max_length=50, unique=True)),
                ('ip', models.CharField(blank=True, max_length=16)),
                ('lan_ip', models.CharField(blank=True, help_text='Only required when using the internal DNS server as a provider', max_length=16)),
                ('key', models.CharField(blank=True, help_text='Optional - Autogenerated if left blank', max_length=50)),
                ('provider', models.CharField(blank=True, choices=[('dummy', 'dummy'), ('rackspace', 'rackspace'), ('digitalocean', 'digitalocean')], max_length=25)),
                ('last_change', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'DNS Record',
            },
        ),
    ]
