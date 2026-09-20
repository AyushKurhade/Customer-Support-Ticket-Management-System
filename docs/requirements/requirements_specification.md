# Software Requirements Specification (SRS)
## Customer Support Ticket Management System (Ticket Categorization)

---

### 1. Introduction & Project Overview
* **Project Title:** Customer Support Ticket Management System — Ticket Categorization
* **Domain:** IT Services & Infrastructure Support
* **Course Context:** College DBMS Mini-Project
* **Primary Focus:** Relational Database Management System (RDBMS) design, normal form compliance (1NF–3NF), integrity constraints, relational queries/joins, views, stored procedures, functions, triggers, and ACID transactions.
* **Secondary Component:** Lightweight, explainable Machine Learning (AI/DS) text classification module for automated ticket category recommendation.

---

### 2. User Roles & Permission Matrix

| Feature / Action | Customer | Support Agent | Administrator |
| :--- | :---: | :---: | :---: |
| Self-Registration & Authentication | Yes | No (Admin provisioned) | Pre-configured / Seeded |
| Create Support Ticket | Yes | No | Yes (on behalf) |
| View Own Created Tickets | Yes | No | Yes (All tickets) |
| View Assigned Tickets | No | Yes | Yes (All tickets) |
| AI Ticket Category Prediction | Yes (at submit) | N/A | N/A |
| Reassign Ticket to Agent | No | No | Yes |
| Change Ticket Priority | No | No | Yes |
| Update Ticket Status (In Progress, Resolved) | No | Yes | Yes |
| Close Ticket | Yes (Confirm) | No | Yes |
| Add Public Comments / Responses | Yes | Yes | Yes |
| Add Internal Notes | No | Yes | Yes |
| View Ticket Status Audit History | Yes | Yes | Yes |
| View Performance Dashboard & Analytics | No | Own KPIs | Yes (Full System KPIs) |
| Generate Analytical Reports | No | No | Yes |
| Master Data Management (Categories, Priorities, Statuses) | No | No | Yes |

---

### 3. Functional Requirements (FR)

#### Module 1: Authentication & User Management
* **FR 1.1:** System shall allow customers to self-register with Name, unique Email, Contact, and a securely hashed password.
* **FR 1.2:** System shall authenticate users and issue session tokens/cookies distinguishing `customer`, `agent`, and `admin` roles.
* **FR 1.3:** Passwords must be hashed using industry-standard hashing (e.g., bcrypt/pbkdf2); plain-text storage is prohibited.

#### Module 2: Master Data Management
* **FR 2.1:** System must maintain dynamic reference tables for Categories (`Hardware`, `Software`, `Network`, `Account`, `Payment`, `Technical Issue`, `Other`).
* **FR 2.2:** System must maintain reference tables for Priorities (`Low`, `Medium`, `High`, `Critical`).
* **FR 2.3:** System must maintain reference tables for Ticket Statuses (`Open`, `In Progress`, `Resolved`, `Closed`).
* **FR 2.4:** Values must be referenced by primary/foreign keys rather than hard-coded strings.

#### Module 3: Customer Ticket Management
* **FR 3.1:** Customer can draft and submit a ticket specifying Subject, Description, and initial Priority.
* **FR 3.2:** System will invoke the AI classifier to recommend the best-fitting Category based on the Description.
* **FR 3.3:** Customer can accept or adjust the category before submission.
* **FR 3.4:** Ticket defaults to status `Open`.

#### Module 4: Agent & Admin Ticket Lifecycle Management
* **FR 4.1:** Admin can inspect unassigned tickets and assign them to an available Agent.
* **FR 4.2:** Agent can transition ticket status from `Open` to `In Progress`, and subsequently to `Resolved`.
* **FR 4.3:** Transitioning to `Resolved` records the resolution timestamp and notes.

#### Module 5: Ticket Audit Trail & Comments
* **FR 5.1:** Customers and Agents can exchange timestamped messages on an open ticket.
* **FR 5.2:** Any status transition must automatically log the previous status, new status, modifier user ID, and timestamp into `Ticket_Status_History`.

#### Module 6: Search & Multi-Criteria Filtering
* **FR 6.1:** System must provide search across Ticket ID, Subject, and Customer Name.
* **FR 6.2:** System must allow multi-criteria filtering: `Category` AND `Priority` AND `Status` AND `Date Range`.

#### Module 7: Reports & Analytics Dashboard
* **FR 7.1:** Admin dashboard must render live ticket counts (Total, Open, In Progress, Resolved, Closed).
* **FR 7.2:** Visual charts displaying ticket breakdown by Category, Priority, and monthly submission trends.
* **FR 7.3:** Agent workload summary showing ticket counts and average resolution time per agent.

#### Module 8: AI/DS Ticket Categorization
* **FR 8.1:** Lightweight Natural Language Processing (NLP) pipeline using TF-IDF vectorization.
* **FR 8.2:** Classification model (Multinomial Naive Bayes / Logistic Regression) trained on categorized IT ticket descriptions.
* **FR 8.3:** Prediction exposed via an internal API endpoint returning predicted category and confidence score.

#### Module 9: Database Operations & Integrity
* **FR 9.1:** All tables must have surrogate or natural Primary Keys and Foreign Key referential integrity.
* **FR 9.2:** Database triggers to enforce status history logging and automatic `resolved_at` timestamp setting.
* **FR 9.3:** Stored procedures to encapsulate complex workflows (e.g., ticket assignment, resolution).
* **FR 9.4:** Stored functions to compute derived values (e.g., ticket age in hours, resolution duration).

---

### 4. Non-Functional Requirements (NFR)
* **Data Integrity:** Enforced at the RDBMS level using declarative constraints (`CHECK`, `NOT NULL`, `UNIQUE`, `FOREIGN KEY ON DELETE RESTRICT/CASCADE`).
* **Explainability:** Code, queries, and ML models must be transparent, easy to trace, and simple to explain during an oral viva.
* **Performance:** Standard queries must resolve in < 50ms for typical mini-project volume (< 100,000 records).
* **Simplicity:** No unnecessary external services, container daemons, or cloud dependencies.

---

### 5. Technology Stack Selection & Rationale

| Layer | Recommended Technology | Why Selected |
| :--- | :--- | :--- |
| **Database** | **MySQL 8.0** (InnoDB Engine) | Already installed on the user's workstation (`MYSQL80`). Native support for Stored Procedures, Triggers, Views, Functions, CHECK constraints, and Transactions. Standard in academic college evaluation. |
| **Backend** | **Python 3.13 + Flask** | Python is installed (`Python 3.13.2`). Flask provides a clean, minimalistic web server without hidden magic. Seamless direct integration with MySQL (`mysql-connector-python`) and Python ML libraries (`scikit-learn`). |
| **Frontend** | **HTML5 + Bootstrap 5 + Vanilla JavaScript** | Clean, responsive UI with zero compilation or node build steps required. Fast to run, lightweight, and easy to inspect. |
| **Charts** | **Chart.js** (CDN) | Easy to bind directly to SQL aggregation results via simple JSON APIs. |
| **AI / DS** | **scikit-learn (TF-IDF + Multinomial Naive Bayes / Logistic Regression)** | Simple, robust, 100% explainable in viva (Bayes theorem / probabilistic text classification), trains in seconds, and requires zero heavy deep-learning dependencies. |
| **Database Tool** | **MySQL Workbench 8.0 / MySQL CLI** | Already present on the machine; ideal for live demonstration of schemas, ER diagrams, and SQL queries to examiners. |
| **Version Control**| **Git** | Industry standard, clear commit traceability across all 31 phases. |
