FROM python:3.11
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY / /code/app
WORKDIR /code/app
CMD python manage.py runserver 0.0.0.0:80

