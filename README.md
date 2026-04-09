 Green Financing Project

[![CI/CD Status](https://github.com/Mehdi-BenZaied/Green-Financing-Project/actions/workflows/main.yml/badge.svg)](https://github.com/Mehdi-BenZaied/Green-Financing-Project/actions)

A modern full-stack application for green financing solutions built with Angular and FastAPI.

 Features

- **Frontend**: Angular 16 with modern UI components
- **Backend**: FastAPI with Python 3.11
- **Deployment**: Docker containerization
- **CI/CD**: Automated testing and deployment

 🔧 Development
 Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

 Quick Start
```bash
# Clone the repository
git clone https://github.com/Mehdi-BenZaied/Green-Financing-Project.git
cd Green-Financing-Project

# Start with Docker
docker-compose up -d

# Or run manually
npm install && npm start  # Frontend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload  # Backend
