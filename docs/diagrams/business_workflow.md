# Phase 2: Core Business Workflow & Ticket Lifecycle

## 1. Overview
This document models the end-to-end operational flow and ticket lifecycle for the **Customer Support Ticket Management System**. It defines how Customers, Support Agents, and Administrators interact with the database across each lifecycle milestone.

---

## 2. End-to-End System Workflow

```mermaid
flowchart TD
    subgraph Customer_Action ["1. Customer Actions"]
        A[Customer Registers / Logs In] --> B[Drafts Ticket: Subject + Description + Priority]
        B --> C[AI Classifier Recommends Category]
        C --> D[Customer Submits Ticket]
    end

    subgraph DB_Creation ["Database Event"]
        D --> E[INSERT into Tickets: Status = 'Open']
        E --> F[Trigger logs to Ticket_Status_History]
    end

    subgraph Admin_Action ["2. Administrator Actions"]
        E --> G[Admin Reviews Unassigned Tickets]
        G --> H[Admin Assigns Ticket to Support Agent]
        H --> I[UPDATE Tickets: assigned_agent_id = Agent_ID]
    end

    subgraph Agent_Action ["3. Support Agent Actions"]
        I --> J[Agent Views Assigned Queue]
        J --> K[Agent Changes Status to 'In Progress']
        K --> L[Agent Posts Comment / Diagnostic Update]
        L --> M[Agent Resolves Issue & Sets Status to 'Resolved']
    end

    subgraph Resolution_Audit ["4. Resolution & Closure"]
        M --> N[Trigger sets resolved_at timestamp]
        N --> O[Customer Views Resolution & Confirms]
        O --> P[Status Updated to 'Closed']
        P --> Q[Dashboard & Analytical Reports Refresh Automatically]
    end
```

---

## 3. Ticket State Transition Diagram

Every ticket transitions through a strictly defined state machine:

```mermaid
stateDiagram-v2
    [*] --> Open: Customer creates ticket (Default)
    Open --> In_Progress: Agent assigned & starts investigation
    In_Progress --> In_Progress: Agent/Customer adds comments
    In_Progress --> Resolved: Agent submits solution
    Resolved --> Closed: Customer or Admin confirms closure
    Resolved --> In_Progress: Customer reopens if unresolved
    Closed --> [*]: Terminal state
```

### State Machine Rules:
1. **`Open`**: Created by customer, awaiting agent assignment or agent pickup.
2. **`In Progress`**: Agent is actively analyzing or communicating with customer.
3. **`Resolved`**: Work completed by agent. Database trigger sets `resolved_at = NOW()`.
4. **`Closed`**: Customer confirms resolution or auto-closed after verification.
5. **Audit Rule**: Any update to `status_id` triggers an automatic row insertion into `Ticket_Status_History`.

---

## 4. Role Responsibility Breakdown

### A. Customer
- Self-registers and logs in.
- Creates support ticket with Subject, Description, and initial Priority.
- Receives instant AI category recommendation based on description.
- Posts comments/replies to clarify questions.
- Views ticket status, resolution details, and closes resolved tickets.

### B. Support Agent
- Logs into Agent Portal.
- Reviews assigned tickets.
- Adds comments/diagnostics (visible to customer).
- Transitions status to `In Progress` when starting work.
- Transitions status to `Resolved` upon solving the issue.

### C. Administrator
- Manages users (customers, agents).
- Manages reference/master data (categories, priorities, statuses).
- Assigns or reassigns unassigned tickets to agents.
- Adjusts ticket priority if escalation is required.
- Views system-wide real-time dashboard and reports (resolution times, backlog counts, agent workload).

---

## 5. Viva Explanation Notes

* **Q: Why is ticket state management handled via a dedicated reference table instead of a plain string column?**
  * **Answer:** Using a normalized `Ticket_Status` master table with foreign key constraints prevents typos (e.g., `"in_progress"` vs `"In Progress"`), ensures referential integrity, and allows clean state machine constraints.
* **Q: How does the workflow guarantee that audit history is never forgotten by developers?**
  * **Answer:** Instead of relying on application code to remember to insert into an audit table, a database-level `AFTER UPDATE` trigger intercepts every status change and records it into `Ticket_Status_History` atomically.
