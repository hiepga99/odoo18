#!/bin/bash

# Fix PyPDF2 Version Compatibility for Odoo 18
# This script fixes the PyPDF2 version issue when installing Sale module

echo "🔧 Fixing PyPDF2 version compatibility for Odoo 18..."

# Activate virtual environment
source venv/bin/activate

# Check current PyPDF2 version
echo "📋 Current PyPDF2 version:"
pip list | grep -i pypdf

# Uninstall newer incompatible version
echo "❌ Removing incompatible PyPDF2 version..."
pip uninstall PyPDF2 -y

# Install correct version for Odoo 18
echo "✅ Installing PyPDF2 version 1.26.0 (compatible with Odoo 18)..."
pip install PyPDF2==1.26.0

# Verify installation
echo "📋 New PyPDF2 version:"
pip list | grep -i pypdf

echo "✅ PyPDF2 compatibility fixed!"
echo "🔄 Please restart Odoo for changes to take effect." 