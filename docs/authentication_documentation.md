# Phase 18: Authentication & Role-Based Access Control Documentation

## 1. Overview
The **Authentication and User Management Module** handles secure user registration, credential verification, session lifecycle management, and role-based access control (RBAC) across the three defined system roles: **Customer**, **Support Agent**, and **Administrator**.

---

## 2. Security Architecture

### 1. Password Hashing (Anti-Plaintext)
* In accordance with Section 31 of the project requirements, passwords are **never** stored in plain text.
* Passwords are salt-hashed using standard **PBKDF2 with SHA-256** (1,000,000 iterations) via `werkzeug.security.generate_password_hash`.
* Verification utilizes constant-time comparison via `werkzeug.security.check_password_hash` to defend against timing side-channel attacks.

### 2. Session Management & RBAC Decorators
* User state is tracked through cryptographically signed server-side session cookies.
* Access control is enforced using two Python decorators:
  * `@login_required`: Restricts endpoints to logged-in sessions (returns `401 Unauthorized` if unauthenticated).
  * `@role_required(['admin', 'agent'])`: Restricts endpoints to authorized roles (returns `403 Forbidden` if unauthorized).

---

## 3. Endpoints Specification

| Method | Endpoint | Access | Request Body | Success Response | Error Codes |
|---|---|---|---|---|---|
| `POST` | `/api/auth/register` | Public | `name`, `email`, `password`, `contact_number` | `201 Created` + user object | `400` (Validation), `409` (Email exists) |
| `POST` | `/api/auth/login` | Public | `email`, `password` | `200 OK` + role profile + session | `400` (Missing input), `401` (Bad credentials) |
| `POST` | `/api/auth/logout` | Authenticated | None | `200 OK` (Session cleared) | None |
| `GET` | `/api/auth/me` | Public / Session | None | `200 OK` (`authenticated: true/false`) | None |

---

## 4. Test Verification Results

| # | Test Scenario | Input Data | Expected Status | Actual Status | Result |
|---|---|---|---|---|:---:|
| **1** | Admin Authentication | `admin@support.com` / `Password@123` | `200 OK`, `role: 'admin'` | `200 OK`, `role: 'admin'` | **PASS** |
| **2** | Session Verification (`/me`) | Active session | `200 OK`, returns email | `200 OK`, `admin@support.com` | **PASS** |
| **3** | Agent Authentication | `sarah.agent@support.com` / `Password@123` | `200 OK`, `role: 'agent'` | `200 OK`, `role: 'agent'` | **PASS** |
| **4** | Customer Registration | `Emily Watson` / `emily@customer.com` | `201 Created` | `201 Created` | **PASS** |
| **5** | Duplicate Email Prevention | Re-register `emily@customer.com` | `409 Conflict` | `409 Conflict` | **PASS** |
| **6** | Bad Password Rejection | Valid email + invalid password | `401 Unauthorized` | `401 Unauthorized` | **PASS** |
| **7** | Session Logout | `POST /api/auth/logout` | `200 OK` | `200 OK` | **PASS** |
| **8** | Profile After Logout | `/api/auth/me` | `authenticated: false` | `authenticated: false` | **PASS** |

---

## 5. Viva Defense Questions & Answers

* **Q: Why must passwords never be stored in plain text in a database?**
  * **Answer:** Plain text passwords expose user credentials to complete compromise in the event of a database dump or unauthorized SQL access. Hashing transforms the password using a one-way cryptographic mathematical function with a unique salt, making it computationally irreversible while still allowing instant verification during login.
* **Q: What is the difference between Authentication and Authorization?**
  * **Answer:**
    - **Authentication:** Verifying *who you are* (e.g. validating email and password credentials).
    - **Authorization:** Determining *what you are allowed to do* based on your role (e.g. verifying that only an `agent` can update ticket statuses or only an `admin` can access the performance dashboard).
* **Q: How does the application verify that a registered user cannot choose an `admin` role?**
  * **Answer:** In `register_user()`, the `role` is hardcoded to `'customer'` in the SQL INSERT statement. Even if a malicious user injects `"role": "admin"` into the registration JSON payload, the backend ignores it. Furthermore, at the database level, the `CHECK (role IN ('customer', 'agent', 'admin'))` constraint guarantees that only valid enumerated roles exist.

