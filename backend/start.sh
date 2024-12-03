#!/bin/bash

function kill_processes() {
    echo "Cleaning up processes..."
    docker-compose down -v
}

trap kill_processes EXIT

echo "🔄 Starting services..."

# Build and start services
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "Running migrations..."
docker-compose exec -T backend python manage.py makemigrations
docker-compose exec -T backend python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
docker-compose exec -T backend python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
EOF

# Initialize cryptocurrencies
echo "Creating initial cryptocurrencies..."
docker-compose exec -T backend python manage.py shell << EOF
from api.models import CryptoCurrency
currencies = [
    {"name": "Curve DAO", "symbol": "CRV", "price": 0},
    {"name": "Curve USD", "symbol": "crvUSD", "price": 0},
    {"name": "Stake DAO Curve USD", "symbol": "scrvUSD", "price": 0}
]
for currency in currencies:
    CryptoCurrency.objects.get_or_create(**currency)
EOF

echo "✅ All services started!"
echo
echo "🔍 You can test the application:"
echo "1. Visit GraphQL playground: http://localhost:8000/graphql"
echo "   Query example:"
echo "   query {"
echo "     allCryptocurrencies {"
echo "       name"
echo "       symbol"
echo "       price"
echo "     }"
echo "   }"
echo
echo "2. Admin interface: http://localhost:8000/admin"
echo "   Credentials: admin/admin"
echo
echo "3. Monitor logs:"
echo "   docker-compose logs -f"

docker-compose logs -f