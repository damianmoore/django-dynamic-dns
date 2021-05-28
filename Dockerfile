FROM python:3.8-slim-buster

RUN apt-get update -yq \
    && apt-get install -yq \
        git \
        build-essential \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/*

RUN pip install Django==3.0.6 psycopg2-binary supervisor gunicorn
# RUN pip install django-dynamic-dns
COPY requirements.txt /srv
RUN pip install -r /srv/requirements.txt

COPY ./dynamicdns /srv/dynamicdns
COPY setup.py /srv/setup.py
WORKDIR /srv
RUN python setup.py install

COPY ./standalone /srv/standalone

WORKDIR /srv/standalone
# RUN python /srv/standalone/manage.py collectstatic --link --noinput

CMD ./run.sh

EXPOSE 80
