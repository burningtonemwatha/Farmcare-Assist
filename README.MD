# 🌾 AgriWatch - Smart Farm Management Platform

<div align="center">
  
![AgriWatch Banner](https://images.unsplash.com/photo-1500382017468-9049fed747ef?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80)

**Empowering Farmers Through Technology**

[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

*Smarter Farming, Healthier Crops*

</div>

## 📋 Table of Contents
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🏗️ Architecture](#️-architecture)
- [📱 Core Modules](#-core-modules)
- [💳 Payment Integration](#-payment-integration)
- [🛠️ Installation](#️-installation)
- [🔧 Configuration](#-configuration)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)

## ✨ Features

### 🌟 **For Farmers**
- **📸 Smart Issue Reporting** - Upload photos and describe farm problems
- **💬 Real-time Expert Consultation** - Connect with certified agricultural experts
- **📊 Farm Dashboard** - Monitor all your reports and recommendations
- **🌱 Crop Health Tracking** - Track the progress of remediation actions
- **🔔 Smart Notifications** - Get alerts for expert responses and updates

### 🎓 **For Agricultural Experts**
- **📋 Expert Dashboard** - Manage assigned farm reports efficiently
- **🔍 Diagnostic Tools** - Analyze farm issues with specialized tools
- **💼 Professional Profile** - Showcase expertise and specialization areas
- **💰 Payment Integration** - Securely receive consultation fees

### 🔐 **Platform Security**
- **👤 Role-based Authentication** - Separate interfaces for farmers and experts
- **🔒 Secure Payment Processing** - M-Pesa integration with STK push
- **📁 Protected Media Storage** - Secure file uploads and management
- **🛡️ CSRF Protection** - Built-in Django security features

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL (recommended) or SQLite
- Virtualenv (optional but recommended)

### Installation in 5 Minutes
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/agriwatch.git
cd agriwatch

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your settings

# 6. Setup database
python manage.py migrate
python manage.py createsuperuser

# 7. Run the server
python manage.py runserver
```

Visit `http://localhost:8000` and start exploring!

## 🏗️ Architecture

```
agriwatch/
├── accounts/          # User authentication & profiles
├── farmcare/          # Core farm management logic
├── payments/          # M-Pesa payment integration
├── templates/         # HTML templates
│   ├── accounts/      # Auth templates
│   ├── farmcare/      # Farm management templates
│   └── payment/       # Payment templates
└── static/           # CSS, JS, images
```

### Technology Stack
| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Django 5.2 | Robust web framework with ORM |
| **Frontend** | Bootstrap 5.3 | Responsive, mobile-first design |
| **Database** | PostgreSQL/SQLite | Data persistence |
| **Payments** | M-Pesa API | Secure mobile payments |
| **Icons** | FontAwesome 6.4 | Professional iconography |
| **Deployment** | Gunicorn + Nginx | Production-ready setup |

## 📱 Core Modules

### 1. **Accounts Module** (`accounts/`)
- User registration and authentication
- Profile management with user types (Farmer/Expert)
- Secure login/logout with session management
- Email notifications system

### 2. **FarmCare Module** (`farmcare/`)
- **Report Management**: Create, view, and track farm issues
- **Expert Matching**: Connect farmers with relevant experts
- **Dashboard Views**: Personalized dashboards for each user type
- **Media Handling**: Photo uploads and management

### 3. **Payments Module** (`payments/`)
- **M-Pesa Integration**: Real-time payment processing
- **Payment Status Tracking**: Monitor transaction states
- **Receipt Management**: Digital payment records
- **Checkout Flow**: User-friendly payment interface

## 💳 Payment Integration

AgriWatch integrates with **M-Pesa**, Kenya's leading mobile money service:

### Features:
- ✅ **STK Push** - Direct payment prompts to user phones
- ✅ **Payment Status Tracking** - Real-time transaction monitoring
- ✅ **Secure Transactions** - Encrypted payment processing
- ✅ **Receipt Generation** - Digital transaction records

### Payment Flow:
```mermaid
graph LR
    A[Farmer Reports Issue] --> B[Expert Diagnosis]
    B --> C[Payment Request]
    C --> D[STK Push to Phone]
    D --> E[PIN Entry]
    E --> F[Payment Confirmation]
    F --> G[Expert Consultation]
```

## 🛠️ Installation

### Detailed Setup Guide

1. **Database Configuration**
```bash
# For PostgreSQL
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb agriwatch
sudo -u postgres createuser agriuser

# Update settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'agriwatch',
        'USER': 'agriuser',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

2. **Environment Variables**
```bash
# .env file
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://user:pass@localhost/agriwatch
MPESA_CONSUMER_KEY=your_mpesa_consumer_key
MPESA_CONSUMER_SECRET=your_mpesa_consumer_secret
MPESA_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey
```

3. **Production Deployment**
```bash
# Collect static files
python manage.py collectstatic

# Install production WSGI server
pip install gunicorn

# Run with gunicorn
gunicorn agriwatch.wsgi:application --bind 0.0.0.0:8000
```

## 🔧 Configuration

### M-Pesa Setup
1. Register on [Safaricom Developer Portal](https://developer.safaricom.co.ke/)
2. Create an app to get Consumer Key and Secret
3. Configure your shortcode and passkey
4. Update `.env` with your credentials

### Email Configuration
```python
# For Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Static & Media Files
```python
# Development
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Production
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute
1. **Report Bugs** - Open an issue with detailed bug reports
2. **Suggest Features** - Share your ideas for improvement
3. **Submit Pull Requests** - Contribute code enhancements
4. **Improve Documentation** - Help make docs clearer
5. **Share with Farmers** - Spread the word about AgriWatch

### Development Process
```bash
# 1. Fork the repository
# 2. Create a feature branch
git checkout -b feature/amazing-feature

# 3. Commit your changes
git commit -m 'Add amazing feature'

# 4. Push to the branch
git push origin feature/amazing-feature

# 5. Open a Pull Request
```

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation accordingly

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 AgriWatch Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 Acknowledgments

### Built With
- **[Django](https://www.djangoproject.com/)** - The web framework for perfectionists with deadlines
- **[Bootstrap](https://getbootstrap.com/)** - The most popular CSS framework
- **[M-Pesa API](https://developer.safaricom.co.ke/)** - Kenya's mobile money service
- **[FontAwesome](https://fontawesome.com/)** - The web's most popular icon set

### Inspiration
- **Farmers everywhere** - For their hard work and dedication
- **Agricultural Experts** - For sharing their knowledge
- **Open Source Community** - For making tools accessible to all

### Support
- Found a bug? [Open an issue](https://github.com/yourusername/agriwatch/issues)
- Need help? [Check discussions](https://github.com/yourusername/agriwatch/discussions)
- Want to chat? [Join our community](https://github.com/yourusername/agriwatch/discussions/1)

---

<div align="center">

**🌱 Growing together, one farm at a time**

[Get Started](#-quick-start) •
[View Demo](#) •
[Report Issue](https://github.com/yourusername/agriwatch/issues) •
[Request Feature](https://github.com/yourusername/agriwatch/issues)

*Made with ❤️ for farmers everywhere*

</div>

## 📞 Contact & Support

- **Website**: [agriwatch.example.com](https://agriwatch.example.com)
- **Email**: support@agriwatch.example.com
- **Twitter**: [@AgriWatchApp](https://twitter.com/AgriWatchApp)
- **Community Forum**: [Join Discussion](https://github.com/yourusername/agriwatch/discussions)

## 📊 Project Status

| Component | Status | Version |
|-----------|--------|---------|
| Core Platform | ✅ Production Ready | v1.0.0 |
| Payment Integration | ✅ Live | v1.0.0 |
| Mobile Responsive | ✅ Complete | v1.0.0 |
| Multi-language | 🔄 Planned | v2.0.0 |
| Mobile App | 🔄 In Development | v1.5.0 |

---

*Last Updated: December 2025*