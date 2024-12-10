#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_service() {
    container_name=$1
    max_attempts=30
    attempt=1
    
    echo -e "${YELLOW}Waiting for $container_name to be ready...${NC}"
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep $container_name | grep -q "Up"; then
            echo -e "${GREEN}$container_name is ready!${NC}"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e "${RED}$container_name failed to start!${NC}"
    return 1
}

echo -e "${BLUE}Starting Backend Services...${NC}"
docker-compose down
docker-compose build --no-cache
docker-compose up -d backend celery_worker celery_beat redis postgres

check_service "backend"

echo -e "${YELLOW}Running backend setup...${NC}"
docker-compose exec -T backend python manage.py makemigrations
docker-compose exec -T backend python manage.py migrate

echo -e "${YELLOW}Creating superuser...${NC}"
docker-compose exec -T backend python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
EOF

# Initialize cryptocurrencies
echo -e "${YELLOW}Creating initial cryptocurrencies...${NC}"
docker-compose exec -T backend python manage.py shell << EOF
from api.models import CryptoCurrency
CryptoCurrency.objects.all().delete()
currencies = [
    {"name": "Curve DAO", "symbol": "CRV", "price": 0},
    {"name": "Curve USD", "symbol": "crvUSD", "price": 0},
    {"name": "Stake DAO CRV", "symbol": "sdCRV", "price": 0},
    {"name": "Ethereum", "symbol": "ETH", "price": 0},
    {"name": "Stable CRV", "symbol": "sCRV", "price": 0}
]
for currency in currencies:
    try:
        CryptoCurrency.objects.update_or_create(
            symbol=currency["symbol"],
            defaults={
                "name": currency["name"],
                "price": currency["price"]
            }
        )
        print(f"Created/Updated {currency['symbol']}")
    except Exception as e:
        print(f"Error creating {currency['symbol']}: {str(e)}")
EOF

echo -e "${BLUE}Starting Frontend...${NC}"
docker-compose up -d frontend
check_service "frontend"

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}You can access:${NC}"
echo "- Frontend: http://localhost:3000"
echo "- Backend GraphQL: http://localhost:8000/graphql"
echo "- Admin Panel: http://localhost:8000/admin (admin/admin)"

echo -e "${YELLOW}Following logs... (Ctrl+C to stop)${NC}"
docker-compose logs -f