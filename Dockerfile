FROM python:alpine3.7
COPY . .
RUN pip install -e .
RUN export FLASK_APP=app_server && export FLASK_ENV=development && FLASK_RUN_PORT=3000
EXPOSE 3000
CMD flask run