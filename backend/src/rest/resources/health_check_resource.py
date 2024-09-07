# src/rest/health_check_resource.py

import os
import structlog
from flask import jsonify
from flask_restful import Resource
from src.custom_exceptions.external_exceptions import HealthCheckError

logger = structlog.get_logger(__name__)


class HealthCheckResource(Resource):
    """
    API resource for health checks.
    """

    def get(self):
        """
        Handle GET requests for health checks.

        Returns
        -------
        Response
            JSON response containing the health status and message.
        """
        missing_vars = []
        critical_vars = ["GENERATOR_CONFIG_FILE", "OPENAI_API_KEY", "RABBITMQ_DEFAULT_USER", "RABBITMQ_DEFAULT_PASS",
                         "RABBITMQ_HOST", "RABBITMQ_PORT",
                         "REDIS_HOST", "REDIS_PORT", "REDIS_PRIMARY_DB_ID"]

        for var in critical_vars:
            if not os.environ.get(var):
                missing_vars.append(var)

        if missing_vars:
            logger.critical(f"Missing critical environment variables", missing_vars=missing_vars)
            raise HealthCheckError(f"Missing critical environment variables: {', '.join(missing_vars)}")
        else:
            health_status = "healthy"
            http_status = 200
            message = "All systems operational"

        response = jsonify({"status": health_status, "message": message})
        response.status_code = http_status
        return response
