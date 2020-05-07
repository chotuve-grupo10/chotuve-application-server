FROM python:alpine3.7
COPY setup.py setup.py
RUN pip install --upgrade pip
RUN pip install -e .
EXPOSE 5000
COPY . .
CMD flask run