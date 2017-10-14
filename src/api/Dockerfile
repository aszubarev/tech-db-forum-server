FROM python:slim

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY ./lib/sqlutils /prereqs/sqlutils
WORKDIR /prereqs/sqlutils
RUN python setup.py install

COPY ./lib/apiutils /prereqs/apiutils
WORKDIR /prereqs/apiutils
RUN python setup.py install

RUN rm -rf /prereqs

COPY . /api
WORKDIR /api
RUN python setup.py install
RUN rm -rf /api

RUN pip freeze | grep apiutils
RUN pip freeze | grep sqlutils
RUN pip freeze | grep tech

COPY ./main.py /usr/local/tech_forum_api/main.py
WORKDIR /usr/local/tech_forum_api

ENV CACHE_TYPE simple
ENV DB_NAME forum_server
ENV DB_USER forum_server
ENV DB_PASS forum_server
ENV DB_SERVICE postgres
ENV DB_PORT 5432
ENV SERVER_NAME forum_server
ENV DB_HOST postgres
ENV WEB_PORT 80

CMD /usr/local/bin/gunicorn -w 1 -b :$WEB_PORT main:app