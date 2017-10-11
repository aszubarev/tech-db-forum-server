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

RUN pip freeze | grep apiutils
RUN pip freeze | grep sqlutils

CMD pip freeze | grep apiutils