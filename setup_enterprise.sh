#!/bin/bash

# Odoo 18 Enterprise Setup Script
# This script configures Odoo 18 with Enterprise modules and dependencies

echo "🚀 Setting up Odoo 18 Enterprise Edition..."

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing Enterprise-specific dependencies..."

# Core enterprise dependencies
pip install python-stdnum
pip install PyPDF2==1.26.0
pip install lxml_html_clean
pip install geoip2

# Excel and document processing
pip install xlwt xlrd xlsxwriter openpyxl

# Security and connection libraries
pip install paramiko cryptography pysftp

# Web services and integrations
pip install zeep suds-py3 ofxparse ebaysdk

# Additional enterprise features
pip install beautifulsoup4
pip install requests-oauthlib
pip install python-magic

echo "✅ Enterprise dependencies installed successfully!"

echo "📁 Checking enterprise modules path..."
if [ -d "enterprise/enterprise" ]; then
    echo "✅ Enterprise modules found at: enterprise/enterprise"
else
    echo "❌ Enterprise modules not found. Please ensure enterprise folder is properly placed."
fi

echo "🔧 Enterprise setup completed!"
echo "🌐 Start Odoo with: ./start_odoo18.sh"
echo "🔗 Access at: http://localhost:1818"
echo ""
echo "📊 Available Enterprise modules include:"
echo "   - Documents, Knowledge, Studio"
echo "   - Advanced Accounting & Reporting"
echo "   - HR Payroll & Contracts"
echo "   - Advanced Project Management"
echo "   - E-commerce & Subscriptions"
echo "   - And many more..." 