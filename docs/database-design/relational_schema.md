# Phase 5: Relational Schema & Integrity Constraints

## 1. Overview
The Relational Schema transforms the conceptual ER Diagram into formal relational structures (relations, schemas, domains, candidate keys, primary keys, and foreign keys with referential integrity rules).

---

## 2. Formal Relational Notation

In standard relational schema notation:
* **Bold & Underline** represents a **Primary Key (PK)**.
* **Underline (Dashed) or FK** represents a **Foreign Key (FK)**.
* Arrows ($\rightarrow$) indicate referential integrity targets.

---

### 1. `Users`
$$\text{Users}(\underline{\mathbf{user\_id}}, name, email, password\_hash, role, contact\_number, created\_at)$$
* **Primary Key:** `user_id`
* **Candidate Key / Unique:** `email`
* **Domain & Check Constraints:**
  * `user_id`: INT, AUTO_INCREMENT, NOT NULL
  * `name`: VARCHAR(100), NOT NULL
  * `email`: VARCHAR(100), NOT NULL, UNIQUE
  * `password_hash`: VARCHAR(255), NOT NULL
  * `role`: VARCHAR(20), NOT NULL, `CHECK (role IN ('customer', 'agent', 'admin'))`
  * `contact_number`: VARCHAR(20), NULL
  * `created_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

---

### 2. `Categories`
$$\text{Categories}(\underline{\mathbf{category\_id}}, category\_name, description, created\_at)$$
* **Primary Key:** `category_id`
* **Candidate Key / Unique:** `category_name`
* **Domain Constraints:**
  * `category_id`: INT, AUTO_INCREMENT, NOT NULL
  * `category_name`: VARCHAR(50), NOT NULL, UNIQUE
  * `description`: VARCHAR(255), NULL
  * `created_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

---

### 3. `Priorities`
$$\text{Priorities}(\underline{\mathbf{priority\_id}}, priority\_name, sla\_hours, created\_at)$$
* **Primary Key:** `priority_id`
* **Candidate Key / Unique:** `priority_name`
* **Domain & Check Constraints:**
  * `priority_id`: INT, AUTO_INCREMENT, NOT NULL
  * `priority_name`: VARCHAR(20), NOT NULL, UNIQUE
  * `sla_hours`: INT, NOT NULL, DEFAULT 24, `CHECK (sla_hours > 0)`
  * `created_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

---

### 4. `Ticket_Status`
$$\text{Ticket\_Status}(\underline{\mathbf{status\_id}}, status\_name, is\_closed)$$
* **Primary Key:** `status_id`
* **Candidate Key / Unique:** `status_name`
* **Domain Constraints:**
  * `status_id`: INT, AUTO_INCREMENT, NOT NULL
  * `status_name`: VARCHAR(30), NOT NULL, UNIQUE
  * `is_closed`: BOOLEAN, NOT NULL, DEFAULT FALSE

---

### 5. `Tickets`
$$\text{Tickets}(\underline{\mathbf{ticket\_id}}, \text{customer\_id}, \text{category\_id}, \text{priority\_id}, \text{status\_id}, \text{assigned\_agent\_id}, subject, description, created\_at, updated\_at, resolved\_at)$$
* **Primary Key:** `ticket_id`
* **Foreign Keys & Referential Actions:**
  * `customer_id` $\rightarrow$ `Users(user_id)`: **ON DELETE RESTRICT, ON UPDATE CASCADE**
  * `category_id` $\rightarrow$ `Categories(category_id)`: **ON DELETE RESTRICT, ON UPDATE CASCADE**
  * `priority_id` $\rightarrow$ `Priorities(priority_id)`: **ON DELETE RESTRICT, ON UPDATE CASCADE**
  * `status_id` $\rightarrow$ `Ticket_Status(status_id)`: **ON DELETE RESTRICT, ON UPDATE CASCADE**
  * `assigned_agent_id` $\rightarrow$ `Users(user_id)`: **ON DELETE SET NULL, ON UPDATE CASCADE**
* **Domain Constraints:**
  * `ticket_id`: INT, AUTO_INCREMENT, NOT NULL
  * `customer_id`: INT, NOT NULL
  * `category_id`: INT, NOT NULL
  * `priority_id`: INT, NOT NULL
  * `status_id`: INT, NOT NULL
  * `assigned_agent_id`: INT, NULL
  * `subject`: VARCHAR(150), NOT NULL
  * `description`: TEXT, NOT NULL
  * `created_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
  * `updated_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
  * `resolved_at`: TIMESTAMP, NULL

---

### 6. `Ticket_Comments`
$$\text{Ticket\_Comments}(\underline{\mathbf{comment\_id}}, \text{ticket\_id}, \text{user\_id}, comment\_text, is\_internal, created\_at)$$
* **Primary Key:** `comment_id`
* **Foreign Keys & Referential Actions:**
  * `ticket_id` $\rightarrow$ `Tickets(ticket_id)`: **ON DELETE CASCADE, ON UPDATE CASCADE**
  * `user_id` $\rightarrow$ `Users(user_id)`: **ON DELETE RESTRICT, ON UPDATE CASCADE**
* **Domain Constraints:**
  * `comment_id`: INT, AUTO_INCREMENT, NOT NULL
  * `ticket_id`: INT, NOT NULL
  * `user_id`: INT, NOT NULL
  * `comment_text`: TEXT, NOT NULL
  * `is_internal`: BOOLEAN, NOT NULL, DEFAULT FALSE
  * `created_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

