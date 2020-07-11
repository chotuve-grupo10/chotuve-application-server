#!/bin/bash

datadog-agent run &
/opt/datadog-agent/embedded/bin/trace-agent --config=/etc/datadog-agent/datadog.yaml &
/opt/datadog-agent/embedded/bin/process-agent --config=/etc/datadog-agent/datadog.yaml &
gunicorn --log-level=debug --statsd-host=localhost:8125 --name=chotuve-app-server 'app_server:create_app()'