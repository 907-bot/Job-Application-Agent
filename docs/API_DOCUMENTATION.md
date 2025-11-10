# API Documentation

## Base URL

```
http://localhost:7860  (Development)
https://api.job-agent.com  (Production)
```

## Authentication

Currently uses Gradio's built-in session management. For API usage:

```python
# Bearer token authentication (optional)
headers = {
    'Authorization': 'Bearer YOUR_API_TOKEN',
    'Content-Type': 'application/json'
}
```

## Endpoints

### **1. Search Jobs**

Search for jobs based on keywords and location.

**URL:** `/search-jobs`  
**Method:** `POST`  
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "keywords": "python docker aws",
  "location": "Remote",
  "num_jobs": 5
}
```

**Response Success (200):**
```json
{
  "status": "success",
  "total_jobs_found": 5,
  "relevant_jobs": 4,
  "pass_rate": 0.8,
  "applications": [
    {
      "job": {
        "id": "job_001",
        "title": "Senior Python Developer",
        "company": "Tech Giants Inc",
        "location": "Remote",
        "requirements": ["Python", "Docker", "AWS"],
        "experience_required": 5,
        "salary_range": "$120k - $160k"
      },
      "relevance_score": 0.95,
      "match_details": {
        "matching_skills": ["Python", "Docker", "AWS"],
        "missing_skills": [],
        "match_percentage": "100%"
      },
      "customized_resume": {
        "summary": "Experienced engineer with Python and Docker expertise...",
        "skills": ["Python", "Docker", "AWS", ...]
      },
      "application_status": "Ready to Apply"
    }
  ]
}
```

**Response Error (400):**
```json
{
  "status": "error",
  "message": "Invalid search parameters",
  "details": "Keywords cannot be empty"
}
```

---

### **2. Customize Resume**

Generate customized resume for specific job.

**URL:** `/customize-resume`  
**Method:** `POST`

**Request Body:**
```json
{
  "job_title": "Senior Python Developer",
  "company": "Tech Giants Inc",
  "requirements": ["Python", "Docker", "AWS", "Kubernetes"]
}
```

**Response (200):**
```json
{
  "status": "success",
  "customized_resume": {
    "name": "Alex Chen",
    "email": "alex.chen@email.com",
    "phone": "+1-555-0123",
    "location": "San Francisco, CA",
    "summary": "Customized summary highlighting relevant skills...",
    "skills": ["Python", "Docker", "AWS", "Kubernetes", ...],
    "experience_details": [
      "Led microservices platform team using Docker and Kubernetes",
      "Deployed AWS infrastructure handling 10M+ users",
      ...
    ],
    "customized_for": {
      "job_title": "Senior Python Developer",
      "company": "Tech Giants Inc",
      "matching_skills": ["Python", "Docker", "AWS", "Kubernetes"],
      "match_score": 1.0
    }
  },
  "cover_letter": "Dear Hiring Manager, I am writing to express my interest in the Senior Python Developer position..."
}
```

---

### **3. Classify Job**

Analyze job relevance for candidate.

**URL:** `/classify-job`  
**Method:** `POST`

**Request Body:**
```json
{
  "job_title": "Senior Python Developer",
  "requirements": "Python, Docker, AWS, PostgreSQL"
}
```

**Response (200):**
```json
{
  "status": "success",
  "relevance_analysis": {
    "relevance_score": 0.92,
    "match_percentage": "92%",
    "matching_skills": ["Python", "Docker", "AWS"],
    "missing_skills": ["PostgreSQL"],
    "extra_skills": ["Kubernetes", "TensorFlow"],
    "recommendation": "Highly Recommended - Strong match",
    "decision": "APPLY"
  }
}
```

---

### **4. Batch Process**

Process multiple jobs at once.

**URL:** `/batch-process`  
**Method:** `POST`

**Request Body:**
```json
{
  "jobs": [
    {
      "title": "Senior Python Developer",
      "requirements": ["Python", "Docker"]
    },
    {
      "title": "Frontend Developer",
      "requirements": ["React", "TypeScript"]
    }
  ],
  "auto_apply": false,
  "min_relevance": 0.5
}
```

**Response (200):**
```json
{
  "status": "success",
  "total_processed": 2,
  "successful": 2,
  "failed": 0,
  "results": [...]
}
```

---

### **5. Get Application History**

Retrieve past application records.

**URL:** `/history`  
**Method:** `GET`

**Query Parameters:**
- `limit`: Number of records (default: 10, max: 100)
- `offset`: Pagination offset (default: 0)
- `sort`: Sort by (default: "date", options: "date", "relevance", "company")
- `order`: ASC or DESC (default: "DESC")

**Response (200):**
```json
{
  "status": "success",
  "total": 25,
  "limit": 10,
  "offset": 0,
  "applications": [
    {
      "application_id": "app_001",
      "job_title": "Senior Python Developer",
      "company": "Tech Giants Inc",
      "applied_date": "2025-11-10",
      "relevance_score": 0.95,
      "status": "submitted",
      "customized_resume_path": "/output/resume_app_001.json"
    }
  ]
}
```

---

### **6. Export Results**

Export application results in various formats.

**URL:** `/export`  
**Method:** `GET`

**Query Parameters:**
- `format`: "json" | "csv" | "pdf" (required)
- `date_range`: "today" | "week" | "month" | "all" (default: "all")

**Response (200):**
```
Content-Type: application/json (or application/pdf)

