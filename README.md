# ExpenseBoard

A personal finance management system with bank statement parsing, expense categorization, and analytics powered by Apache Superset.

## Features

- 📄 **Bank Statement Parsing** - Automatically extract transactions from PDF statements
- 🏦 **Multi-Bank Support** - Union Bank, SBI, HDFC, ICICI, Kotak, and more
- 🏷️ **Smart Categorization** - DSL-based rules for auto-categorizing transactions
- 👥 **Multi-User & Groups** - Track personal and shared/family finances
- 🎯 **Financial Goals** - Set and track savings targets
- 📊 **Analytics Dashboard** - Visualize spending with Apache Superset
- ⚡ **Async Processing** - Celery workers for background PDF processing

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend API | FastAPI, Python 3.12 |
| PDF Parsing | pdfplumber |
| Task Queue | Celery + Redis |
| Database | PostgreSQL 17 |
| Analytics | Apache Superset |
| Containerization | Docker Compose |

## Project Structure

```
ExpenseBoard/
├── StatementParser/          # FastAPI + PDF parsing service
│   ├── app/
│   │   ├── main.py
│   │   ├── celery_app.py
│   │   ├── models/
│   │   ├── parsers/
│   │   ├── tasks/
│   │   └── utils/
│   ├── files/                # Uploaded PDFs
│   ├── Dockerfile
│   └── requirements.txt
├── SuperSetBoard/            # Superset configuration
│   ├── superset_config.py
│   └── init_superset.sh
├── docker-compose.yml
├── .env.example
└── README.md
```

## Database Schema

### Core Tables

| Table | Description |
|-------|-------------|
| `ss_users` | User accounts |
| `ss_bank_accounts` | Linked bank accounts |
| `ss_transactions` | Financial transactions |
| `ss_categories` | Transaction categories |
| `ss_tags` | Transaction tags |
| `ss_goals` | Financial goals |
| `ss_groups` | Shared expense groups |
| `ss_categorization_rules` | DSL-based auto-categorization rules |

### ERD

See `docs/er-diagram.xml` (open with draw.io)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ExpenseBoard.git
cd ExpenseBoard

# Copy environment file
cp .env.example .env
# Edit .env with your configuration


docker build --no-cache -t superset-custom .

# Start all services
docker-compose up -d


> docker-compose restart rules-app


# [OPTIONAL] Initialize database
docker exec -it statement_parser_api python -m alembic upgrade head

# Access services
- API: http://localhost:8000/docs
- Superset: http://localhost:8088
```

### Environment Variables

```env
Refer to .env.example file
```




### API Endpoints

```bash
# Upload statement
POST /api/v1/statements/upload
Content-Type: multipart/form-data

# Get transactions
GET /api/v1/transactions?user_id=1&from_date=2025-01-01

# Get categories
GET /api/v1/categories

# Create categorization rule
POST /api/v1/rules
{
  "name": "Salary Rule",
  "user_id": 1,
  "dsl_text": "IF entity CONTAINS 'SALARY' THEN category = 'Salary'"
}
```

### Supported Banks

| Bank | Email Pattern | Status |
|------|---------------|--------|
| Union Bank | `@unionbankofindia.bank.in` | ✅ |
| SBI | `@sbi.co.in` | ✅ |
| HDFC | `@hdfc` | ✅ |
| ICICI | `@icici` | ✅ |
| Kotak | `@kotak` | ✅ |
| Axis | `@axis` | ✅ |

### Payment Methods Detected

- UPI (UPIAR, UPIAB)
- NEFT
- IMPS
- RTGS
- NACH
- ATM
- Cheque
- Card (Visa, Mastercard, Rupay)

## Development

### Local Setup

```bash
cd StatementParser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run API
uvicorn app.main:app --reload

# Run Celery worker
celery -A app.celery_app worker --loglevel=info -Q statement_parser
```

### Running Tests

```bash
pytest tests/ -v
```

## Docker Services

| Service | Container | Port |
|---------|-----------|------|
| API | statement_parser_api | 8000 |
| Superset | superset_app | 8088 |
| PostgreSQL | superset_postgres | 5432 |
| Redis | superset_redis | 6379 |
| Parser Worker | statement_parser_worker | - |
| Parser Beat | statement_parser_beat | - |
| Superset Worker | superset_celery | - |

```bash
# View logs
docker-compose logs -f statement_parser_worker

# Scale workers
docker-compose up -d --scale statement_parser_worker=3

# Restart specific service
docker-compose restart api
```

## Superset Dashboards

1. Access Superset at `http://localhost:8088`
2. Login with admin credentials
3. Add PostgreSQL database connection
4. Import pre-built dashboards from `SuperSetBoard/dashboards/`

### Available Dashboards

- 📈 Monthly Spending Overview
- 🏷️ Category-wise Breakdown
- 🎯 Goal Progress Tracker
- 👥 Group Expense Summary

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open Pull Request

## License

MIT License

## Acknowledgments

- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF parsing
- [Apache Superset](https://superset.apache.org/) - Analytics
- [FastAPI](https://fastapi.tiangolo.com/) - API framework


