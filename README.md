# Legal Intel Dashboard - Backend

A robust FastAPI-based backend service for the Legal Intelligence Dashboard. This service provides AI-powered document analysis, risk assessment, compliance checking, and comprehensive data management for legal professionals.

## 🚀 Features

### Core Services
- **Document Processing**: Extract text from PDF, DOCX, DOC, and TXT files
- **AI Analysis**: Regex-based pattern matching for risk assessment and compliance
- **Risk Assessment**: Automated risk level evaluation (LOW, MEDIUM, HIGH)
- **Compliance Checking**: Regulatory compliance status assessment
- **Business Impact Analysis**: Document impact evaluation and scoring

### API Endpoints
- **Authentication**: JWT-based user authentication and authorization
- **Document Management**: CRUD operations for legal documents
- **Dashboard Analytics**: Aggregated insights and metrics
- **Export Services**: CSV and PDF export capabilities
- **Query Interface**: Natural language document querying

### Data Processing
- **Text Extraction**: Multi-format document text extraction
- **Metadata Extraction**: Automatic document metadata identification
- **AI Insights Generation**: Automated summary and analysis
- **Confidence Scoring**: Quality assessment of extracted data

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite (with SQLAlchemy ORM)
- **Authentication**: JWT with Python-Jose
- **File Processing**: PyPDF2, python-docx, PyMuPDF
- **AI Analysis**: Regex patterns, text processing
- **Export Services**: CSV generation, PDF creation
- **Documentation**: OpenAPI/Swagger auto-generation
- **Testing**: Pytest
- **Deployment**: Uvicorn ASGI server

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                 # API route definitions
│   │   ├── auth_routes.py   # Authentication endpoints
│   │   ├── document_routes.py # Document management
│   │   ├── dashboard_routes.py # Dashboard analytics
│   │   ├── export_routes.py # Export services
│   │   ├── query_routes.py  # Query interface
│   │   └── routes.py        # Main router configuration
│   ├── core/                # Core configuration
│   │   ├── config.py        # Application settings
│   │   ├── security.py      # JWT authentication
│   │   └── database.py      # Database configuration
│   ├── models/              # Data models
│   │   ├── document.py      # Document schemas
│   │   ├── user.py          # User models
│   │   └── ai_insights.py   # AI analysis models
│   ├── services/            # Business logic
│   │   ├── ai_analyzer.py   # AI analysis service
│   │   ├── auth_service.py  # Authentication service
│   │   ├── document_service.py # Document processing
│   │   ├── export_service.py # Export generation
│   │   ├── file_storage.py  # File management
│   │   └── query_service.py # Query processing
│   └── utils/               # Utility functions
│       ├── file_utils.py    # File handling utilities
│       └── text_utils.py    # Text processing utilities
├── tests/                   # Test suite
├── requirements.txt          # Python dependencies
├── main.py                  # Application entry point
├── Dockerfile               # Container configuration
└── README.md                # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/masdev94/legalDashBackend.git
   cd legalDash/backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the backend directory:
   ```env
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   UPLOAD_DIR=./uploads
   ```
5. **Start the server**
   ```bash
   python main.py
   ```

6. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Available Commands

- `python main.py` - Start development server
- `pytest` - Run test suite
- `pytest -v` - Run tests with verbose output
- `pytest --cov=app` - Run tests with coverage

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: JWT signing secret
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `DATABASE_URL`: Database connection string
- `UPLOAD_DIR`: File upload directory path

### Database Configuration
The application uses SQLite by default for development. For production, consider:
- PostgreSQL with async support
- MySQL with proper indexing
- MongoDB for document storage

### File Storage
- Local file system (default)
- Cloud storage (AWS S3, Google Cloud Storage)
- Distributed file systems

## 📚 API Documentation

### Authentication
All protected endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Key Endpoints

#### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Token refresh

#### Documents
- `GET /documents` - List all documents
- `POST /documents/upload` - Upload new document
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document

#### Dashboard
- `GET /dashboard` - Get dashboard analytics
- `GET /dashboard/export/{format}` - Export dashboard data (CSV/PDF)

#### Query
- `POST /query` - Natural language document query
- `GET /query/history` - Query history

### Request/Response Examples

#### Upload Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "metadata={\"agreement_type\":\"contract\",\"jurisdiction\":\"US\"}"
```

#### Query Documents
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me high-risk contracts"}'
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password encryption
- **Input Validation**: Pydantic model validation
- **CORS Protection**: Configurable cross-origin policies
- **Rate Limiting**: API request throttling
- **File Validation**: Secure file upload handling

## 📊 AI Analysis Engine

### Risk Assessment
The AI analyzer uses pattern matching to assess document risk levels:
- **LOW**: Minimal risk factors detected
- **MEDIUM**: Moderate risk factors present
- **HIGH**: Significant risk factors identified

### Compliance Checking
Automated compliance status assessment:
- **COMPLIANT**: Meets regulatory requirements
- **NON_COMPLIANT**: Violations detected
- **REVIEW_REQUIRED**: Manual review needed

### Confidence Scoring
Quality assessment of extracted data:
- **Low (0-40%)**: Poor quality, manual review recommended
- **Medium (41-70%)**: Acceptable quality
- **High (71-95%)**: High quality, reliable data

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_ai_analyzer.py
```

### Test Structure
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Mock Tests**: External service mocking

## 🚀 Deployment

### Development
```bash
python main.py
```

### Production
```bash
# Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn with uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment
```bash
# Build image
docker build -t legal-dashboard-backend .

# Run container
docker run -p 8000:8000 legal-dashboard-backend
```

### Environment-Specific Configurations
- **Development**: SQLite, debug mode, detailed logging
- **Staging**: PostgreSQL, production-like settings
- **Production**: Optimized database, minimal logging, monitoring

## 📈 Performance Optimization

### Database Optimization
- Proper indexing on frequently queried fields
- Connection pooling for database connections
- Query optimization and caching

### File Processing
- Asynchronous file uploads
- Background task processing
- File compression and optimization

### API Performance
- Response caching
- Pagination for large datasets
- Efficient data serialization

## 🔍 Monitoring and Logging

### Logging Configuration
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log rotation and archival

### Health Checks
- `/health` endpoint for service health
- Database connectivity checks
- External service dependencies

### Metrics Collection
- Request/response timing
- Error rates and types
- Resource usage monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use type hints throughout the codebase

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the [Issues](../../issues) page
- Review the API documentation at `/docs`
- Contact the development team

## 🔄 Version History

- **v1.0.0** - Initial release with basic document processing
- **v1.1.0** - Added AI analysis and risk assessment
- **v1.2.0** - Enhanced export capabilities and query interface
- **v1.3.0** - Improved performance and error handling

---

**Built with ❤️ for the legal community**
