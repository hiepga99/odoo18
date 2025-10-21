#!/bin/bash

# Odoo 18 Startup Script
# This script starts Odoo 18 on port 1818

echo "🚀 Starting Odoo 18 on port 1818..."

# Activate virtual environment
source venv/bin/activate

# Check if PostgreSQL is running
if ! sudo systemctl is-active --quiet postgresql; then
    echo "⚠️  PostgreSQL is not running. Starting PostgreSQL..."
    sudo systemctl start postgresql
fi

# Start Odoo with our configuration
echo "📁 Using configuration file: odoo18.conf"
echo "🌐 Odoo will be available at: http://localhost:1818"
echo "🔐 Default admin password: admin"
echo ""
echo "To stop Odoo, press Ctrl+C"
echo ""

# Run Odoo
python3 odoo/odoo-bin -c odoo18.conf --dev=all

echo "👋 Odoo 18 stopped." 