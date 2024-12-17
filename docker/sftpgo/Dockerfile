FROM drakkan/sftpgo:latest

# ENV SFTPGO_HTTPD__WEB_ROOT="/sftp/"

USER root

COPY sftpgo.json /etc/sftpgo/sftpgo.json

RUN apt-get update
RUN apt-get install -y nano lsof curl

USER sftpgo