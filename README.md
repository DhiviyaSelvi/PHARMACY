# PHARMACY
An online pharmacy management and e-commerce platform developed with Django and PostgreSQL featuring medicine listings, category filters, shopping cart, checkout system, and admin dashboard.

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   - Copy `.env.example` to `.env`.
   - Update the values in `.env` with your local database credentials and a secure `SECRET_KEY`.

3. **Apply Migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Collect Static Files:**
   ```bash
   python manage.py collectstatic
   ```

5. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```

## Checking the Project

- **System Check:** Run `python manage.py check` to ensure the configuration is correct.
- **Production Check:** Run `python manage.py check --deploy` to see production-level security recommendations.
