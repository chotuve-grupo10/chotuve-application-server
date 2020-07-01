FROM python:3
COPY requirements.txt .
COPY setup.py .
RUN pip install --upgrade pip
RUN pip install -e .
RUN pip install -r requirements.txt
ENV DATABASE_URL="mongodb+srv://taller2:taller2@appserver-6nnmq.mongodb.net/test"
ENV APP_SERVER_TOKEN_FOR_AUTH_SERVER='c0f426f1-f3a6-45aa-b452-61a5112591b3'
ENV APP_SERVER_TOKEN_FOR_MEDIA_SERVER='6a3fe107-255e-43f0-9819-386c4f32c41f'
COPY . .
EXPOSE 8000
CMD gunicorn --log-level=debug 'app_server:create_app()'