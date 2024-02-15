# TODO: Optimize build (commented code -> implementations of speed up steps 1-4, see Quizard-Notion/Docker-Poetry)

# Use an official Python runtime as a parent image
FROM python:3.12-slim as base

# SETUP ENV
# Set the locale correctly
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
# Stop Python from generating `.pyc` files
ENV PYTHONDONTWRITEBYTECODE 1
# Enable Python tracebacks on segfaults
ENV PYTHONFAULTHANDLER 1

# Create isolated Poetry environment in Docker container
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install pipenv and compilation dependencies
RUN pip install poetry==1.7.1

# Set the working directory in the container
WORKDIR /app
RUN touch README.md
# Copy the Poetry installation files into the container
COPY pyproject.toml poetry.lock* ./

## Create a non-root user and add permission to access the /app folder (deployment security best practice)
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Install dependencies and clearing useless Poetry cache
# --no-local_dev: Don't install development dependencies (useless, only slow down installation)
# --no-root: Don't install project and build venv with minimal information instead. Install project only after installing dependencies.
# -> In the default Dockerfile setup COPY is called before the dependencies are installed. However, changes to the codebase will invalidate the COPY
#    command. Because of the way Docker layer caching workds, this the subsequent layers will also be rebuild - reinstalling the dependencies each
#    time resulting in long builds. For this reason, we first install all dependencies with minimal information, then copy the source code and then
#    install the project.
RUN poetry install --no-root --no-dev && rm -rf $POETRY_CACHE_DIR

# Copy the backend directory contents into the container at /app
COPY . .

# Now install project into virtual environment
RUN poetry install --no-dev

# Run flashcard_service.py when the container launches
ENTRYPOINT ["poetry", "run"]
CMD ["python", "-m", "src.rest.app"]