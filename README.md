# 🚗 Alo Komak – Roadside Assistance & Auto Service Management System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django)
![HTMX](https://img.shields.io/badge/HTMX-1.9-3d72d7?logo=htmx)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

**Alo Komak** (الو کمک) is a modern web application designed for Iranian roadside assistance businesses.  
It provides a powerful **customer and vehicle database**, **real‑time service request management**, a **dashboard** with daily statistics, and **printable service receipts** – all accessible through a clean, RTL (right‑to‑left) interface optimized for Persian users.

---

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Database Setup](#database-setup)
  - [Running the Development Server](#running-the-development-server)
- [Usage](#-usage)
  - [Operator Workflow](#operator-workflow)
  - [Admin Panel](#admin-panel)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

- **Customer & Vehicle Management**  
  Store detailed customer profiles, multiple vehicles per customer, and **standard Iranian license plates** (4‑part structure: ۲ digits, letter, ۳ digits, city code). Plates are displayed with a **graphical plate badge** and proper LTR alignment.

- **Instant Search**  
  Operators can search by mobile number, last name, first name, or any part of the plate. Results appear instantly without page reload.

- **Service Request Lifecycle**  
  Create new service requests (roadside or in‑shop) with one click. Each request captures:
  - Selected vehicle, service type, fault description, location, assigned technician, and cost.
  - **Status tracking** (Pending → In Progress → Done → Cancelled) directly from the search results or dashboard.

- **HTMX‑Powered Modals**  
  Adding a new service request or a new vehicle opens in a **Bootstrap modal** – no page refresh. After submission, the relevant section (service history or vehicle list) is updated inline.

- **Operator Dashboard**  
  A dedicated dashboard shows today’s statistics:
  - Total requests, Pending, In‑Progress, Done, Cancelled.
  - A live list of today’s requests with quick status change.

- **Printable Service Receipts**  
  Every request can be printed as a professional receipt containing customer info, vehicle details, performed services, technician name, parts used, and total cost. The print layout is clean and ink‑friendly.

- **RTL & Persian‑Friendly UI**  
  Built with Bootstrap 5 RTL, Persian fonts, and Jalali date support (via Django’s locale). The license plate displays correctly in LTR direction.

- **Admin Panel**  
  Full Django admin is configured for managing customers, vehicles, branches, employees, service types, and all service requests.

- **Ready for Production**  
  Configuration via environment variables, SQLite for development, easily switchable to PostgreSQL. Static files management is included.

---

## 📸 Screenshots

*[Add screenshots here – e.g., the dashboard, search page with plate badges, modal forms, and a printed receipt.]*

---

## 🧱 Tech Stack

| Area       | Technology                                              |
|------------|---------------------------------------------------------|
| Backend    | Python 3.9+, Django 4.2                                 |
| Frontend   | Bootstrap 5.3 (RTL), HTMX, Bootstrap Icons, vanilla CSS |
| Database   | SQLite (development), PostgreSQL (production)           |
| Templating | Django Templates with partials for HTMX responses       |
| Dev Tools  | Visual Studio, Git                                      |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (to clone the repository)
- Virtual environment tool (optional but recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SRRasaei/Alo_Komak.git
   cd Alo_Komak

  2. **Create and activate a virtual environment**
     python -m venv venv
     source venv/bin/activate   # On Windows: venv\Scripts\activate
     
  4. **Install dependencies**
     pip install -r requirements.txt
     
**Configuration**

Sensitive settings are managed via environment variables. Create a .env file in the project root (next to manage.py) with the following:
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

Important: Never commit the .env file. It is already included in .gitignore.

In Alo_Komak/settings.py, the secret key is loaded automatically:
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

To load the .env file during development, ensure python-dotenv is installed and add this to manage.py:
import dotenv
dotenv.load_dotenv()

**Database Setup**
Run the migrations to create all necessary tables:
python manage.py migrate

Create a superuser for the admin panel:
python manage.py createsuperuser

**Running the Development Server**
python manage.py runserver 0.0.0.0:8080

Visit:

Operator search page: http://127.0.0.1:8080/

Dashboard: http://127.0.0.1:8080/dashboard/

Admin panel: http://127.0.0.1:8080/admin/

**🧑‍💻 Usage**
**Operator Workflow**
Login with your operator account (or superuser).

On the search page, enter a mobile number, last name, or part of a plate.

The customer’s profile card appears with:

Personal details and phone numbers.

All registered vehicles shown with an Iranian‑style plate badge.

Recent service history in a table.

Create a new service: click the green “+ New Service” button → a modal opens → select the vehicle, service type, fill in the description → submit. The history updates immediately.

Add a vehicle for the customer: click the “+ Add Vehicle” button above the vehicle list → fill in the four‑part plate and other details → the vehicle appears instantly.

Change request status using the dropdown in the status column.

Print a receipt: click the printer icon beside any service request → a new window opens with a print‑optimised layout.

**Admin Panel**
Access /admin/ to manage:

Customers & vehicles (with full CRUD and search).

Branches, employees, service types.

All service requests with inline service details.

**📁 Project Structure**
Alo_Komak/
├── Alo_Komak/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                   # Main application
│   ├── models.py           # All models (Customer, Vehicle, ServiceRequest, etc.)
│   ├── views.py            # Views (search, dashboard, HTMX endpoints, print)
│   ├── forms.py            # VehicleForm, ServiceRequestForm
│   ├── admin.py            # Admin configuration
│   ├── static/core/        # Static assets (CSS)
│   ├── templates/core/     # HTML templates
│   │   ├── base.html
│   │   ├── quick_search.html
│   │   ├── dashboard.html
│   │   ├── create_request.html
│   │   ├── request_modal.html
│   │   ├── vehicle_modal.html
│   │   ├── vehicle_list_partial.html
│   │   ├── recent_requests_partial.html
│   │   ├── print_service.html
│   │   └── login.html
│   └── migrations/
├── manage.py
├── .env                   # Environment variables (not in repo)
├── .gitignore
├── requirements.txt
└── README.md

**🌍 Deployment**
For production, follow standard Django deployment practices:

Set DJANGO_DEBUG=False and configure ALLOWED_HOSTS.

Use PostgreSQL instead of SQLite.

Collect static files with python manage.py collectstatic.

Serve static/media via Nginx or a CDN.

Use Gunicorn (on Linux) or a suitable WSGI server on Windows.

A detailed deployment guide can be added later based on your target server.

**🤝 Contributing**
Contributions are welcome! To contribute:

Fork the repository.

Create a new branch (feature/your-feature).

Make your changes and commit them.

Push to your fork and open a Pull Request.

For bugs or feature requests, please use the Issues page.

**📄 License**
This project is licensed under the MIT License. See the LICENSE file for details.

**📧 Contact**
SR Rasaei

GitHub: @SRRasaei





