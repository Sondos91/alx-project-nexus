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

### **Render Deployment with PostgreSQL**

#### **Step 1: Create PostgreSQL Database**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "PostgreSQL"
3. Configure your database:
   - **Name**: `poll-system-db` (or your preferred name)
   - **Database**: `poll_system_db`
   - **User**: `poll_system_user` (or your preferred username)
   - **Region**: Choose closest to your users
4. Copy the **Internal Database URL** details (not the external URL)

#### **Step 2: Create Web Service**
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Choose deployment method:

**Option A: Docker Deployment (Recommended)**
- Render will automatically detect your `Dockerfile`
- **Start Command**:
  ```bash
  python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers 3 poll_system.wsgi:application
  ```

**Option B: Native Python Deployment**
- **Build Command**:
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- **Start Command**:
  ```bash
  python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers 3 poll_system.wsgi:application
  ```

#### **Step 3: Configure Environment Variables**
Set these in your Render Web Service settings:

**Database Configuration:**
```
USE_POSTGRES=True
DB_NAME=<from your PostgreSQL Internal Database URL>
DB_USER=<from your PostgreSQL Internal Database URL>
DB_PASSWORD=<from your PostgreSQL Internal Database URL>
DB_HOST=<Internal Hostname from PostgreSQL service>
DB_PORT=5432
```

**Application Configuration:**
```
SECRET_KEY=<generate a strong secret key>
DEBUG=False
ALLOWED_HOSTS=<your-service-name.onrender.com>
```

**Optional Redis Configuration (if using Redis on Render):**
```
REDIS_URL=redis://<your-redis-service>:6379/1
CELERY_BROKER_URL=redis://<your-redis-service>:6379/0
CELERY_RESULT_BACKEND=redis://<your-redis-service>:6379/0
```

#### **Step 4: Deploy and Setup**
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Create admin user via Render Shell:
   ```bash
   python manage.py createsuperuser
   ```
4. Access your application:
   - **API**: `https://your-service-name.onrender.com/api/`
   - **Admin**: `https://your-service-name.onrender.com/admin/`
   - **Documentation**: `https://your-service-name.onrender.com/api/docs/`

### **Production Deployment Checklist**
- [ ] PostgreSQL database configured
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Admin user created
- [ ] Health checks configured
- [ ] SSL certificate active (automatic on Render)

### **Docker Deployment (Local/Other Platforms)**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### **CI/CD Pipeline**
- Automated testing on pull requests
- Docker image building and pushing
- Automated deployment to production

### **Troubleshooting Deployment Issues**

#### **Common Issues and Solutions:**

**Database Connection Errors:**
- Ensure you're using the **Internal Database URL** details, not external
- Verify all `DB_*` environment variables are set correctly
- Check that `USE_POSTGRES=True` is set

**Static Files Not Loading:**
- Ensure `python manage.py collectstatic --noinput` runs during build
- Verify `STATIC_ROOT` is set correctly in settings
- Check that WhiteNoise is properly configured

**Migration Errors:**
- Run migrations manually via Render Shell: `python manage.py migrate`
- Check for conflicting migrations: `python manage.py showmigrations`
- Reset migrations if needed: `python manage.py migrate --fake-initial`

**Service Won't Start:**
- Check Render logs for specific error messages
- Verify all required environment variables are set
- Ensure the start command includes both migration and server start

**Health Check Failures:**
- Verify the health check endpoint `/api/` is accessible
- Check that the service is binding to `0.0.0.0:8000`
- Ensure all dependencies are properly installed

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

**Last Updated**: January 2025  
**Version**: 1.1.0  
**Status**: Active Development
