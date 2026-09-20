# Phase 12: Database Views Documentation

## 1. Overview
A **Database View** is a virtual, logical table derived from the result of a predefined SQL query. Views do not store duplicate data on disk; instead, the RDBMS dynamically generates the result set when the view is queried.

This document details the three core views created for the **Customer Support Ticket Management System**, explains their operational rationale, and provides answers for viva defense.

---

## 2. Views Catalog

| View Name | Primary Beneficiaries | Base Tables Joined | Business Purpose |
|---|---|---|---|
| **`vw_OpenTickets`** | Support Agents, System Admins | `Tickets`, `Users`, `Categories`, `Priorities`, `Ticket_Status` | Unified queue of active tickets displaying customer info, elapsed ticket age in hours, and SLA breach warning indicators. |
| **`vw_AgentTicketSummary`** | System Admins, Management | `Users`, `Tickets`, `Ticket_Status` | Real-time performance summary displaying assigned tickets, active in-progress count, completed count, and mean resolution hours per agent. |
| **`vw_CustomerTicketHistory`** | Customers, Support Agents | `Tickets`, `Users`, `Categories`, `Priorities`, `Ticket_Status`, `Ticket_Comments` | Consolidated ticket history for customer portals and detail views, showing aggregated comment counts and resolution timestamps. |

---

## 3. View Definitions & SQL Implementation

### 1. `vw_OpenTickets`
```sql
CREATE VIEW vw_OpenTickets AS
SELECT 
    t.ticket_id,
    t.subject,
    t.description,
    c.user_id AS customer_id,
    c.name AS customer_name,
    c.email AS customer_email,
    cat.category_id,
    cat.category_name,
    p.priority_id,
    p.priority_name,
    p.sla_hours,
    s.status_id,
    s.status_name,
    t.assigned_agent_id,
    COALESCE(a.name, 'Unassigned') AS agent_name,
    COALESCE(a.email, 'N/A') AS agent_email,
    t.created_at,
    ROUND(TIMESTAMPDIFF(MINUTE, t.created_at, NOW()) / 60.0, 1) AS ticket_age_hours,
    CASE 
        WHEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) > p.sla_hours THEN 'SLA BREACHED'
        WHEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) > (p.sla_hours * 0.75) THEN 'SLA WARNING'
        ELSE 'WITHIN SLA'
    END AS sla_status
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
JOIN Ticket_Status s ON t.status_id = s.status_id
LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
WHERE s.is_closed = FALSE;
```

---

### 2. `vw_AgentTicketSummary`
```sql
CREATE VIEW vw_AgentTicketSummary AS
SELECT 
    a.user_id AS agent_id,
    a.name AS agent_name,
    a.email AS agent_email,
    a.contact_number,
    COUNT(t.ticket_id) AS total_assigned,
    SUM(CASE WHEN s.status_name = 'In Progress' THEN 1 ELSE 0 END) AS active_in_progress,
    SUM(CASE WHEN s.status_name = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,
    SUM(CASE WHEN s.status_name = 'Closed' THEN 1 ELSE 0 END) AS closed_count,
    ROUND(COALESCE(AVG(TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0), 0), 2) AS avg_resolution_hours
FROM Users a
LEFT JOIN Tickets t ON a.user_id = t.assigned_agent_id
LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
WHERE a.role = 'agent'
GROUP BY a.user_id, a.name, a.email, a.contact_number;
```

---

### 3. `vw_CustomerTicketHistory`
```sql
CREATE VIEW vw_CustomerTicketHistory AS
SELECT 
    t.ticket_id,
    t.customer_id,
    c.name AS customer_name,
    c.email AS customer_email,
    t.subject,
    cat.category_name,
    p.priority_name,
    s.status_name,
    s.is_closed,
    COALESCE(a.name, 'Unassigned') AS agent_name,
    t.created_at,
    t.updated_at,
    t.resolved_at,
    COUNT(tc.comment_id) AS total_comments,
    MAX(tc.created_at) AS last_comment_at
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
JOIN Ticket_Status s ON t.status_id = s.status_id
LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
LEFT JOIN Ticket_Comments tc ON t.ticket_id = tc.ticket_id
GROUP BY 
    t.ticket_id, t.customer_id, c.name, c.email, t.subject, 
    cat.category_name, p.priority_name, s.status_name, s.is_closed,
    a.name, t.created_at, t.updated_at, t.resolved_at;
```

---

## 4. Viva Defense Questions & Answers

* **Q: What is a View and how is it different from a Base Table?**
  * **Answer:** A base table physically stores data records on disk as tuples. A view is a stored SQL query (a virtual table) that does not duplicate storage; every time a view is queried, the DBMS executes its underlying `SELECT` statement dynamically against current base table rows.
* **Q: Why are views important in this project?**
  * **Answer:**
    1. **Complexity Abstraction:** The backend application can simply write `SELECT * FROM vw_OpenTickets WHERE category_id = 3` instead of writing an extensive 5-table join repeatedly.
    2. **Security & Data Privacy:** Views expose only necessary columns, withholding sensitive attributes like `password_hash` from customer or agent queries.
    3. **Consistency:** Centralizes business logic (such as calculating ticket age and SLA breach thresholds) directly inside the database, preventing discrepancies across different client interfaces.
* **Q: Can you perform `INSERT` or `UPDATE` on these views?**
  * **Answer:** Generally, views containing aggregate functions (`COUNT`, `AVG`, `SUM`), `GROUP BY` clauses, or outer joins (`LEFT JOIN`) are non-updatable in MySQL because the DBMS cannot deterministically trace an aggregate modification back to a single base table row. These views are specifically designed for high-performance reporting and reading.

