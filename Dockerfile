FROM python:alpine3.7
COPY . .
RUN pip install --upgrade pip
RUN pip install -e .
EXPOSE 5000
ENV FLASK_APP=app_server
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
CMD flask run