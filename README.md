# Django REST API Project

This project is a Django REST Framework (DRF) based API with **drf-spectacular** for automatic OpenAPI schema generation and interactive API documentation.

---

## 🚀 Features
- Django REST Framework (DRF) APIs
- Auto-generated OpenAPI schema
- Interactive API docs with Swagger UI and ReDoc
- Easy setup and local development

---

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-project-folder>

   ```
2. **Create and activate a virtual environment**
   ```bash
python3 -m venv venv
source venv/bin/activate 

   ```


3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

   ```

# Running the Project
-python manage.py runserver

# API Documentation
-Swagger UI → http://127.0.0.1:8000/api/schema/swagger-ui/

-ReDoc → http://127.0.0.1:8000/api/schema/redoc/

-Raw OpenAPI Schema (YAML/JSON) → http://127.0.0.1:8000/api/schema/