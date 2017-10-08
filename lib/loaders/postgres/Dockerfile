FROM postgres:latest

COPY ./loader.sh /tmp/loader.sh
RUN chmod +x /tmp/loader.sh

CMD ["/tmp/loader.sh"]