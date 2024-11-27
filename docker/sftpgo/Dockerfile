FROM drakkan/sftpgo:latest

ENV SFTPGO_HTTPD__WEB_ROOT="/sftp/"

USER root

RUN apt-get update
RUN apt-get install -y nano lsof curl

USER sftpgo