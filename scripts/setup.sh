#!/bin/bash

# Online Poll System - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Online Poll System Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
fi

# Check if PostgreSQL is running
echo "🗄️ Checking PostgreSQL..."
if ! pg_isready -q; then
    echo "⚠️ PostgreSQL is not running. Please start PostgreSQL before continuing."
    echo "You can start it with: brew services start postgresql (on macOS)"
    echo "Or: sudo service postgresql start (on Ubuntu)"
fi

# Check if Redis is running
echo "🔴 Checking Redis..."
if ! redis-cli ping &> /dev/null; then
    echo "⚠️ Redis is not running. Please start Redis before continuing."
    echo "You can start it with: brew services start redis (on macOS)"
    echo "Or: sudo service redis-server start (on Ubuntu)"
fi

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
echo "Please create a superuser account:"
python manage.py createsuperuser

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo ""
echo "🎉 You can now start the development server:"
echo "   python manage.py runserver"
echo ""
echo "📚 Access the API documentation at:"
echo "   http://localhost:8000/api/docs/"
echo ""
echo "🔧 Access the admin panel at:"
echo "   http://localhost:8000/admin/"
echo ""
echo "🐳 Or use Docker Compose:"
echo "   docker-compose up -d"
