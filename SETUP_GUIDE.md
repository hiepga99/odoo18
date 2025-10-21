# Odoo 18 Enterprise Local Setup Guide

## 🎯 Overview
This guide helps you run Odoo 18 Enterprise Edition locally on port 1818 with full access to both Community and Enterprise modules.

## ⭐ Enterprise Features Available
- 📋 **Documents & Knowledge Management** - Advanced document handling and knowledge base
- 🧾 **Advanced Accounting & Reporting** - Professional financial reports and analytics  
- 👥 **HR Payroll & Contracts** - Complete human resources management
- 📊 **Project Management & Timesheets** - Advanced project tracking and time management
- 🛒 **E-commerce & Subscriptions** - Professional online sales and recurring billing
- 🏭 **Manufacturing & Quality** - Production planning and quality control
- 📱 **Studio & Mobile** - Custom app builder and mobile access
- 🔗 **API & Integrations** - Advanced third-party integrations

## 📋 Prerequisites
- ✅ Python 3.8+ (currently using Python 3.8.16)
- ✅ PostgreSQL (installed and running)
- ✅ Virtual environment created
- ✅ Dependencies installed

## 🚀 Quick Start

### 1. Start Odoo 18
```bash
./start_odoo18.sh
```

### 2. Access Odoo
- Open your browser and go to: http://localhost:1818
- Default admin password: `admin`

## 🔧 Configuration Files

### `odoo18.conf`
Main configuration file with settings:
- **Port**: 1818 (HTTP) / 1819 (Gevent)
- **Database**: PostgreSQL with user `odoo18`
- **Addons**: Both community (`odoo/addons`) and enterprise (`enterprise/enterprise`) modules
- **Admin password**: `admin`
- **Enterprise**: Full access to all enterprise modules

## 🗄️ Database Setup
- **User**: `odoo18`
- **Password**: `odoo18`
- **Host**: localhost
- **Port**: 5432

## 📁 Project Structure
```
Odoo18/
├── odoo/                      # Community edition
├── enterprise/                # Enterprise modules
│   └── enterprise/            # Actual enterprise modules directory
├── venv/                      # Virtual environment
├── odoo18.conf               # Configuration file (Enterprise enabled)
├── start_odoo18.sh           # Startup script
├── setup_enterprise.sh       # Enterprise setup script
├── install_additional_deps.sh # Additional dependencies installer
├── fix_pypdf2.sh             # PyPDF2 version fixer
└── SETUP_GUIDE.md            # This guide
```

## 🛠️ Manual Commands

If you prefer to run commands manually:

```bash
# Activate virtual environment
source venv/bin/activate

# Start Odoo Enterprise
python3 odoo/odoo-bin -c odoo18.conf --dev=all

# Setup Enterprise dependencies (run once)
./setup_enterprise.sh

# Install additional module dependencies (if needed)
./install_additional_deps.sh

# Fix PyPDF2 version compatibility (if getting PyPDF2 errors)
./fix_pypdf2.sh
```

## 🐛 Troubleshooting

### Port Already in Use
If port 1818 is busy, edit `odoo18.conf` and change `http_port = 1818` to another port.

### Database Connection Issues
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify user exists: `sudo -u postgres psql -c "\\du" | grep odoo18`

### GeoIP Authentication Error (Fixed)
✅ **Issue**: `NameError: name 'GEOIP_EMPTY_COUNTRY' is not defined` after login
✅ **Solution**: Installed geoip2 library and disabled GeoIP in config for development

### Module Installation Errors (Fixed)

#### Missing stdnum library
✅ **Issue**: `ModuleNotFoundError: No module named 'stdnum'` when installing Sale module
✅ **Solution**: Install python-stdnum library
```bash
source venv/bin/activate
pip install python-stdnum
```

#### PyPDF2 Version Compatibility
✅ **Issue**: `PyPDF2.errors.DeprecationError: getFormTextFields is deprecated` when installing Sale module
✅ **Solution**: Use correct PyPDF2 version for Odoo 18
```bash
source venv/bin/activate
pip uninstall PyPDF2 -y
pip install PyPDF2==1.26.0
```

### Missing Dependencies
If you encounter import errors, install missing packages:
```bash
source venv/bin/activate
pip install [package-name]
# Then restart Odoo for the new packages to take effect
```

**Common fixes**:
- Run `./install_additional_deps.sh` to install packages needed by various Odoo modules
- Run `./fix_pypdf2.sh` if you encounter PyPDF2 version compatibility errors

## 🎮 Development Features
The setup includes development mode (`--dev=all`) which provides:
- Automatic module reloading
- Debug mode
- Enhanced logging

## 📞 Support
For issues, check the Odoo documentation or community forums.

---
*Happy Coding! 🎉* 