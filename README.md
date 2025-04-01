# Travel Planning Telegram Bot

This project is an MVP of a Telegram bot for generating travel itineraries using AI. It was developed as a final project for the OTUS Basic course.

## Description
- Generate travel itineraries via an external AI API.
- Collaborative itinerary editing.
- Export itineraries to PDF.
- Request caching for optimization.

## Technology Stack
- **Backend**: FastAPI (asynchronous web framework).
- **Database**: PostgreSQL + SQLAlchemy (ORM).
- **Caching**: Redis.
- **Telegram Bot**: Aiogram.
- **Containerization**: Docker.

## Installation and Setup
1. Install [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/).
2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd travel-bot