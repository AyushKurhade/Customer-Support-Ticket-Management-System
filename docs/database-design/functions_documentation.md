# Phase 14: Database Functions Documentation & Test Verification

## 1. Overview
A **User-Defined Function (UDF)** in SQL is a database routine that accepts parameters, executes computational logic, and returns a **single scalar value**.

Unlike Stored Procedures, Functions can be invoked directly inside `SELECT`, `WHERE`, and `ORDER BY` clauses to compute dynamic, derived values without altering table data.

This document details the 3 functions implemented for the **Customer Support Ticket Management System**, along with test results and viva defenses.

---

## 2. Functions Catalog

| Function Name | Returns | SQL Characteristics | Business & Analytical Purpose |
|---|---|---|---|
| **`fn_CalculateTicketAge`** | `DECIMAL(10,2)` | `READS SQL DATA`, `DETERMINISTIC` | Computes the elapsed lifespan of a ticket in hours from creation until resolution (or until current time if active). |
| **`fn_CalculateResolutionTime`** | `DECIMAL(10,2)` | `READS SQL DATA`, `DETERMINISTIC` | Computes the exact duration in hours taken by support agents to resolve a ticket. Returns `NULL` if still active. |
| **`fn_GetSLAStatus`** | `VARCHAR(25)` | `READS SQL DATA`, `DETERMINISTIC` | Evaluates SLA compliance, returning `'WITHIN SLA'`, `'SLA WARNING'`, `'SLA BREACHED'`, or `'RESOLVED ON TIME'` / `'RESOLVED LATE'`. |

---

## 3. Function Implementations

### 1. `fn_CalculateTicketAge`
```sql
CREATE FUNCTION fn_CalculateTicketAge (p_ticket_id INT) 
RETURNS DECIMAL(10, 2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_created_at TIMESTAMP;
    DECLARE v_resolved_at TIMESTAMP;
    DECLARE v_end_time TIMESTAMP;
    DECLARE v_age_hours DECIMAL(10, 2);

    SELECT created_at, resolved_at 
    INTO v_created_at, v_resolved_at
    FROM Tickets 
    WHERE ticket_id = p_ticket_id;

    IF v_created_at IS NULL THEN RETURN NULL; END IF;

    IF v_resolved_at IS NOT NULL THEN
        SET v_end_time = v_resolved_at;
    ELSE
        SET v_end_time = NOW();
    END IF;

    SET v_age_hours = ROUND(TIMESTAMPDIFF(MINUTE, v_created_at, v_end_time) / 60.0, 2);
    RETURN v_age_hours;
END;
```

---

### 2. `fn_CalculateResolutionTime`
```sql
CREATE FUNCTION fn_CalculateResolutionTime (p_ticket_id INT) 
RETURNS DECIMAL(10, 2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_created_at TIMESTAMP;
    DECLARE v_resolved_at TIMESTAMP;
    DECLARE v_res_hours DECIMAL(10, 2);

    SELECT created_at, resolved_at 
    INTO v_created_at, v_resolved_at
    FROM Tickets 
    WHERE ticket_id = p_ticket_id;

    IF v_created_at IS NULL OR v_resolved_at IS NULL THEN RETURN NULL; END IF;

    SET v_res_hours = ROUND(TIMESTAMPDIFF(MINUTE, v_created_at, v_resolved_at) / 60.0, 2);
    RETURN v_res_hours;
END;
```

---

### 3. `fn_GetSLAStatus`
```sql
CREATE FUNCTION fn_GetSLAStatus (p_ticket_id INT)
RETURNS VARCHAR(25)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_created_at TIMESTAMP;
    DECLARE v_resolved_at TIMESTAMP;
    DECLARE v_sla_hours INT;
    DECLARE v_elapsed_hours DECIMAL(10, 2);

    SELECT t.created_at, t.resolved_at, p.sla_hours
    INTO v_created_at, v_resolved_at, v_sla_hours
    FROM Tickets t
    JOIN Priorities p ON t.priority_id = p.priority_id
    WHERE t.ticket_id = p_ticket_id;

    IF v_created_at IS NULL THEN RETURN 'TICKET NOT FOUND'; END IF;

    IF v_resolved_at IS NOT NULL THEN
        SET v_elapsed_hours = TIMESTAMPDIFF(MINUTE, v_created_at, v_resolved_at) / 60.0;
        IF v_elapsed_hours <= v_sla_hours THEN
            RETURN 'RESOLVED ON TIME';
        ELSE
            RETURN 'RESOLVED LATE';
        END IF;
    END IF;

    SET v_elapsed_hours = TIMESTAMPDIFF(MINUTE, v_created_at, NOW()) / 60.0;
    IF v_elapsed_hours > v_sla_hours THEN
        RETURN 'SLA BREACHED';
    ELSEIF v_elapsed_hours > (v_sla_hours * 0.75) THEN
        RETURN 'SLA WARNING';
    ELSE
        RETURN 'WITHIN SLA';
    END IF;
END;
```

---

## 4. Test Verification in Queries

```sql
SELECT 
    ticket_id, 
    subject, 
    fn_CalculateTicketAge(ticket_id) AS age_hrs, 
    fn_CalculateResolutionTime(ticket_id) AS res_hrs, 
    fn_GetSLAStatus(ticket_id) AS sla_state 
FROM Tickets 
LIMIT 5;
```

### Verified Query Results:
* **Active Ticket within SLA:** Ticket #1 $\rightarrow$ `age_hrs: 0.20`, `res_hrs: NULL`, `sla_state: WITHIN SLA`
* **Resolved on Time Ticket:** Ticket #12 $\rightarrow$ `age_hrs: 24.00`, `res_hrs: 24.00`, `sla_state: RESOLVED ON TIME`
* **Critical Ticket breaching SLA:** Ticket #14 (4h Critical SLA, active for 4.13 hrs) $\rightarrow$ `sla_state: SLA BREACHED`

---

## 5. Viva Defense Questions & Answers

* **Q: When would you choose a Function over a Stored Procedure?**
  * **Answer:** Use a **Function** when you need to calculate and return a scalar value that will be embedded directly inside `SELECT`, `WHERE`, or `ORDER BY` clauses (such as formatting timestamps, computing SLA compliance tags, or deriving mathematical scores). Use a **Procedure** when executing operations that perform table mutations (`INSERT`, `UPDATE`, `DELETE`), return multiple result sets, or require transactions.
* **Q: Why are `DETERMINISTIC` and `READS SQL DATA` declared on these functions?**
  * **Answer:** In MySQL, specifying `READS SQL DATA` informs the storage engine that the function reads database rows without modifying them. `DETERMINISTIC` tells the query optimizer whether the function consistently produces identical output given identical inputs, enabling execution caching and binary log safety.

