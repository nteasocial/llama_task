#!/bin/bash

function kill_processes() {
    echo "Cleaning up processes..."
    pkill -f "redis-server"
    pkill -f "celery"
    pkill -f "runserver"
}

trap kill_processes EXIT

echo "🔄 Starting services..."
if [ "$1" = "docker" ]; then
    export ENV=docker
    echo "Running in Docker environment"
    docker-compose up -d --build
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "🧪 Running tests in Docker..."
    docker-compose exec backend pytest -v
else
    export ENV=local
    echo "Running in local environment"
    
    # Kill any existing processes
    kill_processes
    
    echo "Starting Redis..."
    redis-server --port 6389 &
    sleep 2
    
    echo "Starting Django..."
    cd backend
    python manage.py migrate
    
    echo "🧪 Running tests locally..."
    pytest -v
    
    python manage.py runserver &
    sleep 2
    
    echo "Starting Celery worker..."
    cd backend && celery -A app worker -l info &
    sleep 2
    
    echo "Starting Celery beat..."
    cd backend && celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
    
    echo "✅ All services started!"
    echo 
    echo "🔍 You can test the application:"
    echo "1. Visit GraphQL playground: http://localhost:8000/graphql"
    echo "   Try these queries:"
    echo "   query {"
    echo "     allCryptocurrencies {"
    echo "       name"
    echo "       symbol"
    echo "       price"
    echo "     }"
    echo "   }"
    echo
    echo "2. Visit Admin interface: http://localhost:8000/admin"
    echo "   - Add some cryptocurrencies (CRV, crvUSD, scrvUSD)"
    echo "   - Check if prices are being updated"
    echo
    echo "3. Monitor logs:"
    echo "   - Celery worker: docker-compose logs -f celery-worker"
    echo "   - Celery beat: docker-compose logs -f celery-beat"
    
    read -p "Press enter to stop all services..."
fi