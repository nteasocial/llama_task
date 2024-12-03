#!/bin/bash

echo "🔄 Stopping any running containers..."
docker-compose down -v

echo "🏗️  Building and starting services..."
docker-compose up -d --build

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🗄️  Running migrations..."
docker-compose exec backend python manage.py migrate

echo "🧪 Running tests..."
docker-compose exec backend pytest -v

echo "✅ Setup complete! Services running at:"
echo "👉 Backend: http://localhost:8000"
echo "👉 GraphQL: http://localhost:8000/graphql"
echo "👉 Admin: http://localhost:8000/admin"

echo "📋 Checking service status..."
docker-compose ps