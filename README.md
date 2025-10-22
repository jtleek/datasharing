# 🇧🇷 Brazilian Federal Data Collector SaaS

A comprehensive SaaS platform for accessing, managing, and transforming Brazilian public federal datasets, optimized for AI and machine learning applications.

> **Note**: The original "How to share data with a statistician" guide has been preserved in [README_ORIGINAL.md](README_ORIGINAL.md)

## Overview

This platform provides unified API access to multiple Brazilian federal data sources, with features designed specifically for AI/ML practitioners and data scientists who need clean, well-formatted datasets for training and analysis.

## Features

### 🎯 Core Features

- **Multi-Source Integration**: Access dados.gov.br, Portal da Transparência, IBGE, and more through a single API
- **AI-Ready Formats**: Download data in JSON, CSV, or Parquet formats
- **Data Quality Metrics**: Automatic completeness scores and quality assessments
- **Smart Data Transformation**: Brazilian-specific data normalization (CPF/CNPJ, currency, dates)
- **API Key Management**: Secure access with personal API keys and rate limiting
- **Async Processing**: Background data collection with Celery
- **Search & Discovery**: Full-text search across all datasets
- **Auto-Sync**: Keep datasets updated from official sources

### 📊 Supported Data Sources

1. **dados.gov.br** - Brazilian Open Data Portal (CKAN-based)
   - 10,000+ datasets from federal agencies
   - Multiple formats (CSV, JSON, XML)

2. **Portal da Transparência** - Government Transparency Portal
   - Public spending data
   - Government contracts
   - Public servant salaries
   - Sanctioned companies

3. **IBGE** - Brazilian Institute of Geography and Statistics
   - Geographic data (states, municipalities)
   - Population statistics
   - Economic indicators
   - Census data

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd datasharing

# Copy environment variables
cp .env.example .env

# Edit .env and set your SECRET_KEY
nano .env

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec api python scripts/init_db.py

# View logs
docker-compose logs -f api
```

The API will be available at `http://localhost:8000`

Interactive documentation: `http://localhost:8000/docs`

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Start PostgreSQL and Redis (via Docker or locally)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine

# Initialize database
python scripts/init_db.py

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A celery_app worker --loglevel=info
```

## Usage Examples

### 1. Register and Login

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'

# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=myuser&password=securepassword123"
```

### 2. Create API Key

```bash
# Create an API key (use the access_token from login)
curl -X POST "http://localhost:8000/api/v1/api-keys/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "expires_in_days": 365
  }'
```

### 3. Sync Datasets (Admin Only)

```bash
# Sync datasets from dados.gov.br
curl -X POST "http://localhost:8000/api/v1/datasets/sync/dados_gov_br?limit=100" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 4. Search Datasets

```bash
# Search for datasets
curl -X GET "http://localhost:8000/api/v1/datasets/search?query=educação&limit=20" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Filter by source
curl -X GET "http://localhost:8000/api/v1/datasets/search?source=ibge&ai_ready_only=true" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 5. Fetch Dataset Data

```bash
# Fetch in JSON format
curl -X POST "http://localhost:8000/api/v1/datasets/fetch/1?format=json" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Fetch in Parquet format (optimized for AI/ML)
curl -X POST "http://localhost:8000/api/v1/datasets/fetch/1?format=parquet" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  --output dataset.parquet
```

### 6. Get Statistics

```bash
# Get dataset statistics
curl -X GET "http://localhost:8000/api/v1/datasets/stats" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Python Client Example

```python
import requests
import pandas as pd
from io import BytesIO

class BrazilDataClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def search_datasets(self, query: str = None, source: str = None, limit: int = 20):
        """Search for datasets"""
        params = {"limit": limit}
        if query:
            params["query"] = query
        if source:
            params["source"] = source

        response = requests.get(
            f"{self.base_url}/api/v1/datasets/search",
            headers=self.headers,
            params=params
        )
        return response.json()

    def get_dataset_parquet(self, dataset_id: int) -> pd.DataFrame:
        """Fetch dataset as pandas DataFrame"""
        response = requests.post(
            f"{self.base_url}/api/v1/datasets/fetch/{dataset_id}?format=parquet",
            headers=self.headers
        )

        if response.status_code == 200:
            return pd.read_parquet(BytesIO(response.content))
        else:
            raise Exception(f"Error: {response.text}")

# Usage
client = BrazilDataClient(api_key="bfd_your_api_key_here")

# Search for education datasets
datasets = client.search_datasets(query="educação", limit=10)
print(f"Found {len(datasets)} datasets")

# Fetch first dataset as DataFrame
if datasets:
    df = client.get_dataset_parquet(datasets[0]['id'])
    print(df.head())
```

## API Documentation

Full interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (main.py)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼───────┐
│  API  │ │  Celery  │
│Routes │ │  Tasks   │
└───┬───┘ └──┬───────┘
    │        │
┌───▼────────▼───┐
│   Services     │
│ (Business      │
│  Logic)        │
└───┬────────┬───┘
    │        │
┌───▼───┐ ┌──▼──────────┐
│  DB   │ │ Data        │
│Models │ │ Collectors  │
└───────┘ └──┬──────────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐
│dados  │ │Portal│ │ IBGE │
│.gov.br│ │Trans.│ │      │
└───────┘ └──────┘ └──────┘
```

## Project Structure

```
datasharing/
├── app/
│   ├── api/              # API routes
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── datasets.py   # Dataset endpoints
│   │   └── api_keys.py   # API key management
│   ├── collectors/       # Data source collectors
│   │   ├── base.py
│   │   ├── dados_gov_br.py
│   │   ├── portal_transparencia.py
│   │   └── ibge.py
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utilities
│       ├── security.py
│       └── data_transform.py
├── alembic/              # Database migrations
├── scripts/              # Utility scripts
├── main.py               # FastAPI application
├── celery_app.py         # Celery configuration
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── Dockerfile            # Docker image
└── docker-compose.yml    # Docker services
```

## Configuration

Key environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/datasharing

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Data Sources
DADOS_GOV_BR_BASE_URL=https://dados.gov.br
PORTAL_TRANSPARENCIA_BASE_URL=https://api.portaldatransparencia.gov.br/api-de-dados
IBGE_API_BASE_URL=https://servicodados.ibge.gov.br/api/v3
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
flake8 .
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Production Considerations

1. **Security**:
   - Change `SECRET_KEY` to a strong random value
   - Set `DEBUG=False`
   - Use HTTPS with SSL certificates
   - Configure CORS properly in `main.py`

2. **Database**:
   - Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
   - Enable connection pooling
   - Set up automated backups

3. **Scaling**:
   - Use multiple Celery workers
   - Add Redis cluster for high availability
   - Use load balancer for API instances

4. **Monitoring**:
   - Set up logging aggregation (ELK, Datadog, etc.)
   - Monitor API performance and errors
   - Track quota usage per user

## License

MIT License - see LICENSE file

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Email: support@example.com

## Acknowledgments

Built with data from:
- Portal Brasileiro de Dados Abertos (dados.gov.br)
- Portal da Transparência do Governo Federal
- Instituto Brasileiro de Geografia e Estatística (IBGE)

---

**Original data sharing guidelines by Jeff Leek** - see [README_ORIGINAL.md](README_ORIGINAL.md)
