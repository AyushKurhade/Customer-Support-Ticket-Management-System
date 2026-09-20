# Customer Support Ticket Management System
## Analytical Reports & UI Portals Documentation (Phase 24)

---

### 1. Architectural Overview

Phase 24 completes the user-facing presentation and analytical reporting layer of the Customer Support Ticket Management System. It delivers:
1. **Multi-Role Frontend Portals**:
   - `index.html`: System landing page highlighting DBMS engineering concepts.
   - `login.html`: Unified role-based authentication portal with quick-fill demo profiles.
   - `customer_portal.html`: Customer service portal for ticket submission, conversation threads, and lifecycle tracking.
   - `agent_portal.html`: Agent workspace for queue triage, internal staff notes, and resolution actions.
   - `reports.html`: Analytics suite with interactive data tables, KPI metrics, and export capabilities.
2. **Analytical SQL Engine**:
   - Aggregated business reports across Categories, Statuses, Priorities, and Support Agents.
   - Dynamic SLA compliance rate computation integrating `fn_GetSLAStatus()`.
   - Resolution time analysis using `TIMESTAMPDIFF(MINUTE, created_at, resolved_at)`.
3. **Dynamic CSV Data Export Engine**:
   - Server-side CSV stream generation adhering to RFC-4180 standard via `/api/reports/export?type=...`.

---

### 2. Analytical Reports & SQL Queries

#### Report 1: Category Performance & SLA Breaches (`/api/reports/category`)
- **Objective**: Identify which technical domains experience the highest ticket load and SLA breach frequencies.
- **SQL Implementation**:
```sql
SELECT 
    c.category_id,
    c.category_name,
    COUNT(t.ticket_id) AS total_tickets,
    SUM(CASE WHEN s.status_name IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS active_tickets,
    SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
    ROUND(AVG(CASE WHEN t.resolved_at IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0 END), 2) AS avg_resolution_hours,
    SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END) AS breached_tickets
FROM Categories c
LEFT JOIN Tickets t ON c.category_id = t.category_id
LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
GROUP BY c.category_id, c.category_name
ORDER BY total_tickets DESC;
```

#### Report 2: Status Lifecycle & Operational Flow (`/api/reports/status`)
- **Objective**: Monitor the distribution of tickets across the pipeline and identify aging bottlenecks.
- **SQL Implementation**:
```sql
SELECT 
    s.status_id,
    s.status_name,
    COUNT(t.ticket_id) AS total_tickets,
    ROUND(COUNT(t.ticket_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM Tickets), 0), 2) AS percentage,
    MAX(CASE WHEN s.status_name NOT IN ('Resolved', 'Closed') THEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) ELSE NULL END) AS oldest_ticket_hours
FROM Ticket_Status s
LEFT JOIN Tickets t ON s.status_id = t.status_id
GROUP BY s.status_id, s.status_name
ORDER BY s.status_id ASC;
```

#### Report 3: Priority & SLA Target Compliance (`/api/reports/priority`)
- **Objective**: Evaluate adherence to agreed Service Level Agreements (SLAs) across Critical, High, Medium, and Low priorities.
- **SQL Implementation**:
```sql
SELECT 
    p.priority_id,
    p.priority_name,
    p.sla_hours,
    COUNT(t.ticket_id) AS total_tickets,
    SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
    ROUND(AVG(CASE WHEN t.resolved_at IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0 END), 2) AS avg_resolution_hours,
    SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END) AS breached_tickets,
    ROUND(
        (COUNT(t.ticket_id) - SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END)) * 100.0 / NULLIF(COUNT(t.ticket_id), 0), 
        2
    ) AS sla_compliance_pct
FROM Priorities p
LEFT JOIN Tickets t ON p.priority_id = t.priority_id
LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
GROUP BY p.priority_id, p.priority_name, p.sla_hours
ORDER BY p.priority_id ASC;
```

#### Report 4: Support Agent Productivity Scorecard (`/api/reports/agents`)
- **Objective**: Measure staff workload balance, individual resolution volumes, and SLA performance.
- **SQL Implementation**:
```sql
SELECT 
    u.user_id,
    u.name AS agent_name,
    u.email,
    COUNT(t.ticket_id) AS assigned_tickets,
    SUM(CASE WHEN s.status_name IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS pending_tickets,
    SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
    ROUND(AVG(CASE WHEN t.resolved_at IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0 END), 2) AS avg_resolution_hours,
    SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END) AS breached_tickets,
    ROUND(
        (COUNT(t.ticket_id) - SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END)) * 100.0 / NULLIF(COUNT(t.ticket_id), 0),
        2
    ) AS sla_compliance_pct
FROM Users u
LEFT JOIN Tickets t ON u.user_id = t.assigned_agent_id
LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
WHERE u.role = 'Agent'
GROUP BY u.user_id, u.name, u.email
ORDER BY resolved_tickets DESC;
```

