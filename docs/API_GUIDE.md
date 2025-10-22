# API Guide

## Authentication

All API endpoints (except `/auth/register` and `/auth/login`) require authentication via Bearer token or API key.

### Option 1: JWT Token

1. Register or login to get an access token
2. Include in requests: `Authorization: Bearer <token>`

### Option 2: API Key (Recommended for integrations)

1. Login to get a JWT token
2. Create an API key: `POST /api/v1/api-keys/`
3. Use API key in all requests: `Authorization: Bearer bfd_xxxxx`

## Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "myusername",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "myusername",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "monthly_quota": 1000,
  "current_usage": 0,
  "created_at": "2025-01-15T10:00:00Z"
}
```

#### POST /api/v1/auth/login
Login and receive access token.

**Request (form data):**
```
username=myusername&password=password123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### GET /api/v1/auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "myusername",
  "is_active": true,
  "monthly_quota": 1000,
  "current_usage": 45
}
```

### Dataset Endpoints

#### GET /api/v1/datasets/search
Search for datasets across all sources.

**Query Parameters:**
- `query` (optional): Search term
- `source` (optional): Filter by source (dados_gov_br, portal_transparencia, ibge)
- `organization` (optional): Filter by organization
- `ai_ready_only` (optional, boolean): Only AI-ready datasets
- `limit` (optional, max 100): Results per page
- `offset` (optional): Pagination offset

**Example:**
```bash
GET /api/v1/datasets/search?query=educação&source=ibge&limit=20
```

**Response:**
```json
[
  {
    "id": 1,
    "external_id": "dataset-123",
    "title": "Censo Escolar 2024",
    "description": "Dados do censo escolar brasileiro",
    "source": "ibge",
    "organization": "IBGE",
    "tags": ["educação", "censo", "escolas"],
    "format": "csv",
    "size_bytes": 10485760,
    "status": "available",
    "ai_ready": true,
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

#### GET /api/v1/datasets/stats
Get overall dataset statistics.

**Response:**
```json
{
  "total_datasets": 1547,
  "datasets_by_source": {
    "dados_gov_br": 1200,
    "portal_transparencia": 6,
    "ibge": 341
  },
  "ai_ready_count": 856,
  "total_size_gb": 145.7
}
```

#### GET /api/v1/datasets/{dataset_id}
Get details for a specific dataset.

**Response:**
```json
{
  "id": 1,
  "external_id": "dataset-123",
  "title": "Censo Escolar 2024",
  "description": "...",
  "source": "ibge",
  "metadata": {
    "author": "IBGE",
    "license": "Creative Commons",
    "resources_count": 3
  }
}
```

#### POST /api/v1/datasets/fetch/{dataset_id}
Fetch actual dataset data in specified format.

**Query Parameters:**
- `format`: Output format (json, csv, parquet)

**Response:**
```json
{
  "dataset_id": 1,
  "format": "json",
  "data": [...]
}
```

#### POST /api/v1/datasets/sync/{source}
Synchronize datasets from a source (Admin only).

**Path Parameters:**
- `source`: Data source (dados_gov_br, portal_transparencia, ibge)

**Query Parameters:**
- `limit` (optional, max 1000): Max datasets to sync

**Response:**
```json
{
  "source": "dados_gov_br",
  "synced_count": 150
}
```

### API Key Endpoints

#### POST /api/v1/api-keys/
Create a new API key.

**Request:**
```json
{
  "name": "My Production Key",
  "expires_in_days": 365
}
```

**Response:**
```json
{
  "id": 1,
  "key": "bfd_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "name": "My Production Key",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z",
  "expires_at": "2026-01-15T10:00:00Z"
}
```

#### GET /api/v1/api-keys/
List all API keys for current user.

**Response:**
```json
[
  {
    "id": 1,
    "key": "bfd_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "name": "My Production Key",
    "total_requests": 1547,
    "last_used_at": "2025-01-15T14:30:00Z"
  }
]
```

#### DELETE /api/v1/api-keys/{key_id}
Delete an API key.

#### PUT /api/v1/api-keys/{key_id}/deactivate
Deactivate an API key without deleting it.

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

Default limits:
- 60 requests per minute
- 1000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642345678
```

## Data Formats

### JSON
Standard JSON format with UTF-8 encoding.

### CSV
Comma-separated values with header row.

### Parquet
Apache Parquet format, optimized for:
- Columnar storage
- Compression
- Fast reading in pandas/spark
- ML/AI workflows
