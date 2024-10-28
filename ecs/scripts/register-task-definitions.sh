#!/bin/bash

set -e

# Register all task definitions
aws ecs register-task-definition --cli-input-json file://ecs/task-definitions/compliance-api-v2/task-definition.json
aws ecs register-task-definition --cli-input-json file://ecs/task-definitions/compliance-api-v2-celery/task-definition.json
aws ecs register-task-definition --cli-input-json file://ecs/task-definitions/redis/task-definition.json
aws ecs register-task-definition --cli-input-json file://ecs/task-definitions/rabbitmq/task-definition.json
aws ecs register-task-definition --cli-input-json file://ecs/task-definitions/postgresql/task-definition.json
