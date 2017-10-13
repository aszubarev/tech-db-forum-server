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

CMD echo "HELLO NEW"