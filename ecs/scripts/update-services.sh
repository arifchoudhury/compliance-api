#!/bin/bash

set -e

CLUSTER_NAME="compliance-cluster"

# Update ECS services
aws ecs update-service --cluster $CLUSTER_NAME --service compliance-api-v2-service --task-definition compliance-api-v2
aws ecs update-service --cluster $CLUSTER_NAME --service compliance-api-v2-celery-service --task-definition compliance-api-v2-celery
aws ecs update-service --cluster $CLUSTER_NAME --service redis-service --task-definition redis
aws ecs update-service --cluster $CLUSTER_NAME --service rabbitmq-service --task-definition rabbitmq
aws ecs update-service --cluster $CLUSTER_NAME --service postgresql-service --task-definition postgresql
