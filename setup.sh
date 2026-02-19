#!/bin/bash
# Setup script for Moodle ELT Integration
# This script helps initialize the environment and start services

set -e

echo "================================================"
echo "Moodle ELT Integration - Setup Script"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration:"
    echo "   - Moodle instance URLs"
    echo "   - Moodle API tokens"
    echo "   - Database credentials"
    echo ""
    echo "After editing .env, run this script again."
    exit 0
fi

echo "✅ Found .env file"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✅ Docker is installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✅ Docker Compose is installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p logs plugins config
echo "✅ Directories created"
echo ""

# Set AIRFLOW_UID if not set
if [ -z "${AIRFLOW_UID}" ]; then
    export AIRFLOW_UID=$(id -u)
    echo "export AIRFLOW_UID=${AIRFLOW_UID}" >> .env
fi

echo "Starting services with Docker Compose..."
echo ""
docker-compose up -d

echo ""
echo "================================================"
echo "✅ Services are starting up!"
echo "================================================"
echo ""
echo "Access the services at:"
echo "  - Airflow UI: http://localhost:8080"
echo "    Username: admin"
echo "    Password: admin"
echo ""
echo "  - Superset: http://localhost:8088"
echo "    Username: admin"
echo "    Password: admin"
echo ""
echo "  - PostgreSQL: localhost:5432"
echo "    Username: airflow"
echo "    Password: airflow"
echo "    Database: airflow"
echo ""
echo "⏳ Wait 2-3 minutes for services to fully initialize..."
echo ""
echo "Next steps:"
echo "  1. Open Airflow UI and configure Variables (Admin → Variables):"
echo "     - moodle1_url, moodle1_token"
echo "     - moodle2_url, moodle2_token"
echo "     - moodle3_url, moodle3_token"
echo "     - moodle4_url, moodle4_token"
echo ""
echo "  2. Configure PostgreSQL connection (Admin → Connections):"
echo "     Connection ID: postgres_moodle"
echo "     Connection Type: Postgres"
echo "     Host: postgres"
echo "     Schema: airflow"
echo "     Login: airflow"
echo "     Password: airflow"
echo "     Port: 5432"
echo ""
echo "  3. Enable DAGs:"
echo "     - moodle1_elt"
echo "     - moodle2_elt"
echo "     - moodle3_elt"
echo "     - moodle4_elt"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo "================================================"
