# Phase 15: Database Triggers Documentation & Lifecycle Audit Verification

## 1. Overview
A **Database Trigger** is an event-driven stored program that the RDBMS automatically executes (fires) whenever a specific Data Manipulation Language (DML) action (`INSERT`, `UPDATE`, or `DELETE`) occurs on a target table.

Triggers operate autonomously at the database engine level, guaranteeing that critical business rules, timestamps, and audit records are executed even if an external application developer forgets to write code for them.

This document details the 3 triggers implemented for the **Customer Support Ticket Management System**, along with test results and viva defenses.

---

## 2. Triggers Catalog

| Trigger Name | Event & Timing | Target Table | Pseudo-Records Used | Operational Purpose |
|---|---|---|---|---|
| **`trg_Ticket_Initial_History_Log`** | `AFTER INSERT` | `Tickets` | `NEW` | Automatically creates the inception record in `Ticket_Status_History` ($NULL \rightarrow Open$) upon ticket creation. |
| **`trg_Ticket_Status_Resolved_Timestamp`** | `BEFORE UPDATE` | `Tickets` | `NEW`, `OLD` | Automatically sets `NEW.resolved_at = NOW()` when status changes to 'Resolved'. Clears `resolved_at = NULL` if reopened. |
| **`trg_Ticket_Status_History_Log`** | `AFTER UPDATE` | `Tickets` | `NEW`, `OLD` | Automatically logs an immutable audit trail entry into `Ticket_Status_History` whenever `status_id` changes. |

---

## 3. Trigger Implementations

### 1. `trg_Ticket_Initial_History_Log` (AFTER INSERT)
```sql
CREATE TRIGGER trg_Ticket_Initial_History_Log
AFTER INSERT ON Tickets
FOR EACH ROW
BEGIN
    INSERT INTO Ticket_Status_History (
        ticket_id, old_status_id, new_status_id, changed_by, remarks, changed_at
    ) VALUES (
        NEW.ticket_id, NULL, NEW.status_id, NEW.customer_id, 
        'Ticket initially submitted by customer', NOW()
    );
END;
```

---

### 2. `trg_Ticket_Status_Resolved_Timestamp` (BEFORE UPDATE)
```sql
CREATE TRIGGER trg_Ticket_Status_Resolved_Timestamp
BEFORE UPDATE ON Tickets
FOR EACH ROW
BEGIN
    DECLARE v_resolved_status_id INT;
    SELECT status_id INTO v_resolved_status_id FROM Ticket_Status WHERE status_name = 'Resolved' LIMIT 1;

    -- If status transitioned to Resolved, automatically stamp resolved_at
    IF NEW.status_id = v_resolved_status_id AND (OLD.status_id <> v_resolved_status_id OR OLD.status_id IS NULL) THEN
        IF NEW.resolved_at IS NULL THEN
            SET NEW.resolved_at = NOW();
        END IF;
    -- If reopened, clear timestamp
    ELSEIF OLD.status_id = v_resolved_status_id AND NEW.status_id <> v_resolved_status_id THEN
        SET NEW.resolved_at = NULL;
    END IF;
END;
```

---

### 3. `trg_Ticket_Status_History_Log` (AFTER UPDATE)
```sql
CREATE TRIGGER trg_Ticket_Status_History_Log
AFTER UPDATE ON Tickets
FOR EACH ROW
BEGIN
    DECLARE v_old_status_name VARCHAR(30);
    DECLARE v_new_status_name VARCHAR(30);

    IF OLD.status_id <> NEW.status_id THEN
        SELECT status_name INTO v_old_status_name FROM Ticket_Status WHERE status_id = OLD.status_id;
        SELECT status_name INTO v_new_status_name FROM Ticket_Status WHERE status_id = NEW.status_id;

        INSERT INTO Ticket_Status_History (
            ticket_id, old_status_id, new_status_id, changed_by, remarks, changed_at
        ) VALUES (
            NEW.ticket_id, OLD.status_id, NEW.status_id, NEW.assigned_agent_id,
            CONCAT('Status transitioned from ', COALESCE(v_old_status_name, 'Unknown'), ' to ', v_new_status_name),
            NOW()
        );
    END IF;
END;
```

---

## 4. End-to-End Test Verification

We performed a complete lifecycle test on a single ticket:

1. **Ticket Creation (`INSERT`)**:
   - Ticket #28 submitted with status `Open`.
   - `trg_Ticket_Initial_History_Log` fired immediately.
   - Verified row in `Ticket_Status_History`: `old_status: NULL`, `new_status: 1`, `remarks: 'Ticket initially submitted by customer'`.
2. **First State Transition (`UPDATE` to In Progress)**:
   - `status_id` updated to `2` (In Progress).
   - `trg_Ticket_Status_History_Log` fired.
   - Verified second row in `Ticket_Status_History`: `old_status: 1`, `new_status: 2`, `remarks: 'Status transitioned from Open to In Progress'`.
3. **Resolution State Transition (`UPDATE` to Resolved)**:
   - Executed simple query: `UPDATE Tickets SET status_id = 3 WHERE ticket_id = 28;` (Note: query did *not* specify `resolved_at`).
   - `trg_Ticket_Status_Resolved_Timestamp` fired `BEFORE UPDATE` and set `resolved_at = 2026-09-20 20:49:26`.
   - `trg_Ticket_Status_History_Log` fired `AFTER UPDATE` and created third row in `Ticket_Status_History`: `old_status: 2`, `new_status: 3`, `remarks: 'Status transitioned from In Progress to Resolved'`.

**Status:** **100% PASS on all lifecycle milestones.**

---

## 5. Viva Defense Questions & Answers

* **Q: What is the difference between `BEFORE` and `AFTER` triggers?**
  * **Answer:**
    - A `BEFORE` trigger executes *before* data is physically written to disk. It is ideal for validating inputs or altering values on the incoming row (e.g. `SET NEW.resolved_at = NOW()`).
    - An `AFTER` trigger executes *after* the base table change has succeeded. It is ideal for logging audit trails into secondary tables (e.g. `Ticket_Status_History`), ensuring the primary change succeeded before logging it.
* **Q: What are the `NEW` and `OLD` pseudo-records?**
  * **Answer:**
    - `NEW`: Contains the column values of the record being inserted or updated. (Available in `INSERT` and `UPDATE`).
    - `OLD`: Contains the original column values before the update or deletion. (Available in `UPDATE` and `DELETE`).
* **Q: Why is audit logging implemented via Triggers rather than in application code?**
  * **Answer:** Guarantee of compliance and tamper resistance. If audit logging is in backend code, a developer writing a new script, direct SQL update, or batch migration might forget to call the audit log function. A database trigger intercepts *any* modification regardless of where the query originated.

