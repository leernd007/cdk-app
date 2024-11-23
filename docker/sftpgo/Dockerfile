FROM drakkan/sftpgo:latest

ENV SFTPGO_HTTPD__WEB_ROOT="/sftp/"

USER root

RUN apt-get update
RUN apt-get install -y nano lsof curl
#
# RUN chown -R 1100:1100 /etc/sftpgo && chown 1100:1100 /var/lib/sftpgo /srv/sftpgo
USER sftpgo