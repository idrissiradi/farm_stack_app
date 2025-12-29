# Backend - FastAPI

This is the backend API for the FARM stack learning project, built with FastAPI.

## Purpose

This backend is part of a learning project to understand how to build REST APIs with FastAPI and connect to MongoDB.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **uv** - Fast Python package installer

## Getting Started

### Prerequisites

- Python 3.x
- uv package manager
- MongoDB instance

### Installation & Running

```bash
# Install dependencies
uv sync

# Run the server
uv run main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/                 # Application modules
├── main.py             # Entry point
├── pyproject.toml      # Project dependencies
└── uv.lock             # Lock file
```
