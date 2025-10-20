# QCoder Project Context Example

Copy this file to QCODER.md and customize for your project.

## Project Description

Describe your project here. This context will be provided to the AI in every conversation.

Example:
- **Name**: My Awesome Project
- **Type**: Web Application
- **Stack**: React + FastAPI + PostgreSQL
- **Purpose**: [Brief description of what the project does]

## Architecture

Describe the high-level architecture:

- **Frontend**: React with TypeScript, using Material-UI
- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL
- **Deployment**: Docker containers on AWS

## Coding Standards

List coding standards and conventions:

### Python
- Follow PEP 8 style guide
- Use type hints for all functions
- Minimum test coverage: 80%
- Docstrings required for all public functions

### JavaScript/TypeScript
- Use ESLint with Airbnb config
- Prefer functional components and hooks
- PropTypes or TypeScript interfaces required
- Jest for unit tests

### Git Workflow
- Feature branches from `develop`
- PR reviews required before merge
- Conventional commit messages
- Squash commits when merging

## Directory Structure

```
project/
├── frontend/          # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   └── tests/
├── backend/           # FastAPI application
│   ├── api/
│   ├── models/
│   ├── services/
│   └── tests/
└── docs/              # Documentation
```

## Important Files

- `backend/api/routes/` - API endpoint definitions
- `backend/models/` - Database models
- `frontend/src/components/` - Reusable React components
- `docker-compose.yml` - Local development environment

## Common Tasks

### Starting Development Server

```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend
cd frontend && npm start
```

### Running Tests

```bash
# Backend
pytest backend/tests/

# Frontend
cd frontend && npm test
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Important Notes

- Always run tests before committing
- Database credentials are in `.env` (never commit this file)
- API documentation available at `/docs` when server is running
- Use feature flags for experimental features

## Dependencies

### Backend
- FastAPI >= 0.104.0
- SQLAlchemy >= 2.0.0
- Pydantic >= 2.0.0

### Frontend
- React >= 18.0.0
- Material-UI >= 5.14.0
- React Router >= 6.16.0

## Team Conventions

- Code reviews within 24 hours
- Standup meetings: Daily at 10 AM
- Sprint planning: Every 2 weeks
- Documentation: Update docs/ when adding features

## External Resources

- [API Documentation](https://api.example.com/docs)
- [Design System](https://design.example.com)
- [Deployment Guide](https://docs.example.com/deploy)
