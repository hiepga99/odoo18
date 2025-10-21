#!/bin/bash

# Additional Dependencies for Odoo 18 Modules
# This script installs common packages needed by various Odoo modules

echo "🔧 Installing additional Odoo module dependencies..."

# Activate virtual environment
source venv/bin/activate

# Install additional common dependencies
echo "📦 Installing python-stdnum (for account/sale modules)..."
pip install python-stdnum

echo "📦 Installing correct PyPDF2 version for Odoo 18..."
pip install PyPDF2==1.26.0

echo "📦 Installing other common dependencies..."
pip install ofxparse  # For bank statement import
pip install ebaysdk   # For eBay connector
pip install requests-oauthlib  # For OAuth integrations

echo "📦 Installing PDF and image processing libraries..."
pip install wkhtmltopdf  # For PDF reports (if available)
pip install python-magic  # For file type detection

echo "📦 Installing email and communication libraries..."
pip install email-validator  # For email validation

echo "📦 Installing development and testing tools..."
pip install coverage  # For code coverage

echo "✅ Additional dependencies installed successfully!"
echo "🔄 You may need to restart Odoo for all modules to work properly." 