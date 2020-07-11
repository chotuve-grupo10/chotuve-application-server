FROM python:3

# Install GPG dependencies
RUN apt-get update \
 && apt-get install -y gpg apt-transport-https gpg-agent curl ca-certificates
# Add Datadog repository and signing key
RUN sh -c "echo 'deb https://apt.datadoghq.com/ stable 7' > /etc/apt/sources.list.d/datadog.list"
RUN apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 A2923DFF56EDA6E76E55E492D3A80E30382E94DE
# Install the Datadog agent
RUN apt-get update && apt-get -y --force-yes install --reinstall datadog-agent
# Expose DogStatsD and trace-agent ports
EXPOSE 8125/udp 8126/tcp
# Copy your Datadog configuration
COPY datadog-config/ /etc/datadog-agent/

COPY requirements.txt .
COPY setup.py .
RUN pip install --upgrade pip
RUN pip install -e .
RUN pip install -r requirements.txt
ENV DATABASE_URL="mongodb+srv://taller2:taller2@appserver-6nnmq.mongodb.net/test"
ENV APP_SERVER_TOKEN_FOR_AUTH_SERVER='c0f426f1-f3a6-45aa-b452-61a5112591b3'
ENV APP_SERVER_TOKEN_FOR_MEDIA_SERVER='6a3fe107-255e-43f0-9819-386c4f32c41f'
ENV FIREBASE_SERVER_KEY='AAAAVKWePyU:APA91bEXDvxMY3Xk41S67G1Dnc-1SiybDAoqthftsHWql-IAWS-rSm_jQIJ9wS52-ecU7TNNHrhfCnYE7HEOUfae0qvN7EPIaAeS9riVVmnvtxk4NCDd6Qlt1npAimIlIADqNUOtVjwQ'
COPY . .
EXPOSE 8000

CMD ["/entrypoint.sh"]