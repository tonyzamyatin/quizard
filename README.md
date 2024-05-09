# Quizard

## Overview
Active recall and spaced repetition are shown to be THE most effective studying techniques. Therefore, bite-sized learning with flashcards (popularized by apps like Anki) 
is a great learning approach...if it was not for the tedious and timeconsuming task of writing every flashcard yourself, and that fact that you are somewhat taking away the 
suprise effect if you know the answer in advance.

Using ready flashcards from the internet generally doesn’t do the job either since they usually differ in content, even if the topic is the same.

This is why we built Quizard™ — an AI powered flashcard generator. It tailors flashcards to your needs and exports them to your favorite flashcard learning app.
Currently, is is still a proof of concept and a playground for testing various features.

## Setup Instructions
### Prerequisites
- Python 3.12+
- Docker
- Node.js 14+

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/tonyzamyatin/Quizard.git
    cd Quizard
    ```
2. Build and run the application using Docker Compose:
    ```bash
    docker-compose up --build
    ```

## Configuration
Environment variables:
- `FLASK_ENV`: Flask environment (`development`, `production`).
- `OPENAI_API_KEY`: public key to access OpenAI API
- `SECRET_KEY`: secret key to access OpenAI API

## API Documentation
Refer to [API Documentation](docs/API.md).

## Testing
1. Backend Tests:
    ```bash
    pytest
    ```
2. Frontend Tests:
    ```bash
    npm test
    ```

## Deployment Guide
Refer to docker-compose.yml
1. Build Docker image:
    ```bash
    docker build -t quizard-app:latest .
    ```
2. Run Docker container:
    ```bash
    docker run -p 5000:5000 quizard-app:latest
    ```