[Exported data in requested format]
```

---

### **7. Health Check**

Verify API and service status.

**URL:** `/health`  
**Method:** `GET`

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T04:09:00Z",
  "components": {
    "api": "healthy",
    "model": "loaded",
    "database": "connected",
    "cache": "healthy"
  },
  "uptime": "15 hours",
  "version": "1.0.0"
}
```

---

### **8. System Status**

Get detailed system information.

**URL:** `/status`  
**Method:** `GET`

**Response (200):**
```json
{
  "system": {
    "version": "1.0.0",
    "environment": "production",
    "uptime": 54000,
    "timestamp": "2025-11-10T04:09:00Z"
  },
  "resources": {
    "cpu_percent": 45.2,
    "memory_percent": 62.5,
    "memory_available_gb": 8.5,
    "disk_percent": 35.8
  },
  "model": {
    "name": "MAYINI",
    "parameters": 3500000,
    "vocab_size": 5000,
    "loaded": true
  },
  "metrics": {
    "requests_total": 1250,
    "requests_per_minute": 5.2,
    "avg_response_time_ms": 245,
    "error_rate": 0.002
  }
}
```

---

## Error Responses

### **400 Bad Request**
```json
{
  "status": "error",
  "code": "INVALID_REQUEST",
  "message": "Invalid parameters provided",
  "details": {
    "field": "keywords",
    "issue": "Cannot be empty"
  }
}
```

### **401 Unauthorized**
```json
{
  "status": "error",
  "code": "UNAUTHORIZED",
  "message": "Authentication required"
}
```

### **429 Too Many Requests**
```json
{
  "status": "error",
  "code": "RATE_LIMITED",
  "message": "Rate limit exceeded",
  "retry_after": 60
}
```

### **500 Internal Server Error**
```json
{
  "status": "error",
  "code": "INTERNAL_ERROR",
  "message": "An unexpected error occurred",
  "error_id": "err_abc123"
}
```

---

## Rate Limiting

- **Limit:** 60 requests per minute per IP
- **Header:** `X-RateLimit-Remaining`
- **Reset:** Hourly

---

## Pagination

Use `limit` and `offset` parameters:

```
GET /history?limit=10&offset=20
```

Typical response includes:
```json
{
  "total": 150,
  "limit": 10,
  "offset": 20,
  "data": [...]
}
```

---

## Webhooks

Subscribe to events:

```
POST /webhooks/subscribe
{
  "event": "application_submitted",
  "url": "https://your-domain.com/callback"
}
```

---

## SDKs & Libraries

### **Python**
```python
from job_agent import JobApplicationAgent

agent = JobApplicationAgent(api_key='YOUR_KEY')
results = agent.search_jobs('python', 'Remote')
```

### **JavaScript**
```javascript
import { JobAgent } from 'job-agent-sdk';

const agent = new JobAgent({ apiKey: 'YOUR_KEY' });
const results = await agent.searchJobs('python', 'Remote');
```

---

## Examples

### **Python Example**
```python
import requests
import json

API_URL = "http://localhost:7860"

# Search jobs
response = requests.post(
    f"{API_URL}/search-jobs",
    json={
        "keywords": "python docker",
        "location": "Remote",
        "num_jobs": 5
    }
)

if response.status_code == 200:
    results = response.json()
    print(f"Found {results['total_jobs_found']} jobs")
```

### **cURL Example**
```bash
curl -X POST http://localhost:7860/search-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "python docker",
    "location": "Remote",
    "num_jobs": 5
  }'
```

---

## Best Practices

1. **Always include error handling**
2. **Use pagination for large datasets**
3. **Cache responses when possible**
4. **Implement exponential backoff for retries**
5. **Monitor rate limit headers**
6. **Use appropriate HTTP methods**
7. **Validate input before sending**
8. **Log all API calls for debugging**

---

## Support

For API issues, contact: `api-support@job-agent.com`

Documentation: https://docs.job-agent.com
