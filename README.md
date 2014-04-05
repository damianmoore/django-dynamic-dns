django-dynamic-dns
==================

It is common to have a server or NAS on a home network that you would like to be able to occasionally access from other locations across the internet. However, most home internet connections have dynamically-assigned IP addresses which change every few days so you need to use a dynamic DNS service located on a static IP address. This project implements a flexible dynamic DNS service written in Python using the Django web framework.

Machines on dynamic IPs can call this service at regular intervals (e.g. via cron) and when the server notices an address change it makes the relevant API call to update the DNS provider. Alternatively a simple DNS server is included which can be run instead of using an external DNS provider - see the section *Built-in DNS Server* below for more details. You will need your own domain name set with the nameservers to a DNS provider controlled via API or your own instance of the built-in DNS server.

It's recommended that new users check out the `sampleproject` for an example setup.

Domains/subdomains that are going to be managed as aliases to dynamic IP addresses are added to the database through Django's admin interface. The last known IP for a domain is stored against the name so the service knows whether the IP is different from what it was previously. A plugin infrastructure is in place which makes it easy to add new DNS service providers. So far **Rackspace Cloud DNS** and **DigitalOcean** are the only DNS service plugins included but I'd be very happy to receive contributions for other ones.


Server configuration
--------------------

Before adding your domains to the system, you will need to make a couple of additions to Django's `settings.py`. Add `'dynamicdns'` to your `INSTALLED_APPS`. Configure which DNS provider(s) you are going to use along with whatever parameters are required by the plugin.

    INSTALLED_APPS = (
        'django.contrib.admin',
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
    }

Depending on the plugins you use, you may need to install Python dependencies. The file `optional-requirements.txt` lists which requirements are required and running `pip install -r optional-requirements.txt` will install them all.


URL configuration
-----------------

You will need to add the url to your existing urls.py and make you have django admin set up too. This is from the `sampleproject` example:

    url(r'^dynamicdns/', include('dynamicdns.urls')),


Admin configuration
-------------------

Add a new *DnsRecord* in the Django Admin. These are the properties that can be set:
  * **Domain (required):** The domain name that is to be an alias to a dynamic IP - should not contain a dot `.` at the end as in some DNS tools.
  * **IP:** Used for the alias - will get filled in when the scheduled update command runs.
  * **LAN IP:** Only required when using the Built-in DNS server - should be the IP address you use to access it on your internal network e.g. *192.168.x.x* or *10.x.x.x*.
  * **Key:** A secret (like a password) that must be provided when the scheduled job update job is run - leave the field blank and a random one will be generated.
  * **Provider:** Options which were configured in `settings.py` under `DYNAMICDNS_PROVIDERS`. This should be left blank if using the built-in DNS server.
  * **Last change:** Will show when the IP address last changed - leave blank.


Client configuration
--------------------

The easiest way to set up the machine that will be running on a dynamic IP is to create a new cron job (`crontab -e`) that POSTs the domain's secret key to the relevant update URL. This cron line would make sure your machine is not unreachable for more than 15 minutes.

    */15 * * * * curl https://example.com/dynamicdns/update/a.example.com/ --data "key=ZHXPu3RTfs3oAexrwBTi8DGN5lmiH3t1pc9iGG1NZsp75UeM84"

If, for some reason, you want to supply an IP address rather than let the server determine it automatically, you can supply an `ip` parameter like this:

    curl https://example.com/dynamicdns/update/a.example.com/ --data "key=ZHXPu3RTfs3oAexrwBTi8DGN5lmiH3t1pc9iGG1NZsp75UeM84&ip=1.2.3.4"


Security
--------

It is highly recommend that you run the Django project behind a server that supports SSL/TLS with a certificate signed by an authority, otherwise people will be able to override where your domain points. Your client configuration (i.e. curl command) should always use `https://` to begin the URL. Whilst a self-signed certificate can offer protection, you will want to make sure that curl (or alternative) is checking the certificate the server provides against a CA list that includes the fake CA you created. Disabling certificate authority checking or using a library like `urllib` (which doesn't do certificate verification by default) leaves you vulnerable to man-in-the-middle (MITM) attacks.


Built-in DNS Server
-------------------

A simple Python DNS server is included in this package which can be used instead of using an external service. Whilst you would not want to use it for a high-traffic site, it does have it's own advantages.

Unlike any DNS service I know, this server can return an IP address depending on the location of the client requesting a lookup. Say you have a server or some kind of NAS on your home network. Most of the time you access it from within your home and would like to address it at 192.168.1.100 to avoid any looping back of packets to the router or internet, improving speed. By storing the server's LAN address as well as the WAN address of the router, the internal DNS server can identify if a client requesting a lookup is from the same WAN IP and in that case return the LAN address of the server.

This DNS server also has a very small TTL value (1 second) so you shouldn't run in to caching issues - note that a lot of external providers will not let you have a TTL less than approximately 5 minutes.

The built-in DNS server needs to run with suppicient permissions to listen on UDP port 53. If you are using a virtualenv you can use a combination of `sudo` and specifying which `python` to use.

    sudo /PATH/TO/VIRTUALENV/bin/python manage.py run_dns_server

When testing this out it is useful to learn a few `dig` commands. This will perform a basic lookup of a domain using your local built-in DNS server:

    dig @127.0.0.1 a.example.com.

You should get a response similar to the following. Note the `ANSWER SECTION` in the response should show the domain name with the IP address.

    ; <<>> DiG 0.0.0 <<>> @127.0.0.1 a.example.com.
    ; (1 server found)
    ;; global options: +cmd
    ;; Got answer:
    ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 8559
    ;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

    ;; OPT PSEUDOSECTION:
    ; EDNS: version: 0, flags:; udp: 4096
    ;; QUESTION SECTION:
    ;a.example.com.  IN  A

    ;; ANSWER SECTION:
    a.example.com.  1  IN  A  192.168.1.100

    ;; Query time: 1 msec
    ;; SERVER: 127.0.0.1#53(127.0.0.1)
    ;; WHEN: Wed Jan 15 23:50:01 GMT 2014
    ;; MSG SIZE  rcvd: 69

You're most likely going to want to bind subdomains to your instance of the built-in DNS server using `NS` records. I found that delegating a subdomain to a different nameserver on Rackspace Cloud DNS was a bit tricky as the user interface on their control panel doesn't allow you to do it. This tutorial showed it was possible on Rackspace using their API: http://wherenow.org/delegating-a-subdomain-with-rackspace-cloud-dns/


DNS Debugging
-------------

Here's a few quick `dig` commands that are helpful for getting things working.

Check a domain is managed by intended name servers:

    dig +short NS a.example.com.

Check a domain has an alias and points to a certain IP address:

    dig +short A a.example.com.

Show all other DNS info for a domain:

    dig a.example.com.

Query a specific DNS server like `127.0.0.1` for the in-built server or `8.8.8.8` for Google's servers by using `@` and then a DNS IP:

    dig @127.0.0.1 a.example.com.


Future features
---------------

  * Adding more DNS provider plugins
  * Support for DNSSEC in the built-in DNS server
