# Phase 10: CRUD Testing & Referential Integrity Verification Report

## 1. Overview
This document records the formal verification results for Create, Read, Update, and Delete (CRUD) operations, along with Foreign Key referential integrity actions (`ON DELETE CASCADE` and `ON DELETE RESTRICT`).

---

## 2. Test Cases & Execution Results

### Test Case 1: Create User
* **Feature:** User Creation (Customer)
* **Input:** `Name: 'David Miller'`, `Email: 'david@customer.com'`, `Role: 'customer'`
* **Expected Output:** Row inserted into `Users`, `user_id = 7` generated.
* **Actual Output:** Row successfully inserted; unique email constraint validated.
* **Status:** **PASS**

---

### Test Case 2: Create Support Ticket
* **Feature:** Support Ticket Submission
* **Input:** `customer_id: 4 (Alice)`, `category_id: 3 (Network)`, `priority_id: 3 (High)`, `status_id: 1 (Open)`, `subject: 'WiFi drops repeatedly in Conference Room B'`
* **Expected Output:** Ticket row generated with `ticket_id = 1` and foreign keys validated.
* **Actual Output:** `ticket_id = 1` generated with default timestamps.
* **Status:** **PASS**

---

### Test Case 3: Create Threaded Comments
* **Feature:** Activity / Comment Logging
* **Input:** `ticket_id: 1`, `user_id: 2 (Agent Sarah)`, `comment_text: 'Checking AP log metrics'`, `is_internal: FALSE`
* **Expected Output:** Comment inserted and linked to Ticket 1.
* **Actual Output:** Comment created with `comment_id = 1` linked to `ticket_id = 1`.
* **Status:** **PASS**

---

### Test Case 4: Read Tickets with Relational JOINs
* **Feature:** Relational Query with Multi-Table Joins
* **Input:** `SELECT` joining `Tickets`, `Users` (as Customer), `Categories`, `Priorities`, `Ticket_Status`, and `Users` (as Agent via `LEFT JOIN`)
* **Expected Output:** Readable table showing customer names, category names, status names, and agent names.
* **Actual Output:** Correctly returned all active tickets with human-readable attributes.
* **Status:** **PASS**

---

### Test Case 5: Update Ticket Assignment & Status
* **Feature:** Agent Assignment and State Transition
* **Input:** `UPDATE Tickets SET assigned_agent_id = 2, status_id = 2 WHERE ticket_id = 1`
* **Expected Output:** Ticket 1 assigned to Sarah Jenkins and moved to `In Progress`.
* **Actual Output:** 1 row affected; fields updated cleanly.
* **Status:** **PASS**

---

### Test Case 6: Referential Integrity — ON DELETE CASCADE
* **Feature:** Automatic child record cleanup on parent deletion
* **Input:**
  1. Insert temporary Ticket #4.
  2. Insert child Comment #4 referencing Ticket #4.
  3. Delete parent Ticket #4 (`DELETE FROM Tickets WHERE ticket_id = 4`).
* **Expected Output:** Ticket #4 is deleted, and Comment #4 is automatically deleted via `ON DELETE CASCADE`.
* **Actual Output:** `SELECT * FROM Ticket_Comments WHERE ticket_id = 4` returned 0 rows.
* **Status:** **PASS**

---

### Test Case 7: Referential Integrity — ON DELETE RESTRICT
* **Feature:** Protection of parent records referenced by active child rows
* **Input:** Attempt to delete Category #3 (Network) which has active Ticket #1 referencing it (`DELETE FROM Categories WHERE category_id = 3`).
* **Expected Output:** RDBMS rejects query with Foreign Key constraint error (Error 1451).
* **Actual Output:** `ERROR 1451 (23000): Cannot delete or update a parent row: a foreign key constraint fails`.
* **Status:** **PASS**

---

## 3. Viva Defense Notes

* **Q: Why does deleting a category fail while deleting a ticket succeeds in deleting comments?**
  * **Answer:** Because different referential actions were designed based on business rules:
    - `Categories` $\rightarrow$ `Tickets` uses `ON DELETE RESTRICT` to protect active tickets from losing their categorization and breaking reporting integrity.
    - `Tickets` $\rightarrow$ `Ticket_Comments` uses `ON DELETE CASCADE` because comments are subordinate to a ticket and have no valid business existence if the ticket is removed.

