# Phase 13: Stored Procedures Documentation & Test Verification

## 1. Overview
A **Stored Procedure** is a compiled sequence of SQL statements, control flow structures (`IF-ELSE`), local variables, and error exception handlers (`SIGNAL SQLSTATE`) stored directly inside the relational database engine.

This document details the 6 stored procedures developed for the **Customer Support Ticket Management System**, along with independent verification test cases and viva defenses.

---

## 2. Stored Procedures Catalog

| Procedure Name | Type | Key Parameters | Operational Purpose |
|---|---|---|---|
| **`sp_CreateTicket`** | Transactional / Mutation | `IN customer_id, category_id, priority_id, subject, description, OUT ticket_id` | Validates customer role, enforces initial status 'Open', and returns generated `ticket_id`. |
| **`sp_AssignTicket`** | Workflow / Mutation | `IN ticket_id, agent_id, assigned_by` | Validates agent qualification, assigns agent, and auto-promotes status from 'Open' to 'In Progress'. |
| **`sp_UpdateTicketStatus`** | Lifecycle / Mutation | `IN ticket_id, new_status_id, changed_by, remarks` | Validates state transition; automatically stamps `resolved_at = NOW()` when status becomes 'Resolved'. |
| **`sp_AddTicketComment`** | Audit / Activity | `IN ticket_id, user_id, comment_text, is_internal, OUT comment_id` | Inserts discussion entry and updates the parent ticket's `updated_at` timestamp. |
| **`sp_GetCustomerTickets`** | Query / Reporting | `IN customer_id` | Fetches all tickets submitted by a customer with resolved names for UI display. |
| **`sp_GetAgentTickets`** | Query / Queue | `IN agent_id, status_id (optional)` | Fetches ticket queue assigned to an agent, ordered by urgency SLA. |

---

## 3. Independent Test Results

### Test Case 1: `sp_CreateTicket` (Happy Path)
* **Input:** `customer_id: 4 (Alice)`, `category_id: 1 (Hardware)`, `priority_id: 3 (High)`, `subject: 'SP Test: Mouse laser not functioning'`, `description: 'Mouse disconnected repeatedly.'`
* **Expected Output:** New ticket created with status `Open`, returning `@new_ticket_id = 26`.
* **Actual Output:** Generated ticket ID `26` returned via OUT parameter.
* **Status:** **PASS**

### Test Case 2: `sp_CreateTicket` (Defensive Validation Failure)
* **Input:** `customer_id: 2 (Agent Sarah)`
* **Expected Output:** SQL exception thrown: `Validation Error: Invalid customer_id or user is not a customer.`
* **Actual Output:** `ERROR 1644 (45000): Validation Error: Invalid customer_id or user is not a customer.`
* **Status:** **PASS**

### Test Case 3: `sp_AssignTicket`
* **Input:** `ticket_id: 26`, `agent_id: 2 (Agent Sarah)`, `assigned_by: 1 (Admin)`
* **Expected Output:** `assigned_agent_id` updated to `2`; status auto-promoted from `Open` (1) to `In Progress` (2).
* **Actual Output:** `assigned_agent_id = 2`, `status_id = 2`.
* **Status:** **PASS**

### Test Case 4: `sp_AddTicketComment`
* **Input:** `ticket_id: 26`, `user_id: 2`, `comment_text: 'Testing SP comment addition'`, `is_internal: FALSE`
* **Expected Output:** Comment inserted, returning `@new_comment_id = 11`.
* **Actual Output:** `comment_id = 11` generated and linked to ticket 26.
* **Status:** **PASS**

### Test Case 5: `sp_UpdateTicketStatus` (Resolution Stamping)
* **Input:** `ticket_id: 26`, `new_status_id: 3 (Resolved)`, `changed_by: 2`, `remarks: 'Issue fixed via SP test'`
* **Expected Output:** `status_id = 3` and `resolved_at` populated with current timestamp.
* **Actual Output:** `status_id = 3`, `resolved_at = 2026-09-20 20:44:55`.
* **Status:** **PASS**

### Test Case 6: `sp_GetCustomerTickets` & `sp_GetAgentTickets`
* **Input:** Query customer 4 and agent 2 queues.
* **Expected Output:** Multi-row result sets ordered by date and urgency SLA.
* **Actual Output:** Clean result sets returned matching all joined attributes.
* **Status:** **PASS**

---

## 4. Viva Defense Questions & Answers

* **Q: What is the difference between a Stored Procedure and a Function in MySQL?**
  * **Answer:**
    1. **Invocation:** A stored procedure is invoked using the `CALL` statement (e.g. `CALL sp_CreateTicket(...)`), whereas a function is invoked inline within a SQL expression (e.g. `SELECT CalculateTicketAge(ticket_id)`).
    2. **Return Value:** A function must return exactly one value via `RETURNS type` and cannot use `OUT` parameters. A procedure does not have a formal return type, but can return multiple values using `OUT` / `INOUT` parameters or return entire result sets.
    3. **DML / Side Effects:** In standard SQL, stored procedures can freely execute `INSERT`, `UPDATE`, and `DELETE` transactions, whereas stored functions used within `SELECT` queries cannot modify database tables.
* **Q: Why use Stored Procedures rather than writing queries in application code?**
  * **Answer:**
    1. **Performance:** Eliminates multiple network round-trips; operations execute locally inside the database engine.
    2. **Security:** Protects against SQL injection by using strictly typed input parameters and prevents unauthorized users from querying raw tables directly.
    3. **Centralized Business Logic:** Business rules (e.g. auto-promoting status upon agent assignment) are enforced universally, regardless of which client or endpoint executes the action.
* **Q: What is `SIGNAL SQLSTATE '45000'` in MySQL stored procedures?**
  * **Answer:** `SQLSTATE '45000'` is the ANSI SQL standard state code for an unhandled user-defined exception. It halts execution and sends a custom, human-readable error message back to the application.

