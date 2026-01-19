# FastAPI + Ollama AI Backend

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-green.svg)

A production-ready, open-source backend application integrating **FastAPI**, **PostgreSQL**, and **Ollama** for local Large Language Model (LLM) inference. This project is designed for privacy-first AI applications, such as healthcare data processing or financial document analysis.

## 🚀 Features

- **Local LLM Inference**: Uses [Ollama](https://ollama.ai/) to run models like Llama 3 locally. Data never leaves your infrastructure.
- **Secure Authentication**: Full JWT-based authentication flow (Register, Login).
- **Role-Based Access Control (RBAC)**: Database-driven permission system with dynamic Roles (Admin, User) and Permissions.
- **Structured Output**: Support for JSON mode to extract structured data (e.g., Invoices) from unstructured text.
- **Production Ready**:
  - Async SQLalchemy & Alembic Migrations
  - Docker & Docker Compose setup
  - Pydantic Settings for configuration
  - Clean Architecture

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic
- **LLM Runtime**: Ollama
- **Containerization**: Docker

## 📦 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [Ollama](https://ollama.ai/) (Running inside Docker or locally)

### Quick Start (Docker)

1. **Clone the repository**

   ```bash
   git clone https://github.com/yoosuf/fastapi-ollama-backend.git
   cd fastapi-ollama-backend
   ```

2. **Start the services**

   ```bash
   docker-compose up --build
   ```

   This will start:
   - FastAPI Backend (`http://localhost:8000`)
   - PostgreSQL Database (`port 5432`)
   - Ollama Service (`port 11434`)

3. **Initialize the LLM Model**
   The Ollama container starts empty. You need to pull the model you want to use (e.g., llama3).

   ```bash
   docker-compose exec ollama ollama pull llama3
   ```

4. **Access API Documentation**
   Open your browser and navigate to:
   [http://localhost:8000/docs](http://localhost:8000/docs)

## 🔑 Authentication & RBAC

The system comes with a pre-seeded **Admin** role and a **User** role.

### 1. Register an Admin

To access protected admin routes, register a user with the `admin` role.
_> Note: In a real production environment, you should disable public admin registration._

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "securepassword",
    "role": "admin"
  }'
```

### 2. Login to get Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=admin@example.com" \
  -F "password=securepassword"
```

### 3. Use the Token

Authorize your requests by sending the token in the header:
`Authorization: Bearer <your_access_token>`

## 💡 Usage Examples

### Generic Prompt Generation

```http
POST /api/v1/prompts
Content-Type: application/json
Authorization: Bearer <token>

{
  "prompt_text": "Explain quantum computing in simple terms.",
  "model_name": "llama3"
}
```

### Accounting: Invoice Extraction (Structured JSON)

Extract data from an invoice text into a valid JSON object.

```http
POST /api/v1/extract-invoice
Authorization: Bearer <token>

(Query Param) text_content="Invoice #999 from TechCorp. Date: 2024-01-15. 2 Laptops at $1000 each. Total: $2000."
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Contact

Project Maintainer - Yoosuf Mohamed ([mayoosuf@gmail.com](mailto:mayoosuf@gmail.com))

Project Link: [https://github.com/yoosuf/fastapi-ollama-backend](https://github.com/yoosuf/fastapi-ollama-backend)
