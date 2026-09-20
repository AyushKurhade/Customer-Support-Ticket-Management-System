# Phase 23: Real-Time Admin Dashboard Documentation & UI Verification

## 1. Overview
The **Admin Dashboard** provides real-time operational visibility into customer ticket pipelines, agent performance, SLA compliance, and monthly submission trends.

Unlike static reporting systems, the dashboard queries the live MySQL database on every request, ensuring that metrics automatically update as tickets are submitted, assigned, and resolved.

---

## 2. Dashboard Components & Database Integration

### 1. KPI Summary Stat Cards
Computed via a single high-efficiency SQL query with conditional aggregation:
* **Total Tickets:** `COUNT(ticket_id)`
* **Open Tickets:** `SUM(CASE WHEN s.status_name = 'Open' THEN 1 ELSE 0 END)`
* **In Progress Tickets:** `SUM(CASE WHEN s.status_name = 'In Progress' THEN 1 ELSE 0 END)`
* **Resolved Tickets:** `SUM(CASE WHEN s.status_name = 'Resolved' THEN 1 ELSE 0 END)`
* **Closed Tickets:** `SUM(CASE WHEN s.status_name = 'Closed' THEN 1 ELSE 0 END)`
* **Average Resolution Duration:** Computed via `AVG(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0)`.

### 2. Interactive Chart.js Visualizations
* **Chart 1 (Tickets by Category):** Doughnut chart showing distribution across master categories (`Hardware`, `Software`, `Network`, etc.) using a `LEFT JOIN` to ensure 0-ticket categories are retained.
* **Chart 2 (Tickets by Priority & SLA):** Bar chart displaying ticket volumes segmented by urgency tiers (`Critical 4h`, `High 24h`, `Medium 48h`, `Low 72h`).
* **Chart 3 (Pipeline Status):** Pie chart rendering current pipeline distribution.
* **Chart 4 (Monthly Volume Trend):** Column chart showing monthly inflow trends using `DATE_FORMAT(t.created_at, '%Y-%m')`.

### 3. Agent Workload & Performance Table
* Directly consumes the database view **`vw_AgentTicketSummary`**:
  * Displays each agent's name, email, total assigned count, active in-progress count, resolved count, and mean resolution duration in hours.

### 4. Recent Tickets Feed
* Real-time stream of the latest 5 submitted tickets with formatted timestamps and status badges.

---

## 3. Endpoints Specification

| Method | Endpoint | Access | Response Content |
|---|---|---|---|
| `GET` | `/api/dashboard/stats` | `@role_required(['agent', 'admin'])` | JSON object containing `kpis`, `charts` (`by_category`, `by_priority`, `by_status`, `by_month`), `agent_summary`, and `recent_tickets`. |
| `GET` | `/admin_dashboard.html` | Browser | Responsive web interface rendering KPI cards and Chart.js graphs. |

---

## 4. Test Verification Results

| # | Test Scenario | Verified Metric | Result Value | Status |
|---|---|---|---|:---:|
| **1** | Endpoint Status | `GET /api/dashboard/stats` | `200 OK` | **PASS** |
| **2** | Real-Time KPI Retrieval | Live database count | 23 Total Tickets, 6 Open, 5 In Progress, 9 Resolved, 3 Closed | **PASS** |
| **3** | Mean Resolution Time | Live computation | `16.43 hours` | **PASS** |
| **4** | Category Aggregations | Master tables join | 9 categories mapped with counts | **PASS** |
| **5** | Priority Aggregations | SLA breakdown | 4 urgency tiers mapped | **PASS** |
| **6** | View Integration | `vw_AgentTicketSummary` query | 3 agent rows returned with active/resolved counts | **PASS** |
| **7** | Static Asset Serving | CSS & JS bundle loading | `200 OK` on `/static/css/style.css` & `/static/js/api.js` | **PASS** |
| **8** | HTML Page Serving | Web Dashboard rendering | `200 OK` on `/admin_dashboard.html` | **PASS** |

---

## 5. Viva Defense Questions & Answers

* **Q: Why are dashboard statistics calculated using SQL aggregations instead of loading all tickets into Python memory?**
  * **Answer:** **Database-Side Processing Efficiency.** Computing aggregations (`COUNT`, `SUM(CASE ...)`, `AVG(TIMESTAMPDIFF(...))`) directly inside the MySQL storage engine takes microseconds and transmits only a tiny summary payload over the network. If the database scales to 500,000 tickets, transferring all rows into Python memory would exhaust RAM and introduce unacceptable latency.
* **Q: How does the dashboard leverage Database Views?**
  * **Answer:** The Agent Performance section queries `vw_AgentTicketSummary` directly. By querying the view instead of writing a complex 3-table join with conditional aggregations inside the Python script, the business logic remains centralized and consistent with external reporting queries.
