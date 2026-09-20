# Phase 17: Backend Setup & Database Connectivity Documentation

## 1. Overview
This document outlines the architecture, configuration, and connectivity verification of the Python Flask backend for the **Customer Support Ticket Management System**.

The backend layer serves as the bridge between the web user interface, the machine learning classification model, and the MySQL database engine.

---

## 2. Architecture & File Structure

```text
backend/
├── config/
│   ├── config.py       # Reads environment variables (.env) and configuration constants
│   └── db.py           # Database connection manager, parameterized query executors
├── routes/             # API blueprints (auth, tickets, admin, reports, ai)
├── controllers/        # Request parsing and HTTP response orchestration
├── services/           # Business logic layer calling DB procedures/queries
├── models/             # Schema data definitions and validation schemas
├── utils/              # Password hashing, decorators, helpers
└── app.py              # Flask application factory, JSON providers, static route handler
```

---

## 3. Database Connectivity & Defensive SQL Design

In `backend/config/db.py`:
- **Direct Parameterized Execution**: All queries use placeholder substitution (`%s`), completely isolating input data from SQL commands to prevent SQL injection vulnerabilities.
- **Dictionary Cursor (`DictCursor`)**: Database rows are returned as dictionary mappings (`{'ticket_id': 1, 'subject': '...'}`), ensuring clean, predictable JSON serialization.
- **Custom JSON Provider**: Extends Flask's `DefaultJSONProvider` to automatically serialize Python `datetime`, `date`, `timedelta`, and `Decimal` objects into ISO-8601 strings and floats without crashing.

---

## 4. Health Check Verification

The `/api/health` endpoint verifies that the Flask application and the MySQL database are properly linked and communicating:

* **HTTP Method:** `GET`
* **URL:** `/api/health`
* **Response Status:** `200 OK`
* **Response Payload:**
```json
{
  "service": "Customer Support Ticket Management API",
  "status": "healthy",
  "database": {
    "status": "connected",
    "info": {
      "db_name": "support_ticket_db",
      "version": "10.4.11-MariaDB"
    }
  }
}
```

---

## 5. Viva Defense Notes

* **Q: How does this backend architecture protect against SQL Injection attacks?**
  * **Answer:** By enforcing parameterized queries throughout `backend/config/db.py` (e.g. `cursor.execute(sql, params)`). The database driver sends the query template and the parameter data in separate protocol packets; user input is treated strictly as data literals and can never be interpreted as executable SQL syntax.
* **Q: Why was Flask selected over heavyweight frameworks like Django for this DBMS mini-project?**
  * **Answer:** Flask is minimalist and lightweight. Heavy frameworks like Django enforce their own Object-Relational Mapping (ORM) layer, which obscures raw SQL, views, triggers, and stored procedures behind Python classes. Flask allows us to write and expose transparent, raw SQL queries and stored procedure invocations directly, which is the primary objective of a college DBMS project.

