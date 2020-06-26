FROM python:3
COPY requirements.txt .
COPY setup.py .
RUN pip install --upgrade pip
RUN pip install -e .
RUN pip install -r requirements.txt
ENV DATABASE_URL="mongodb+srv://taller2:taller2@appserver-6nnmq.mongodb.net/test"
COPY . .
EXPOSE 8000
CMD gunicorn --log-level=debug 'app_server:create_app()'