# Electricity Billing Management System

Python (Tkinter) + MySQL desktop billing application with three roles:
ADMIN, EMPLOYEE, CUSTOMER.

## Setup

1. Install dependencies:
   ```
   pip install mysql-connector-python
   ```

2. Create your local database:
   ```
   mysql -u root -p < database/schema.sql
   mysql -u root -p electricity_billing < database/seed.sql   # optional demo data
   ```

3. Configure database credentials:
   ```
   cp .env.example .env
   ```
   Edit `.env` and fill in your real `DB_HOST` / `DB_USER` / `DB_PASSWORD` / `DB_NAME`.
   `.env` is git-ignored and is never committed.

4. Run the app:
   ```
   python main.py
   ```

## Demo accounts (from database/seed.sql)

| Role     | Username                        | Password       |
|----------|----------------------------------|-----------------|
| Admin    | admin                            | Admin@123       |
| Employee | employee.raj                     | Employee@123    |
| Customer | demo.customer1@example.com       | DemoPass@123    |
| Customer | demo.customer2@example.com       | DemoPass@123    |
| Customer | demo.customer3@example.com       | DemoPass@123    |

Passwords are stored hashed (PBKDF2-SHA256). The seed file writes them as
plain text for readability; the app automatically hashes each one the
first time that account logs in.

## Project layout

- `main.py` -- entry point, login screen, role routing
- `database/` -- `connections.py` (env-based config), `schema.sql`, `seed.sql`
- `services/` -- all business logic and SQL (no UI code)
- `ui/` -- all Tkinter screens, organized as: shared design system
  (`theme.py`, `components.py`), the three role shells
  (`admin_dashboard.py`, `employee_dashboard.py`, `customer_dashboard.py`),
  and one file per management screen
