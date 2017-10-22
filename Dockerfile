FROM ubuntu:17.04

MAINTAINER ZubarevAnton

ENV PGVER 10

ENV DB_HOST 127.0.0.1
ENV DB_PORT 54545
ENV DB_NAME forum_server
ENV DB_USER forum_server
ENV DB_PASS forum_server
ENV DATABASE /tmp/database

ENV CACHE_TYPE simple
ENV DB_SERVICE postgres
ENV SERVER_NAME forum_server
ENV WEB_PORT 80


########################################################################################################################
# install postgres
RUN echo "try install"
RUN apt-get -qq update -y
RUN apt-get install wget -y
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ zesty-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
RUN apt-get -y update

RUN apt-get install -y postgresql-$PGVER

USER postgres
RUN echo "local all all trust" >> /var/lib/postgresql/$PGVER/main/pg_hba.conf
RUN echo "host  all all 127.0.0.1/32 trust	" >> /var/lib/postgresql/$PGVER/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /var/lib/postgresql/$PGVER/main/postgresql.conf


RUN /usr/lib/postgresql/$PGVER/bin/pg_ctl -o "-p ${DB_PORT}" -D /var/lib/postgresql/$PGVER/main restart
RUN ps -aux | grep postgre


USER root

USER root
########################################################################################################################
COPY ./src/database $DATABASE
COPY ./lib/loader/database_loader /loader
WORKDIR /loader
RUN bash create_db.sh $DB_HOST $DB_PORT $DB_NAME $DB_USER $DB_PASS $DATABASE
########################################################################################################################

COPY ./src/api/requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY ./src/api/lib/sqlutils /prereqs/sqlutils
WORKDIR /prereqs/sqlutils
RUN python setup.py install

COPY ./src/api/lib/apiutils /prereqs/apiutils
WORKDIR /prereqs/apiutils
RUN python setup.py install

RUN rm -rf /prereqs

COPY ./src/api /api
WORKDIR /api
RUN python setup.py install
RUN rm -rf /api

RUN pip freeze | grep apiutils
RUN pip freeze | grep sqlutils
RUN pip freeze | grep tech

COPY ./src/api/main.py /usr/local/tech_forum_api/main.py
WORKDIR /usr/local/tech_forum_api

EXPOSE 5000
CMD /usr/local/bin/gunicorn -w 1 -b :$WEB_PORT main:app