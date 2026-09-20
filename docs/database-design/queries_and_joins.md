# Phase 11: SQL Queries, Relational Joins, Aggregations & Subqueries

## 1. Overview
This document showcases all 12 core SQL queries designed to demonstrate practical relational database querying, multi-table joins, aggregate functions, filtering, grouping, date arithmetic, and nested subqueries in the **Customer Support Ticket Management System**.

---

## 2. Query Catalog & Concept Mapping

| # | Query Objective | DBMS Concepts Demonstrated | Output Summary |
|---|---|---|---|
| **Q1** | Show all Open tickets | `SELECT`, `WHERE`, `INNER JOIN`, `ORDER BY` | Lists all unassigned/open tickets sorted by urgency. |
| **Q2** | Filter tickets by Category ('Network') | `INNER JOIN`, string equality `WHERE` | Retrieves tickets classified under Network. |
| **Q3** | Filter tickets by Assigned Agent | Multi-table `JOIN`, Foreign Key filtering | Retrieves tickets handled by Agent Sarah Jenkins. |
| **Q4** | Count tickets per category | `GROUP BY`, `COUNT()`, `LEFT JOIN` | Shows ticket volume per category (includes categories with 0). |
| **Q5** | Count tickets per priority with SLA | `GROUP BY`, `COUNT()`, `ORDER BY` | Categorizes workload by SLA urgency level. |
| **Q6** | Count tickets per status | `GROUP BY`, `COUNT()`, status breakdown | Displays pipeline status counts (Open, In Progress, Resolved, Closed). |
| **Q7** | Average, Min, Max resolution time | `AVG()`, `MIN()`, `MAX()`, `TIMESTAMPDIFF()` | Computes mean resolution hours across resolved tickets. |
| **Q8** | Find all unresolved tickets | `WHERE ... IN`, `COALESCE()`, `LEFT JOIN` | Aggregates all backlog tickets needing staff attention. |
| **Q9** | Date-range query (Past 7 days) | `DATE_SUB()`, `NOW()`, `INTERVAL`, date math | Filters tickets submitted within the rolling week. |
| **Q10** | Customers with multiple tickets | `GROUP BY`, `HAVING COUNT(*) > 1` | Pinpoints repeat customers / frequent requesters. |
| **Q11** | Agent workload summary | `LEFT JOIN`, `SUM(CASE ...)`, conditional aggregation | Calculates total, in-progress, and resolved counts per agent. |
| **Q12** | Resolved tickets via Subquery | Nested `IN (SELECT ...)`, Subqueries | Demonstrates subquery execution with date filtering. |

---

## 3. Detailed Query Implementations & Verification

### Query 1: Show all Open tickets
```sql
SELECT 
    t.ticket_id, c.name AS customer_name, cat.category_name, 
    p.priority_name, t.subject, t.created_at
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
JOIN Ticket_Status s ON t.status_id = s.status_id
WHERE s.status_name = 'Open'
ORDER BY p.sla_hours ASC, t.created_at ASC;
```

---

### Query 4: Count tickets by category (Demonstrating LEFT JOIN)
```sql
SELECT 
    cat.category_id, cat.category_name, COUNT(t.ticket_id) AS ticket_count
FROM Categories cat
LEFT JOIN Tickets t ON cat.category_id = t.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY ticket_count DESC, cat.category_name ASC;
```
*Note:* The `LEFT JOIN` ensures categories with **0 tickets** (such as `'Other'`) still appear in the result set rather than being dropped.

---

### Query 7: Average, Minimum, and Maximum Resolution Time (Hours)
```sql
SELECT 
    ROUND(AVG(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 2) AS avg_resolution_hours,
    ROUND(MIN(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 2) AS min_resolution_hours,
    ROUND(MAX(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 2) AS max_resolution_hours,
    COUNT(ticket_id) AS total_resolved_tickets
FROM Tickets
WHERE resolved_at IS NOT NULL;
```
*Output:* Average resolution duration: **22.50 hours** across resolved tickets.

---

### Query 10: Find customers with multiple tickets (`HAVING` Clause)
```sql
SELECT 
    c.user_id, c.name AS customer_name, c.email,
    COUNT(t.ticket_id) AS total_tickets_submitted
FROM Users c
JOIN Tickets t ON c.user_id = t.customer_id
GROUP BY c.user_id, c.name, c.email
HAVING COUNT(t.ticket_id) > 1
ORDER BY total_tickets_submitted DESC;
```
*Note:* Demonstrates the difference between `WHERE` (filters individual rows before grouping) and `HAVING` (filters aggregated groups after `GROUP BY`).

---

### Query 11: Agent Workload Summary (Conditional Aggregation with `CASE`)
```sql
SELECT 
    a.user_id AS agent_id, a.name AS agent_name, a.email AS agent_email,
    COUNT(t.ticket_id) AS total_assigned_tickets,
    SUM(CASE WHEN s.status_name = 'In Progress' THEN 1 ELSE 0 END) AS active_in_progress,
    SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS completed_tickets
FROM Users a
LEFT JOIN Tickets t ON a.user_id = t.assigned_agent_id
LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
WHERE a.role = 'agent'
GROUP BY a.user_id, a.name, a.email
ORDER BY total_assigned_tickets DESC;
```

---

### Query 12: Subquery Demonstration (Nested `IN`)
```sql
SELECT 
    t.ticket_id, c.name AS customer_name, cat.category_name, 
    t.subject, t.resolved_at
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
WHERE t.ticket_id IN (
    SELECT ticket_id 
    FROM Tickets 
    WHERE status_id IN (SELECT status_id FROM Ticket_Status WHERE status_name IN ('Resolved', 'Closed'))
      AND resolved_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
)
ORDER BY t.resolved_at DESC;
```

---

## 4. Viva Defense Questions & Answers

* **Q: What is the fundamental difference between `WHERE` and `HAVING`?**
  * **Answer:** `WHERE` acts as a pre-filter, removing individual rows from consideration *before* any grouping occurs. `HAVING` acts as a post-filter, evaluating conditions on aggregated values *after* the `GROUP BY` operation has grouped the rows (e.g., `HAVING COUNT(ticket_id) > 1`).
* **Q: Why did you use `LEFT JOIN` instead of `INNER JOIN` in Query 4 (Tickets by Category) and Query 11 (Agent Summary)?**
  * **Answer:** An `INNER JOIN` only returns rows where keys match in both tables. If a category currently has zero tickets or an agent has zero assigned tickets, an `INNER JOIN` would omit them entirely. A `LEFT JOIN` retains all master categories and all agents, returning `0` or `NULL` for missing child rows, ensuring accurate and complete reporting.
* **Q: What is a Subquery and when is it preferred?**
  * **Answer:** A subquery is a nested `SELECT` statement enclosed in parentheses whose result is consumed by an outer query. Subqueries are preferred for multi-stage filtering, existence checks (`EXISTS` / `IN`), and temporary derived tables without creating persistent views.