#### Report 5: Resolution Time Distribution Analysis (`/api/reports/resolution-time`)
- **Objective**: Bucket resolved tickets into operational duration intervals (<4h, 4-24h, 24-48h, >48h) and log recent resolutions.
- **SQL Implementation**:
```sql
-- Bucket aggregates
SELECT 
    SUM(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) < 4 THEN 1 ELSE 0 END) AS under_4_hours,
    SUM(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) >= 4 AND TIMESTAMPDIFF(HOUR, created_at, resolved_at) < 24 THEN 1 ELSE 0 END) AS hours_4_to_24,
    SUM(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) >= 24 AND TIMESTAMPDIFF(HOUR, created_at, resolved_at) < 48 THEN 1 ELSE 0 END) AS hours_24_to_48,
    SUM(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) >= 48 THEN 1 ELSE 0 END) AS over_48_hours,
    ROUND(AVG(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 2) AS overall_avg_hours,
    COUNT(ticket_id) AS total_resolved
FROM Tickets
WHERE resolved_at IS NOT NULL;
```

---

### 3. REST API Specifications

| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `GET` | `/api/reports/category` | Agent, Admin | Aggregates volume, active/resolved count, avg duration, breaches per category |
| `GET` | `/api/reports/status` | Agent, Admin | Computes status breakdown %, volume, and oldest active ticket age |
| `GET` | `/api/reports/priority` | Agent, Admin | Evaluates SLA targets against actual average resolution and compliance % |
| `GET` | `/api/reports/agents` | Agent, Admin | Staff scorecard of assignments, pending, resolved, SLA compliance % |
| `GET` | `/api/reports/resolution-time` | Agent, Admin | Time distribution buckets (<4h, 4-24h, 24-48h, >48h) & resolved log |
| `GET` | `/api/reports/export?type=<report>` | Agent, Admin | Dynamic RFC-4180 CSV export for selected report type |

---

### 4. Frontend Portals Summary

| Portal Page | Target Audience | Primary Functionalities |
|---|---|---|
| `index.html` | Public / Evaluators | Landing presentation, architectural highlights, quick portal launchers |
| `login.html` | All Users | Unified login, customer self-registration, 1-click evaluation demo credentials |
| `customer_portal.html` | Customers | Submit tickets, AI suggest hook, track lifecycle, conversation reply modal |
| `agent_portal.html` | Support Agents | Assigned queue, unassigned pool triage, internal notes toggle, resolve tickets |
| `reports.html` | Agents & Admins | Tabular analytical reports, KPI strip, CSV download, print/PDF layout |
| `admin_dashboard.html` | Admins | High-level KPI tiles, Chart.js trends, agent workload from `vw_AgentTicketSummary` |

---

### 5. Verification & Test Evidence

All endpoints tested and verified via Flask test client:
```python
# API Endpoint Tests
GET /api/reports/category        -> 200 OK (9 categories analyzed)
GET /api/reports/status          -> 200 OK (4 statuses analyzed)
GET /api/reports/priority        -> 200 OK (4 priorities with SLA compliance computed)
GET /api/reports/agents          -> 200 OK (3 support agents scored)
GET /api/reports/resolution-time -> 200 OK (11 resolved tickets analyzed)

# CSV Export Tests
GET /api/reports/export?type=category   -> 200 OK (Content-Type: text/csv, attachment)
GET /api/reports/export?type=status     -> 200 OK (Content-Type: text/csv, attachment)
GET /api/reports/export?type=priority   -> 200 OK (Content-Type: text/csv, attachment)
GET /api/reports/export?type=agents     -> 200 OK (Content-Type: text/csv, attachment)
GET /api/reports/export?type=resolution -> 200 OK (Content-Type: text/csv, attachment)

# Frontend Page Routes
GET /                     -> 200 OK (10,188 bytes)
GET /login.html           -> 200 OK (13,205 bytes)
GET /customer_portal.html -> 200 OK (23,548 bytes)
GET /agent_portal.html    -> 200 OK (24,949 bytes)
GET /admin_dashboard.html -> 200 OK (18,581 bytes)
GET /reports.html         -> 200 OK (19,595 bytes)
```
