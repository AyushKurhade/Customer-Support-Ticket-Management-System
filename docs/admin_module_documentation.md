# Phase 21: Administrator Management Module Documentation & Test Verification

## 1. Overview
The **Administrator Management Module** provides privileged operational control over the entire system. System Administrators can provision staff accounts, manage user roles, inspect system-wide ticket queues, assign or reassign tickets to agents (invoking Stored Procedure `sp_AssignTicket`), escalate ticket priorities, and manage master reference data (Categories, Priorities, and SLAs).

---

## 2. API Endpoints Specification

All Admin endpoints are strictly guarded by `@role_required(['admin'])`. Non-admin accounts (Customers and Support Agents) receive `403 Forbidden`.

| Method | Endpoint | Request Body | Operational Purpose |
|---|---|---|---|
| `GET` | `/api/admin/users` | Optional query: `?role=` | Retrieves all users with ticket counts. Excludes `password_hash`. |
| `POST` | `/api/admin/users` | `name`, `email`, `password`, `role`, `contact_number` | Provisions a new Support Agent or Administrator with PBKDF2 hashing. |
| `GET` | `/api/admin/tickets` | Filters: `status_id`, `priority_id`, `category_id`, `agent_id`, `unassigned_only`, `search` | Global ticket registry across all customers and agents. |
| `POST` | `/api/admin/tickets/<id>/assign` | `agent_id` | Invokes stored procedure `sp_AssignTicket` to assign agent and advance state to `In Progress`. |
| `PUT` | `/api/admin/tickets/<id>/priority` | `priority_id`, `remarks` | Escalate or adjust ticket priority with internal handover audit comment. |
| `POST` | `/api/admin/categories` | `category_name`, `description` | Creates a new IT service domain category in master reference data. |
| `PUT` | `/api/admin/priorities/<id>` | `sla_hours` | Adjusts SLA resolution target hours, enforcing `CHECK (sla_hours > 0)`. |

---

## 3. Database Concept Integration

1. **Stored Procedure Invocation (`sp_AssignTicket`)**:
   - Rather than executing inline SQL updates, `POST /api/admin/tickets/<id>/assign` directly invokes `sp_AssignTicket`.
   - Validates that the target user has role `'agent'`.
   - If the ticket was in state `'Open'`, it is automatically advanced to `'In Progress'`.
2. **CHECK Constraint Compliance**:
   - `PUT /api/admin/priorities/<id>` checks `sla_hours > 0`, aligning with the physical database constraint `CONSTRAINT chk_priorities_sla CHECK (sla_hours > 0)`.
3. **Data Protection & Sanitization**:
   - `GET /api/admin/users` omits `password_hash` from the `SELECT` projection, preventing inadvertent credential exposure over HTTP.

---

## 4. Test Verification Results

| # | Test Scenario | Route & Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|:---:|
| **1** | Non-Admin Access Rejection | `GET /api/admin/users` as Agent | `403 Forbidden` | `403 Forbidden` | **PASS** |
| **2** | Global User Registry | `GET /api/admin/users` as Admin | `200 OK`, passwords hidden | `200 OK`, password_hash hidden | **PASS** |
| **3** | Agent Provisioning | `POST /api/admin/users` (Alex Taylor) | `201 Created` | `201 Created`, user #32 created | **PASS** |
| **4** | Unassigned Ticket Filter | `GET /api/admin/tickets?unassigned_only=true` | `200 OK`, unassigned only | `200 OK`, returned unassigned list | **PASS** |
| **5** | Ticket Assignment via Stored Procedure | `POST /api/admin/tickets/<id>/assign` | `200 OK`, assigned to Alex | `200 OK`, assigned via `sp_AssignTicket` | **PASS** |
| **6** | Priority Escalation | `PUT /api/admin/tickets/<id>/priority` | `200 OK`, priority set to Critical | `200 OK`, updated with internal log | **PASS** |
| **7** | Dynamic Category Creation | `POST /api/admin/categories` (Cloud Infra) | `201 Created` | `201 Created`, category created | **PASS** |
| **8** | Dynamic SLA Adjustment | `PUT /api/admin/priorities/1` (60 hours) | `200 OK`, SLA updated | `200 OK`, Low priority = 60h | **PASS** |

---

## 5. Viva Defense Questions & Answers

* **Q: Why should ticket assignment call a Stored Procedure rather than executing raw SQL directly from the Python backend?**
  * **Answer:** Encapsulation and consistency. Stored procedure `sp_AssignTicket` enforces database-level validation (verifying that the assigned user actually holds the `agent` role and that the ticket exists), advances the status machine atomically from `Open` to `In Progress`, and ensures business rules cannot be bypassed by external scripts.
* **Q: How does the Admin Module manage master reference data dynamically without code changes?**
  * **Answer:** By providing endpoints (`/api/admin/categories` and `/api/admin/priorities/<id>`) that modify the underlying normalized master tables (`Categories`, `Priorities`). When an admin creates a new category (e.g. "Cloud Infrastructure"), it immediately appears in all customer ticket forms and AI category mapping tables without restarting the server or editing code.
