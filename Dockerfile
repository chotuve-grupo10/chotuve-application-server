FROM python:alpine3.7
COPY . .
RUN pip install --upgrade pip
RUN pip install -e .
EXPOSE 8000
CMD gunicorn 'app_server:create_app()'