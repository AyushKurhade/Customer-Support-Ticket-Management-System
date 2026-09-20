# Phase 20: Support Agent Module Documentation & Test Verification

## 1. Overview
The **Support Agent Module** equips IT support staff with tools to inspect their assigned queue, review issue descriptions, publish public customer replies or private internal notes, advance ticket states (`In Progress`, `Resolved`), and trigger automatic SLA timestamping and audit logging.

---

## 2. API Endpoints Specification

All Agent endpoints require authentication with role `'agent'` or `'admin'` via `@role_required(['agent', 'admin'])`. Unauthorized attempts are rejected with `403 Forbidden`.

| Method | Endpoint | Request Body | Purpose |
|---|---|---|---|
| `GET` | `/api/agent/tickets` | Query params: `status_id`, `priority_id`, `category_id`, `search` | Returns the agent's assigned queue ordered by SLA urgency (`sla_hours ASC`). |
| `GET` | `/api/agent/tickets/<id>` | None | Returns full ticket details, customer contact info, SLA metrics, all public/private comments, and trigger audit history. |
| `PUT` | `/api/agent/tickets/<id>/status` | `status_id` | Transitions ticket state. Trigger auto-populates `resolved_at` if resolved, and logs to `Ticket_Status_History`. |
| `POST` | `/api/agent/tickets/<id>/resolve` | `resolution_notes` (optional) | Convenience endpoint that sets status to `Resolved` and appends resolution comments. |
| `POST` | `/api/agent/tickets/<id>/comments` | `comment_text`, `is_internal` (boolean) | Posts a public reply to the customer (`is_internal=False`) or a private diagnostic note for staff (`is_internal=True`). |

---

## 3. Privacy & Internal Notes Security

* **Staff Collaboration:** Support agents can post internal diagnostics (e.g. *"Suspecting switch loop on VLAN 20"*) with `is_internal = TRUE`.
* **Zero Leakage:** In `customer_controller.py`, customer queries explicitly execute `WHERE is_internal = FALSE`. In our test suite, we verified:
  - Agent sees **4 comments** (including internal notes).
  - Customer sees only **2 comments** (zero internal notes leaked).

---

## 4. Database Trigger Lifecycle Verification

When an agent resolves a ticket via `/api/agent/tickets/<id>/resolve`:
1. The backend issues a standard SQL `UPDATE Tickets SET status_id = 3 WHERE ticket_id = %s;`.
2. Database trigger `trg_Ticket_Status_Resolved_Timestamp` fires **BEFORE UPDATE** and automatically stamps `resolved_at = 2026-09-20 21:21:10`.
3. Database trigger `trg_Ticket_Status_History_Log` fires **AFTER UPDATE** and automatically appends an audit row to `Ticket_Status_History`:
   `Status transitioned from Open to Resolved`.

---

## 5. Test Verification Results

| # | Test Scenario | Route & Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|:---:|
| **1** | Unauthenticated Access | `GET /api/agent/tickets` | `401 Unauthorized` | `401 Unauthorized` | **PASS** |
| **2** | Customer Access Rejection | `GET /api/agent/tickets` as Customer | `403 Forbidden` | `403 Forbidden` | **PASS** |
| **3** | Agent Queue Retrieval | `GET /api/agent/tickets` as Agent | `200 OK`, assigned tickets returned | `200 OK`, 8 tickets returned | **PASS** |
| **4** | Post Internal Note | `POST /api/agent/tickets/<id>/comments` (`is_internal: true`) | `201 Created` | `201 Created` | **PASS** |
| **5** | Agent Comment Inspection | `GET /api/agent/tickets/<id>` | Sees internal notes | Internal notes present | **PASS** |
| **6** | Customer Privacy Check | `GET /api/customer/tickets/<id>` | Internal notes hidden | Internal notes leaked: `False` | **PASS** |
| **7** | Ticket Resolution | `POST /api/agent/tickets/<id>/resolve` | `200 OK`, status updated | `200 OK` | **PASS** |
| **8** | Trigger Timestamping Check | Inspect `resolved_at` in DB | Auto-populated by trigger | `resolved_at = 2026-09-20 21:21:10` | **PASS** |
| **9** | Trigger History Check | Inspect `Ticket_Status_History` | Transition logged | Logged: `Open to Resolved` | **PASS** |

---

## 6. Viva Defense Questions & Answers

* **Q: How does the system guarantee that `resolved_at` cannot be spoofed or forgotten?**
  * **Answer:** By delegating resolution timestamping to the database trigger `trg_Ticket_Status_Resolved_Timestamp`. The trigger checks if `NEW.status_id` corresponds to `Resolved` and automatically assigns `NEW.resolved_at = NOW()`. Even if an update query does not pass a timestamp, the database engine enforces it at the storage layer.
* **Q: Why does the agent queue sort by `p.sla_hours ASC, t.created_at ASC`?**
  * **Answer:** This implements **SLA-driven priority dispatching**. Tickets with tighter resolution deadlines (e.g. Critical 4h SLA) appear at the top of the queue before Medium (48h) or Low (72h) tickets, ensuring agents address high-urgency incidents first.
