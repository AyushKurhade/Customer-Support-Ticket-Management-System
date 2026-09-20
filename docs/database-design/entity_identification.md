# Phase 3: Entity Identification & Attribute Mapping

## 1. Overview
This document defines all 7 core entities for the **Customer Support Ticket Management System**. Each entity is mapped to its real-world domain concept, primary and candidate keys, foreign key relationships, data types, constraints, and operational business purpose.

No extraneous tables are introduced, keeping the schema strictly normalized and purposeful.

---

## 2. Identified Entities & Domain Classification

| Entity Name | Domain Classification | Operational Role |
|---|---|---|
| **Users** | Core Identity | Stores customers, support agents, and admins with role-based access. |
| **Categories** | Master / Reference Data | Predefined IT support domains (Hardware, Software, Network, etc.). |
| **Priorities** | Master / Reference Data | Urgency levels (Low, Medium, High, Critical) with target SLA resolution hours. |
| **Ticket_Status** | Master / Reference Data | Lifecycle states (Open, In Progress, Resolved, Closed). |
| **Tickets** | Core Transactional Entity | Central record capturing the customer's issue, assignment, and status. |
| **Ticket_Comments** | Activity / Communication | Timestamped conversation thread between customer and agent. |
| **Ticket_Status_History** | Audit Log / Event Entity | Immutable log of status changes automatically populated via DB triggers. |

---

## 3. Detailed Entity Attribute Specifications

### 1. `Users` Entity
* **Description:** Represents all human actors accessing the system.
* **Attributes:**
  * `user_id` (INT, AUTO_INCREMENT) — **Primary Key**
  * `name` (VARCHAR(100), NOT NULL) — Full name of the user
  * `email` (VARCHAR(100), NOT NULL, UNIQUE) — **Candidate Key**; login identifier
  * `password_hash` (VARCHAR(255), NOT NULL) — Hashed credential string (bcrypt / pbkdf2)
  * `role` (VARCHAR(20), NOT NULL) — **Check Constraint**: `CHECK (role IN ('customer', 'agent', 'admin'))`
  * `contact_number` (VARCHAR(20), NULL) — Contact phone
  * `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP) — Account creation timestamp

---

### 2. `Categories` Entity (Master Data)
* **Description:** IT service problem classifications used for routing and AI predictions.
* **Attributes:**
  * `category_id` (INT, AUTO_INCREMENT) — **Primary Key**
  * `category_name` (VARCHAR(50), NOT NULL, UNIQUE) — **Candidate Key** (`Hardware`, `Software`, `Network`, `Account`, `Payment`, `Technical Issue`, `Other`)
  * `description` (VARCHAR(255), NULL) — Brief scope of the category
  * `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

---

