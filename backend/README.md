
## Environment Variables

This project relies on several environment variables to configure different parts of the system. Below is a list of these variables, their purpose, and the possible values they can take.

### General Configuration

| Variable               | Description                                                                 | Possible Values                    |
|------------------------|-----------------------------------------------------------------------------|------------------------------------|
| `ENVIRONMENT`           | Specifies the environment in which the application is running.               | `development`, `production`        |
| `OPENAI_API_KEY`        | API key used to authenticate requests to the OpenAI service.                 | A valid OpenAI API key.            |
| `SECRET_KEY`            | Secret key used for cryptographic operations, such as session management.    | A secure, random string.           |

### RabbitMQ Configuration

| Variable               | Description                                                                 | Possible Values                    |
|------------------------|-----------------------------------------------------------------------------|------------------------------------|
| `RABBITMQ_DEFAULT_USER` | Username for connecting to the RabbitMQ message broker.                      | A valid RabbitMQ username.         |
| `RABBITMQ_DEFAULT_PASS` | Password for the RabbitMQ user.                                              | A valid RabbitMQ password.         |
| `RABBITMQ_PORT`         | Port on which RabbitMQ listens for connections.                              | A valid port number.               |
| `RABBITMQ_HOST`         | Hostname of the RabbitMQ service.                                            | A valid hostname or IP address.    |

### Redis Configuration

| Variable               | Description                                                                 | Possible Values                    |
|------------------------|-----------------------------------------------------------------------------|------------------------------------|
| `REDIS_HOST`           | Hostname of the Redis service.                                               | A valid hostname or IP address.    |
| `REDIS_PORT`           | Port on which Redis listens for connections.                                 | A valid port number.               |
| `REDIS_PRIMARY_DB_ID`  | Redis database ID to use.                                                    | An integer representing the DB ID. |

### Logging Configuration

| Variable               | Description                                                                 | Possible Values                    |
|------------------------|-----------------------------------------------------------------------------|------------------------------------|
| `LOG_LEVEL`            | The logging level for the application.                                       | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

### Application-Specific Configuration

| Variable               | Description                                                                 | Possible Values                    |
|------------------------|-----------------------------------------------------------------------------|------------------------------------|
| `QUIZARD_CONFIG`       | Path to the YAML configuration file for the Quizard application.              | A valid file path.                 |

### How to Set Up Environment Variables

You can set these environment variables by creating a `.env` file in the root directory of the project or by exporting them directly in your shell or CI/CD environment.

For example, to create a `.env` file, you can add:

```
ENVIRONMENT=development
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-secret-key
RABBITMQ_DEFAULT_USER=root_user
RABBITMQ_DEFAULT_PASS=your-rabbitmq-pw
RABBITMQ_PORT=5672
RABBITMQ_HOST=rabbitmq
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PRIMARY_DB_ID=0
LOG_LEVEL=INFO
QUIZARD_CONFIG=quizard_config.yaml
```

**Note on Secrets:**
Make sure to never commit sensitive values like `OPENAI_API_KEY` and `SECRET_KEY` directly to version control. Use a `.env` file for local development and set these variables securely in your production environment.