---

### 7. `Ticket_Status_History`
$$\text{Ticket\_Status\_History}(\underline{\mathbf{history\_id}}, \text{ticket\_id}, \text{old\_status\_id}, \text{new\_status\_id}, \text{changed\_by}, remarks, changed\_at)$$
* **Primary Key:** `history_id`
* **Foreign Keys & Referential Actions:**
  * `ticket_id` $\rightarrow$ `Tickets(ticket_id)`: **ON DELETE CASCADE, ON UPDATE CASCADE**
  * `old_status_id` $\rightarrow$ `Ticket_Status(status_id)`: **ON DELETE SET NULL, ON UPDATE CASCADE**
  * `new_status_id` $\rightarrow$ `Ticket_Status(status_id)`: **ON DELETE RESTRICT, ON UPDATE CASCADE**
  * `changed_by` $\rightarrow$ `Users(user_id)`: **ON DELETE SET NULL, ON UPDATE CASCADE**
* **Domain Constraints:**
  * `history_id`: INT, AUTO_INCREMENT, NOT NULL
  * `ticket_id`: INT, NOT NULL
  * `old_status_id`: INT, NULL (NULL for initial ticket creation event)
  * `new_status_id`: INT, NOT NULL
  * `changed_by`: INT, NULL
  * `remarks`: VARCHAR(255), NULL
  * `changed_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP

---

## 3. Integrity Constraints Summary Table

| Table | Entity Integrity (PK) | Candidate Keys (Unique) | Referential Integrity (FK) | Check Constraints |
|---|---|---|---|---|
| `Users` | `user_id` | `email` | None | `CHECK (role IN ('customer', 'agent', 'admin'))` |
| `Categories` | `category_id` | `category_name` | None | None |
| `Priorities` | `priority_id` | `priority_name` | None | `CHECK (sla_hours > 0)` |
| `Ticket_Status` | `status_id` | `status_name` | None | None |
| `Tickets` | `ticket_id` | None | `customer_id`, `category_id`, `priority_id`, `status_id`, `assigned_agent_id` | None |
| `Ticket_Comments` | `comment_id` | None | `ticket_id`, `user_id` | None |
| `Ticket_Status_History` | `history_id` | None | `ticket_id`, `old_status_id`, `new_status_id`, `changed_by` | None |

---

## 4. Referential Action Decision Justification

1. **`ON DELETE RESTRICT` (Protected Records)**:
   - Customers, Categories, Priorities, and Statuses cannot be deleted if there are tickets referencing them. This prevents orphan records and ensures audit stability.
2. **`ON DELETE CASCADE` (Dependent Records)**:
   - When a `Ticket` is purged, all of its child comments and status history entries are purged automatically. Comments have no independent meaning without their parent ticket.
3. **`ON DELETE SET NULL` (Optional Associations)**:
   - If a support agent account is deactivated/deleted, active tickets previously assigned to them should not be deleted; their `assigned_agent_id` is simply set to `NULL` so an administrator can reassign them.

---

## 5. Viva Defense Notes

* **Q: What are the three fundamental integrity constraints in the Relational Model?**
  * **Answer:**
    1. **Entity Integrity:** The primary key of a relation cannot contain NULL values and must uniquely identify each tuple.
    2. **Referential Integrity:** A foreign key in a referencing relation must either match a valid primary key value in the referenced relation or be NULL (if permitted).
    3. **Domain Integrity:** Every attribute value must conform to its declared data type, length, and check constraints (e.g., `role` must be one of `'customer'`, `'agent'`, `'admin'`).

