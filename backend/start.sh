#!/bin/bash
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Starting Backend Services...${NC}"

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
EOF

# Initialize cryptocurrencies with real prices
python manage.py shell << EOF
from api.tasks import initialize_crypto_prices
initialize_crypto_prices()
EOF

echo -e "${GREEN}Backend setup complete!${NC}"
echo -e "${BLUE}You can access:${NC}"
echo "- GraphQL: http://localhost:8000/graphql"
echo "- Admin: http://localhost:8000/admin (admin/admin)"

python manage.py runserver 0.0.0.0:8000