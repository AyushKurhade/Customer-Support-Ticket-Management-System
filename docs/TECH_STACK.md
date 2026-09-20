# Technology Stack Selection & Architecture Analysis

## 1. Context & Evaluation Criteria

To meet college DBMS mini-project standards, the technology stack was evaluated against these criteria:
1. **DBMS Concept Support**: Complete native support for Views, Stored Procedures, Functions, Triggers, Transactions (ACID), Foreign Keys, and Constraints.
2. **AI/DS Integration**: Seamless integration between the ML model and the backend server without complex microservices or IPC overhead.
3. **Ease of Demonstration & Viva**: Transparent, readable code that can be explained in a viva without hidden ORM abstractions obscuring SQL.
4. **Local Environment Compatibility**: Seamless operation on the current system (Python 3.13, Node 24, Git, MySQL 8.0).
5. **No Overengineering**: Strict avoidance of unnecessary complexity (no React/Angular builds, no Docker, no Kubernetes, no microservices, no heavy LLM APIs).

---

## 2. Recommended Technology Stack

| Layer | Recommended Technology | Alternatives Considered | Why Selected |
|---|---|---|---|
| **Database** | **MySQL 8.0 (InnoDB)** | PostgreSQL, SQLite | Standard in college DBMS curricula; full native support for stored procedures, triggers, ACID transactions, views, and functions; already installed on system. |
| **Backend** | **Python (Flask)** | Node.js (Express), Django, Java Spring | Lightweight, minimal boilerplate; Python allows the ML model (scikit-learn) and database connector (`mysql-connector-python`) to run within the exact same runtime without inter-process communication; directly executes raw SQL/stored procedures for clear viva explanation. |
| **Frontend** | **HTML5 + CSS3 + Bootstrap 5 + Vanilla JavaScript** | React, Vue, Angular | Zero build tools required; rapid, responsive, clean UI; directly consumes Flask REST endpoints/templates without npm build errors during viva demos. |
| **AI / Data Science** | **Python (scikit-learn: Multinomial Naive Bayes / Logistic Regression + TF-IDF)** | Deep Learning (PyTorch/TensorFlow), LLM APIs | Explainable, fast, lightweight; requires minimal training data; transparent mathematics (Bayes theorem / probability) easy to defend in viva. |
| **Charts / Visuals** | **Chart.js (CDN)** | D3.js, Recharts | Simple JavaScript canvas-based charting; renders category, priority, status, and resolution time analytics with minimal code. |
| **Development Tools** | **VS Code / Antigravity IDE, MySQL Workbench / CLI** | DBeaver, Postman | Standard, accessible tooling for database inspection and debugging. |
| **Version Control** | **Git** | SVN | Industry standard; already installed; clean atomic commits matching development phases. |

---

## 3. Component Interaction Flow

```
[Customer / Agent / Admin]
           │
      (HTTP / JSON)
           ▼
[Frontend: HTML5 / Bootstrap 5 / Vanilla JS / Chart.js]
           │
      (REST / JSON)
           ▼
[Backend: Python Flask]
     │                 │
     │ (Direct Python)  │ (mysql-connector-python: Parameterized Queries & SP calls)
     ▼                 ▼
[AI Model: scikit-learn]  [Database: MySQL 8.0 (InnoDB)]
(Predicts Category)      (Tables, Views, Procedures, Triggers, Functions)
```

---

## 4. Why This Stack is Ideal for a DBMS Mini-Project

1. **SQL Transparency**: We will use direct parameterized SQL queries and stored procedure execution via `mysql-connector-python`. Examiners want to see actual SQL, views, procedures, and triggers being triggered—not obscured behind heavy ORM abstractions.
2. **Unified Backend & AI**: Because Flask is Python, our AI classifier (trained with scikit-learn) can be loaded directly into memory as a `.joblib` model and invoked in one line of code when creating a ticket. No separate AI servers, microservices, or external network requests are needed.
3. **Rock-Solid Viva Defense**: Every piece is easy to trace: HTML form $\rightarrow$ Flask route $\rightarrow$ ML model prediction $\rightarrow$ MySQL Stored Procedure execution $\rightarrow$ Trigger execution $\rightarrow$ Status History log.

