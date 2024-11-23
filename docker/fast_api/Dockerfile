FROM python:3.9

WORKDIR /code
RUN apt-get update
RUN apt-get install -y nano lsof
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./ /code

CMD ["fastapi", "run", "new/main.py", "--port", "80"]
