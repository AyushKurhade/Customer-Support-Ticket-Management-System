# Phase 16: Database Transactions & ACID Verification Documentation

## 1. Overview
A **Database Transaction** is a single Logical Unit of Work (LUW) consisting of one or more SQL operations that must be executed in an **all-or-nothing** manner.

If every operation within the transaction succeeds, the changes are made permanent via `COMMIT`. If any operation fails, encounters an exception, or violates an integrity rule, all preceding modifications are completely reverted via `ROLLBACK`, leaving the database in its original consistent state.

---

## 2. ACID Properties Mapping to This Project

| ACID Property | Formal DBMS Definition | How Demonstrated in This Project |
|---|---|---|
| **Atomicity** | "All or Nothing." An entire transaction executes completely or has no effect at all. | When transferring a ticket (`sp_SafeTicketTransfer`), changing the assigned agent and logging the handover comment succeed together. If an error occurs midway, `ROLLBACK` undoes the agent reassignment immediately. |
| **Consistency** | The database transitions from one valid state to another, preserving all declared constraints. | Enforces foreign keys (`customer_id`, `category_id`), unique emails, and check constraints (`role IN (...)`). A transaction cannot leave orphan records or invalid foreign keys. |
| **Isolation** | Concurrent transactions execute as if they were running serially without interference. | Managed by MySQL InnoDB engine using multi-version concurrency control (MVCC) and row-level locks, preventing dirty reads while agents resolve tickets. |
| **Durability** | Once a transaction is committed, its modifications survive crashes, reboots, or power failures. | InnoDB write-ahead redo logs (WAL) guarantee that `COMMIT` persists records to disk permanently. |

---

## 3. SQL Implementation & Scenarios

### Scenario A: Successful Multi-Step Transaction (`COMMIT`)
```sql
START TRANSACTION;

-- Step 1: Reassign agent
UPDATE Tickets SET assigned_agent_id = 3 WHERE ticket_id = 1;

-- Step 2: Escalate priority
UPDATE Tickets SET priority_id = 3 WHERE ticket_id = 1;

-- Step 3: Insert handover audit comment
INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal)
VALUES (1, 1, 'Admin Handover: Transferred ticket with priority escalation.', TRUE);

-- Commit all 3 changes atomically
COMMIT;
```

---

### Scenario B: Defensive Exception Handling (`ROLLBACK`)
```sql
CREATE PROCEDURE sp_SafeTicketTransfer (
    IN p_ticket_id INT,
    IN p_new_agent_id INT,
    IN p_simulated_error BOOLEAN,
    OUT p_result_status VARCHAR(100)
)
BEGIN
    -- Automatically rollback on any SQL error
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result_status = 'TRANSACTION FAILED: Error detected, rolled back all changes.';
    END;

    START TRANSACTION;

    -- Operation 1: Reassign agent
    UPDATE Tickets SET assigned_agent_id = p_new_agent_id WHERE ticket_id = p_ticket_id;

    -- Operation 2: Check for error condition
    IF p_simulated_error = TRUE THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Simulated system failure during transfer.';
    ELSE
        INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal)
        VALUES (p_ticket_id, p_new_agent_id, 'Transfer confirmed and accepted by agent.', TRUE);
        
        COMMIT;
        SET p_result_status = 'TRANSACTION SUCCESS: Ticket transferred and logged.';
    END IF;
END;
```

---

## 4. Test Verification Results

| Test Execution | Input Parameters | Expected State | Actual State | Status |
|---|---|---|---|:---:|
| **Initial State** | Inspect Ticket #3 | `assigned_agent_id = NULL` | `assigned_agent_id = NULL` | **PASS** |
| **Simulated Failure** | `sp_SafeTicketTransfer(3, 2, TRUE, @res)` | Error caught, `ROLLBACK` triggered. `assigned_agent_id` remains `NULL`. | Output: `TRANSACTION FAILED: Error detected, rolled back all changes.`<br>`assigned_agent_id = NULL` | **PASS** |
| **Normal Execution** | `sp_SafeTicketTransfer(3, 2, FALSE, @res)` | Operations execute, `COMMIT` triggered. `assigned_agent_id` becomes `2`. | Output: `TRANSACTION SUCCESS: Ticket transferred and logged.`<br>`assigned_agent_id = 2` | **PASS** |

---

## 5. Viva Defense Questions & Answers

* **Q: What is a Transaction and what are the ACID properties?**
  * **Answer:** A transaction is an atomic sequence of database operations treated as a single logical unit. It adheres to ACID:
    - **A (Atomicity):** All operations succeed or all are rolled back.
    - **C (Consistency):** Database invariants and constraints are preserved before and after execution.
    - **I (Isolation):** Transactions execute independently without intermediate interference.
    - **D (Durability):** Committed updates are permanent and survive system restarts.
* **Q: How does MySQL implement Rollback?**
  * **Answer:** MySQL's InnoDB storage engine uses an **Undo Log**. When an `UPDATE` or `INSERT` runs inside a transaction, the before-image of the modified data is written to the undo log. If `ROLLBACK` is issued or an unhandled exception occurs, InnoDB reads the undo log in reverse to restore the exact original bytes on disk.
* **Q: Why are transactions necessary for ticket reassignment in this system?**
  * **Answer:** Reassigning a ticket involves modifying the ticket row (`UPDATE Tickets`) and writing an internal handover note (`INSERT INTO Ticket_Comments`). If the network or server fails between these two statements, without a transaction the ticket would show a new agent but have zero explanation or audit history. Transactions ensure both operations succeed together or neither occurs.

