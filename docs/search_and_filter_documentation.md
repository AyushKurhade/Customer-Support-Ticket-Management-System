# Phase 22: Advanced Search & Multi-Criteria Filtering Engine Documentation

## 1. Overview
The **Search and Multi-Criteria Filtering Engine** implements a dynamic query builder allowing users and administrators to search, filter, sort, and paginate tickets across multiple dimensions simultaneously.

It enforces role-based data privacy:
* **Customers:** All search queries are automatically scoped with `AND t.customer_id = session['user_id']`.
* **Agents & Admins:** Queries search the entire database registry.

---

## 2. Supported Search & Filter Parameters

| Parameter | Type | SQL Logic Implemented | Description |
|---|---|---|---|
| `q` | String / Integer | Multi-column `LIKE %s` + `ticket_id = %s` | Searches across Subject, Description, Customer Name/Email, Agent Name, Category Name, and exact Ticket ID. |
| `category_id` | Integer | `t.category_id = %s` | Filters by IT problem domain (e.g. Network, Hardware). |
| `priority_id` | Integer | `t.priority_id = %s` | Filters by urgency tier (e.g. Critical, High). |
| `status_id` | Integer | `t.status_id = %s` | Filters by lifecycle state (e.g. Open, In Progress). |
| `agent_id` | Integer | `t.assigned_agent_id = %s` | Filters by assigned staff member. |
| `unassigned` | Boolean | `t.assigned_agent_id IS NULL` | Filters only tickets awaiting assignment. |
| `sla_status` | String | `fn_GetSLAStatus(...) = %s` | Filters by SLA state (`SLA BREACHED`, `SLA WARNING`, `WITHIN SLA`). |
| `date_preset` | Enum | `CURDATE()`, `DATE_SUB(...)` | Presets: `today`, `last_7_days`, `last_30_days`, `this_month`. |
| `start_date` / `end_date` | Date (YYYY-MM-DD) | `DATE(t.created_at) BETWEEN ...` | Custom date range filtering. |
| `sort_by` / `order` | String | `ORDER BY column ASC/DESC` | Sorts by `created_at`, `priority`, `status`, or `ticket_id`. |
| `page` / `limit` | Integer | `LIMIT %s OFFSET %s` | Server-side pagination. |

---

## 3. Dynamic SQL Query Construction

The engine dynamically concatenates parameterized clauses:
```sql
SELECT 
    t.ticket_id, c.name AS customer_name, cat.category_name, 
    p.priority_name, s.status_name, COALESCE(a.name, 'Unassigned') AS agent_name,
    t.subject, t.created_at,
    fn_GetSLAStatus(t.ticket_id) AS sla_status,
    fn_CalculateTicketAge(t.ticket_id) AS age_hours
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
JOIN Ticket_Status s ON t.status_id = s.status_id
LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
WHERE 1=1
  AND (t.subject LIKE %s OR t.description LIKE %s OR c.name LIKE %s)
  AND t.category_id = %s
  AND t.priority_id = %s
  AND t.status_id = %s
  AND t.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY p.sla_hours ASC, t.created_at ASC
LIMIT %s OFFSET %s;
```

---

## 4. Test Verification Results

| # | Test Scenario | Query Parameters | Expected Result | Actual Result | Status |
|---|---|---|---|---|:---:|
| **1** | Full-Text Keyword Search | `?q=WiFi` | Matches tickets containing "WiFi" | `200 OK`, matched 1 ticket | **PASS** |
| **2** | Numeric Ticket ID Search | `?q=1` | Matches exact Ticket #1 | `200 OK`, found ticket #1 | **PASS** |
| **3** | Combined Multi-Filter | `?category_id=3&priority_id=3` (Network + High) | Evaluates both criteria simultaneously via `AND` | `200 OK`, 1 ticket returned | **PASS** |
| **4** | SLA Status Filter | `?sla_status=SLA BREACHED` | Filters via stored function `fn_GetSLAStatus` | `200 OK`, 2 breached tickets | **PASS** |
| **5** | Date Range Filter | `?date_preset=last_7_days` | Evaluates rolling 7-day window | `200 OK`, matching tickets returned | **PASS** |
| **6** | Customer Privacy Isolation | Alice searching for Bob's ticket (`?q=Excel`) | Scoped to Alice only | `200 OK`, Count: 0 | **PASS** |
| **7** | Admin Global Visibility | Admin searching for Bob's ticket (`?q=Excel`) | Unscoped global registry | `200 OK`, Count: 2 | **PASS** |

---

## 5. Viva Defense Questions & Answers

* **Q: How does the search engine combine multiple filters without SQL injection?**
  * **Answer:** By dynamically assembling query conditions into a `where_clauses` list joined with `AND`, while simultaneously appending parameter values into a separate `params` tuple. The combined string is passed to `cursor.execute(sql, tuple(params))`, ensuring parameterized isolation regardless of how many filters are combined.
* **Q: Why was `COLLATE utf8mb4_unicode_ci` used in the `fn_GetSLAStatus` filter?**
  * **Answer:** In MySQL, stored functions may evaluate character literals with default collation (`utf8mb4_general_ci`). Comparing a general collation literal to a table column or parameter typed with `utf8mb4_unicode_ci` causes error 1267 (*Illegal mix of collations*). Applying explicit collation coerces both operands to the identical Unicode collation sequence.

