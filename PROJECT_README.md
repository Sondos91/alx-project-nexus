# Online Poll System Backend - Project Nexus

## 🎯 Project Overview

This is a comprehensive **Online Poll System Backend** built with Django REST Framework, designed as a capstone project for the ProDev Backend Engineering program. The system provides real-time voting capabilities with optimized database design and comprehensive API documentation.

## 🚀 Key Features

### **Core Functionality**
- **Poll Management**: Create, update, and manage polls with multiple options
- **Real-time Voting**: Cast votes with duplicate prevention and validation
- **Live Results**: Real-time calculation of vote counts and percentages
- **User Authentication**: Support for both authenticated and anonymous voting
- **API Documentation**: Comprehensive Swagger/OpenAPI documentation

### **Technical Features**
- **Scalable Architecture**: Optimized database schema for high-performance operations
- **Caching Strategy**: Redis-based caching for improved response times
- **Background Processing**: Celery for asynchronous task processing
- **Containerization**: Docker support for easy deployment
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## 🛠️ Technologies Used

### **Backend Framework**
- **Django 4.2.7**: High-level Python web framework
- **Django REST Framework**: Building robust RESTful APIs
- **PostgreSQL**: Relational database for data persistence
- **Redis**: Caching and message broker

### **Additional Tools**
- **Celery**: Asynchronous task processing
- **Docker**: Containerization and deployment
- **Swagger/OpenAPI**: API documentation
- **GitHub Actions**: CI/CD pipeline

## 📋 API Endpoints

### **Poll Management**
- `GET /api/polls/` - List all polls with filtering options
- `POST /api/polls/` - Create a new poll (authenticated)
- `GET /api/polls/{id}/` - Get detailed poll information
- `PUT/PATCH /api/polls/{id}/` - Update poll (creator only)
- `DELETE /api/polls/{id}/` - Delete poll (creator only)

### **Voting System**
- `POST /api/polls/{id}/vote/` - Cast a vote
- `GET /api/polls/{id}/results/` - Get real-time poll results

### **User Management**
- `GET /api/user/polls/` - Get user's created polls
- `GET /api/user/votes/` - Get user's voting history
- `GET /api/user/profile/` - Get user profile with statistics

### **Documentation**
- `GET /api/docs/` - Interactive Swagger documentation
- `GET /api/redoc/` - ReDoc documentation
- `GET /api/schema/` - OpenAPI schema

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### **Local Development Setup**

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/alx-project-nexus.git
   cd alx-project-nexus
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - Documentation: http://localhost:8000/api/docs/

### **Docker Setup**

1. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

3. **Access the application**
   - API: http://localhost:8000/api/
   - Documentation: http://localhost:8000/api/docs/

## 📊 Performance Features

### **Real-time Results**
- Cached vote counts for instant response
- Asynchronous result updates
- Redis-based caching strategy
- Optimized database queries

### **Scalability**
- Database indexing for fast queries
- Pagination for large datasets
- Background task processing
- Containerized deployment

### **Security**
- Input validation and sanitization
- Duplicate vote prevention
- Rate limiting capabilities
- CORS configuration

## 🧪 Testing

### **Run Tests**
```bash
python manage.py test
```

### **Run with Coverage**
```bash
pip install pytest-cov
pytest --cov=polls --cov-report=html
```

### **API Testing**
Use the interactive Swagger documentation at `/api/docs/` or import the OpenAPI schema into Postman.

## 📈 Monitoring & Maintenance

### **Management Commands**
```bash
# Update poll results cache
python manage.py update_poll_results

# Update specific poll
python manage.py update_poll_results --poll-id <poll-id>

# Force update all results
python manage.py update_poll_results --force
```

### **Background Tasks**
- Celery worker processes handle result updates
- Scheduled tasks for maintenance
- Health checks for service monitoring

## 🚀 Deployment

### **Production Deployment**
1. Set production environment variables
2. Configure database and Redis
3. Run migrations
4. Collect static files
5. Start services with Gunicorn
6. Configure reverse proxy (Nginx)

### **Docker Deployment**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### **CI/CD Pipeline**
- Automated testing on pull requests
- Docker image building and pushing
- Automated deployment to production

## 📚 API Documentation

### **Interactive Documentation**
- **Swagger UI**: `/api/docs/` - Interactive API explorer
- **ReDoc**: `/api/redoc/` - Clean, responsive documentation
- **OpenAPI Schema**: `/api/schema/` - Machine-readable API specification

### **Example API Usage**

#### **Create a Poll**
```bash
curl -X POST "http://localhost:8000/api/polls/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "title": "What is your favorite programming language?",
    "description": "Choose your preferred language for backend development",
    "options": [
      {"text": "Python", "order": 1},
      {"text": "JavaScript", "order": 2},
      {"text": "Java", "order": 3}
    ]
  }'
```

#### **Cast a Vote**
```bash
curl -X POST "http://localhost:8000/api/polls/{poll-id}/vote/" \
  -H "Content-Type: application/json" \
  -d '{"option_text": "Python"}'
```

#### **Get Results**
```bash
curl "http://localhost:8000/api/polls/{poll-id}/results/"
```

## 🤝 Collaboration

### **ProDev Backend Engineering Program**
This project serves as a comprehensive demonstration of backend engineering skills including:

- **API Design**: RESTful API design principles
- **Database Optimization**: Efficient schema design and query optimization
- **Real-time Processing**: Asynchronous task handling and caching
- **Documentation**: Comprehensive API documentation
- **Testing**: Unit and integration testing
- **Deployment**: Containerization and CI/CD

### **Frontend Integration**
The API is designed for easy integration with frontend applications:
- CORS enabled for cross-origin requests
- Comprehensive error handling
- Detailed response formats
- Real-time result updates

## 📞 Support

For questions or support regarding this project:
- **GitHub Issues**: Create an issue in this repository
- **Discord**: Join #ProDevProjectNexus for collaboration
- **Documentation**: Check the API docs at `/api/docs/`

## 📄 License

This project is part of the ProDev Backend Engineering program and is intended for educational purposes.

---

**Project Nexus - Online Poll System Backend**  
*Demonstrating real-world backend engineering skills with Django, PostgreSQL, and modern development practices.*

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Active Development
