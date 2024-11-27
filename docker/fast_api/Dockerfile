FROM python:3.9

WORKDIR /code
RUN apt-get update
RUN apt-get install -y nano lsof

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