### 3. `Priorities` Entity (Master Data)
* **Description:** Urgency tiers defining resolution expectations.
* **Attributes:**
  * `priority_id` (INT, AUTO_INCREMENT) — **Primary Key**
  * `priority_name` (VARCHAR(20), NOT NULL, UNIQUE) — **Candidate Key** (`Low`, `Medium`, `High`, `Critical`)
  * `sla_hours` (INT, NOT NULL, DEFAULT 24) — Target resolution window in hours for SLA metrics
  * `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

---

### 4. `Ticket_Status` Entity (Master Data)
* **Description:** Allowed lifecycle phases in the ticket state machine.
* **Attributes:**
  * `status_id` (INT, AUTO_INCREMENT) — **Primary Key**
  * `status_name` (VARCHAR(30), NOT NULL, UNIQUE) — **Candidate Key** (`Open`, `In Progress`, `Resolved`, `Closed`)
  * `is_closed` (BOOLEAN, DEFAULT FALSE) — Flag indicating whether the status represents a finished state

---

### 5. `Tickets` Entity (Core Transactional Table)
* **Description:** The central entity tracking the customer's problem and lifecycle.
* **Attributes:**
  * `ticket_id` (INT, AUTO_INCREMENT) — **Primary Key**
  * `customer_id` (INT, NOT NULL) — **Foreign Key** $\rightarrow$ `Users(user_id)` (ON DELETE RESTRICT)
  * `category_id` (INT, NOT NULL) — **Foreign Key** $\rightarrow$ `Categories(category_id)` (ON DELETE RESTRICT)
  * `priority_id` (INT, NOT NULL) — **Foreign Key** $\rightarrow$ `Priorities(priority_id)` (ON DELETE RESTRICT)
  * `status_id` (INT, NOT NULL) — **Foreign Key** $\rightarrow$ `Ticket_Status(status_id)` (ON DELETE RESTRICT)
  * `assigned_agent_id` (INT, NULL) — **Foreign Key** $\rightarrow$ `Users(user_id)` (ON DELETE SET NULL)
  * `subject` (VARCHAR(150), NOT NULL) — Brief headline of the issue
  * `description` (TEXT, NOT NULL) — Complete details (used by AI model for classification)
  * `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP) — Submission time
  * `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
  * `resolved_at` (TIMESTAMP, NULL) — Automatically populated when `status_id` transitions to `Resolved`

---

### 6. `Ticket_Comments` Entity (Activity / Communication)
* **Description:** Conversation trail between customer, assigned agent, and admin.
* **Attributes:**
  * `comment_id` (INT, AUTO_INCREMENT) — **Primary Key**
  * `ticket_id` (INT, NOT NULL) — **Foreign Key** $\rightarrow$ `Tickets(ticket_id)` (ON DELETE CASCADE)
  * `user_id` (INT, NOT NULL) — **Foreign Key** $\rightarrow$ `Users(user_id)` (ON DELETE RESTRICT)
  * `comment_text` (TEXT, NOT NULL) — Message body
  * `is_internal` (BOOLEAN, DEFAULT FALSE) — True for agent-only notes, False for public dialogue
  * `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

---

### 7. `Ticket_Status_History` Entity (Audit Trail)
* **Description:** Immutable record of all status changes for compliance and SLA tracking.
* **Attributes:**
  * `history_id` (INT, AUTO_INCREMENT) — **Primary Key**
  * `ticket_id` (INT, NOT NULL) — **Foreign Key** $\rightarrow$ `Tickets(ticket_id)` (ON DELETE CASCADE)
  * `old_status_id` (INT, NULL) — **Foreign Key** $\rightarrow$ `Ticket_Status(status_id)` (NULL upon initial creation)
  * `new_status_id` (INT, NOT NULL) — **Foreign Key** $\rightarrow$ `Ticket_Status(status_id)`
  * `changed_by` (INT, NULL) — **Foreign Key** $\rightarrow$ `Users(user_id)` (User who made the change)
  * `changed_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP) — Exact timestamp of state change
  * `remarks` (VARCHAR(255), NULL) — Optional explanation of status transition

---

## 4. Entity Relationship Overview

```
Users (Customer) ──(1:N)──► Tickets
Users (Agent)    ──(0:1..N)► Tickets
Categories       ──(1:N)──► Tickets
Priorities       ──(1:N)──► Tickets
Ticket_Status    ──(1:N)──► Tickets
Tickets          ──(1:N)──► Ticket_Comments
Users            ──(1:N)──► Ticket_Comments
Tickets          ──(1:N)──► Ticket_Status_History
Ticket_Status    ──(1:N)──► Ticket_Status_History (as old_status & new_status)
```

---

## 5. Viva Defense Notes

* **Q: Why are `customer_id` and `assigned_agent_id` both referencing the `Users` table instead of having separate `Customers` and `Agents` tables?**
  * **Answer:** Both customers and agents share identical core identity properties (name, email, password, authentication logic). Splitting them into duplicate tables violates the DRY principle and forces redundant tables. Distinguishing them via a `role` attribute with a `CHECK (role IN ('customer', 'agent', 'admin'))` constraint is standard 3NF practice and models role-based specialization cleanly.
* **Q: Why use `ON DELETE RESTRICT` for `customer_id` on `Tickets`, but `ON DELETE CASCADE` for `Tickets` on `Ticket_Comments`?**
  * **Answer:** A customer who has active tickets must never be silently deleted, as doing so destroys historical support audit data (`RESTRICT`). Conversely, if a ticket is legitimately purged, its comments and history logs have no independent meaning and should be cleaned up automatically (`CASCADE`).

