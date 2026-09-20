# Phase 19: Customer Module Documentation & Test Verification

## 1. Overview
The **Customer Module** provides authenticated customers with self-service capabilities to create support tickets, view their personal ticket history, filter and search through submitted issues, review agent responses, add comments, and close resolved tickets.

It integrates directly with database triggers to automatically generate an audit log entry upon ticket creation and on status transitions.

---

## 2. API Endpoints Specification

### Master Reference Data Endpoints
| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| `GET` | `/api/master/categories` | Public / Authenticated | Returns all active IT categories from `Categories`. |
| `GET` | `/api/master/priorities` | Public / Authenticated | Returns urgency tiers and target SLA hours from `Priorities`. |
| `GET` | `/api/master/statuses` | Public / Authenticated | Returns lifecycle states from `Ticket_Status`. |

### Customer Ticket Endpoints
| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| `POST` | `/api/customer/tickets` | `@login_required` | Creates a new support ticket. Sets status to `Open` (trigger logs inception). |
| `GET` | `/api/customer/tickets` | `@login_required` | Retrieves all tickets submitted by the authenticated customer. Supports `?category_id=`, `?status_id=`, and `?search=`. |
| `GET` | `/api/customer/tickets/<id>` | `@login_required` | Fetches ticket details, SLA status (`fn_GetSLAStatus`), public comments, and status history. Enforces ownership check. |
| `POST` | `/api/customer/tickets/<id>/comments` | `@login_required` | Adds a customer reply to the discussion thread (`is_internal = FALSE`). Updates ticket `updated_at`. |
| `POST` | `/api/customer/tickets/<id>/close` | `@login_required` | Marks the ticket as `Closed`. Trigger records closure transition. |

---

## 3. Database Automation & Trigger Verification

1. **Automatic Inception Logging**: When `POST /api/customer/tickets` executes an `INSERT INTO Tickets`, database trigger `trg_Ticket_Initial_History_Log` automatically inserts:
   - `old_status_id = NULL`
   - `new_status_id = 1 (Open)`
   - `remarks = 'Ticket initially submitted by customer'`
2. **Automatic Closure Transition Logging**: When `POST /api/customer/tickets/<id>/close` updates `status_id = 4 (Closed)`, database trigger `trg_Ticket_Status_History_Log` automatically intercepts the change and records:
   - `old_status_id = 1 (Open)`
   - `new_status_id = 4 (Closed)`
   - `remarks = 'Status transitioned from Open to Closed'`

---

## 4. Test Verification Results

| # | Test Scenario | Route & Method | Expected Result | Actual Result | Status |
|---|---|---|---|---|:---:|
| **1** | Master Categories Query | `GET /api/master/categories` | `200 OK`, 7 categories returned | `200 OK`, 7 categories returned | **PASS** |
| **2** | Master Priorities Query | `GET /api/master/priorities` | `200 OK`, 4 tiers with SLAs | `200 OK`, 4 tiers with SLAs | **PASS** |
| **3** | Unauthenticated Guard | `GET /api/customer/tickets` | `401 Unauthorized` | `401 Unauthorized` | **PASS** |
| **4** | Customer Ticket Submission | `POST /api/customer/tickets` | `201 Created`, ticket_id returned | `201 Created`, ticket #30 created | **PASS** |
| **5** | Customer Ticket List | `GET /api/customer/tickets` | `200 OK`, lists user's tickets | `200 OK`, returned tickets | **PASS** |
| **6** | Customer Comment Addition | `POST /api/customer/tickets/30/comments` | `201 Created` | `201 Created` | **PASS** |
| **7** | Ticket Closure | `POST /api/customer/tickets/30/close` | `200 OK` | `200 OK` | **PASS** |
| **8** | Status Audit Verification | `GET /api/customer/tickets/30` | 2 trigger history rows present | 2 history rows logged via triggers | **PASS** |

---

## 5. Viva Defense Questions & Answers

* **Q: How does the backend prevent Customer A from viewing Customer B's tickets?**
  * **Answer:** Horizontal authorization is enforced in `get_my_tickets()` by scoping the SQL query with `WHERE t.customer_id = %s` using `session['user_id']`. In `get_ticket_details()`, an explicit ownership check compares `ticket['customer_id']` against `session['user_id']`; if mismatched, a `403 Forbidden` is returned.
* **Q: Why are comments flagged with `is_internal`?**
  * **Answer:** `is_internal` is a boolean attribute that supports internal staff collaboration. Support agents and administrators can post diagnostic notes visible only to staff, while customer-facing comments have `is_internal = FALSE`. In `get_ticket_details()`, if `session['role'] == 'customer'`, the SQL query explicitly filters `WHERE is_internal = FALSE`, ensuring staff notes are never leaked to customers.

