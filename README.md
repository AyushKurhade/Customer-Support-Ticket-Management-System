
# 🎫 Customer Support Ticket Management System

### 📚 DBMS Mini Project | Academic Year 2025–2026

A database-driven web application designed to manage customer support tickets efficiently, from ticket creation to assignment, tracking, and resolution.

The system uses a normalized relational database and includes an AI-assisted ticket classification component to support ticket categorization.

---

## 📌 Table of Contents

- [📖 Project Overview](#-project-overview)
- [🎯 Objectives](#-objectives)
- [✨ Key Features](#-key-features)
- [🛠️ Technology Stack](#️-technology-stack)
- [🔄 System Workflow](#-system-workflow)
- [🧩 Main Modules](#-main-modules)
- [🗄️ Database Design](#️-database-design)
- [🤖 AI/DS Component](#-aids-component)
- [📊 Reports and Dashboard](#-reports-and-dashboard)
- [🔐 User Roles](#-user-roles)
- [⚙️ Installation and Setup](#️-installation-and-setup)
- [📁 Project Structure](#-project-structure)
- [🧠 DBMS Concepts Implemented](#-dbms-concepts-implemented)
- [🚀 Future Enhancements](#-future-enhancements)
- [👨‍💻 Author](#-author)

---

## 📖 Project Overview

The **Customer Support Ticket Management System** is a web-based application developed as a DBMS mini project.

It provides a centralized platform where customers can raise support tickets, agents can manage and resolve them, and administrators can monitor the overall ticket management process.

The system organizes support requests using categories, priorities, ticket statuses, and agent assignments.

### 🏷️ Project Details

| Category | Description |
|---|---|
| Project Type | DBMS Mini Project |
| Domain | IT Services |
| Application Type | Web-Based Application |
| Database | MySQL 8.0 |
| Backend | Python Flask |
| AI/DS Component | Ticket Classification |
| Academic Year | 2026–2027 |

---

## 🎯 Objectives

- 📝 Enable customers to create and track support tickets.
- 🗂️ Organize tickets based on category and priority.
- 👨‍💼 Allow agents to pick up and resolve tickets.
- 🔍 Provide search and filtering functionality.
- 📊 Generate reports and dashboard statistics.
- 🤖 Integrate an AI/DS component for ticket classification.
- 🗄️ Demonstrate core DBMS concepts through a relational database.

---

## ✨ Key Features

### 👤 Login and User Management
- User authentication and role-based access.
- Separate interfaces for customers, agents, and administrators.

### 🎫 Ticket Management
- Create and submit support tickets.
- Assign tickets to available agents.
- Track ticket status and priority.
- Resolve and close support tickets.

### 🔎 Search and Filter
- Search tickets by ID or subject.
- Filter tickets by status, category, and priority.
- View assigned and unassigned tickets.

### 📊 Reports and Dashboard
- View total ticket counts.
- Monitor open, in-progress, and closed tickets.
- Visualize ticket distribution using charts.

### 🤖 AI/DS Analysis
- Ticket classification based on ticket text.
- Use machine learning to assist in categorizing support requests.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, Vanilla JavaScript |
| Backend | Python, Flask |
| Database | MySQL 8.0 — InnoDB |
| Database Connectivity | MySQL Connector / PyMySQL |
| AI/ML | Python, Scikit-learn |
| ML Algorithm | Multinomial Naive Bayes / Logistic Regression |
| Data Visualization | Chart.js |

---

## 🔄 System Workflow

### 1️⃣ Customer Ticket Creation

```text
👤 Customer Login
       ↓
📝 Create Ticket
       ↓
Enter Subject & Description
       ↓
Select Category & Priority
       ↓
📩 Submit Ticket
       ↓
🎫 Ticket Created
       ↓
Status = OPEN
Assigned Agent = NULL
```

### 2️⃣ Agent Ticket Assignment

```text
👨‍💼 Agent Login
       ↓
📋 View Unassigned Tickets
       ↓
Select a Ticket
       ↓
🖱️ Click "Pick Up"
       ↓
🔍 Validate Ticket Availability
       ↓
Assign Ticket to Agent
       ↓
Status = IN_PROGRESS
       ↓
📂 Ticket Appears in My Tickets
```

### 3️⃣ Ticket Resolution

```text
👨‍💼 Agent Opens Assigned Ticket
       ↓
🔧 Works on Customer Issue
       ↓
📝 Updates Ticket
       ↓
✅ Marks Ticket as Resolved
       ↓
Status = CLOSED
       ↓
📋 Ticket History Updated
```

### 4️⃣ Admin Workflow

```text
🛡️ Admin Login
       ↓
📊 Open Admin Dashboard
       ↓
👥 Manage Users & Master Data
       ↓
🎫 Monitor All Tickets
       ↓
🔍 Review Ticket Assignments
       ↓
📈 View Reports & Statistics
```

---

## 🧩 Main Modules

| Module | Description |
|---|---|
| Login/User Management | Handles user authentication and roles. |
| Master Data Management | Manages categories, priorities, and other reference data. |
| Ticket Management | Creates, assigns, updates, and resolves tickets. |
| Search & Filter | Finds tickets using different conditions. |
| SQL Queries & Joins | Retrieves data from related tables. |
| Reports & Dashboard | Displays ticket statistics and visual reports. |
| AI/DS Analysis | Classifies ticket text into relevant categories. |
| Database Management | Maintains relationships, constraints, and data integrity. |

---

## 🗄️ Database Design

The system uses a **relational database in MySQL 8.0** to store and manage customer support information.

### 🧱 Core Database Entities

- 👤 Users — Stores user information and roles.
- 🎫 Tickets — Stores ticket details, status, priority, and assignments.
- 🗂️ Categories — Stores ticket categories.
- ⚡ Priorities — Stores ticket priority levels.
- 📝 Ticket Activity / History — Records ticket updates and activities.

*The exact tables and relationships depend on the implemented database schema.*

### 🔗 Relationship Overview

```text
👤 Users
   │
   ├────────────── Creates ──────────────┐
   │                                     ↓
   │                                  🎫 Tickets
   │                                     │
   ├────────────── Assigned To ──────────┤
   │                                     │
   │                                  🗂️ Categories
   │                                     │
   │                                  ⚡ Priorities
   │
   └────────────── Records Activity ─── Ticket History
```

### 🧠 Database Concepts Implemented

| Concept | Purpose |
|---|---|
| ER Diagram | Represents entities and their relationships. |
| Normalization | Reduces redundancy and improves data organization. |
| Primary Keys | Uniquely identify records. |
| Foreign Keys | Maintain relationships between tables. |
| Constraints | Enforce valid data. |
| Views | Display selected data through reusable queries. |
| Stored Procedures | Execute reusable database operations. |
| Functions | Perform reusable calculations or return values. |
| Triggers | Automatically respond to specified database events. |
| Transactions | Maintain consistency across related operations. |

---

## 🤖 AI/DS Component

### 🎯 Ticket Classification

The system includes a machine learning component designed to classify support tickets based on their text.

### 🔄 Classification Workflow

```text
📝 Ticket Subject & Description
              ↓
       🧹 Text Preprocessing
              ↓
       🔢 Text Vectorization
              ↓
       🤖 ML Classification
              ↓
       🗂️ Predicted Category
              ↓
       🎫 Ticket Categorization
```

### 🧪 Machine Learning Algorithms

- Multinomial Naive Bayes
- Logistic Regression

### 📌 Purpose

- Assist in categorizing incoming support tickets.
- Reduce the need for manual classification.
- Demonstrate the application of machine learning in a DBMS project.

*Actual classification performance depends on the training dataset and model evaluation.*

---

## 📊 Reports and Dashboard

The dashboard helps administrators and agents monitor ticket activity.

### 📈 Key Statistics

- 🎫 Total Tickets
- 🟡 Open Tickets
- 🔵 In-Progress Tickets
- 🟢 Closed Tickets
- 👨‍💼 Agent Workload
- 🗂️ Category-Wise Ticket Distribution

### 📉 Visualization

Charts can be used to display ticket status distribution, category-wise ticket counts, and other relevant statistics.

---

## 🔐 User Roles

| Role | Responsibilities |
|---|---|
| 👤 Customer | Create tickets and track their status. |
| 👨‍💼 Agent | Pick up assigned tickets and resolve customer issues. |
| 🛡️ Admin | Manage users, monitor tickets, and view reports. |

---

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

### 📋 Software used 

- Python 3.x
- MySQL Server 8.0
- XAMPP (if used for local MySQL/phpMyAdmin management)
- Git
- Visual Studio Code

 

## 📁 Project Structure

```text
CustomerSupportTicketManagementSystem/
│
├── 📂 templates/          # HTML templates
├── 📂 static/             # CSS, JavaScript, and assets
├── 📂 database/           # SQL scripts and database setup
├── 📂 models/             # Database models (if applicable)
├── 📂 routes/             # Flask routes (if applicable)
├── 📂 ml/                 # ML classification files (if applicable)
│
├── 📄 app.py              # Flask application entry point
├── 📄 requirements.txt    # Python dependencies
├── 📄 .env.example        # Example environment variables
├── 📄 .gitignore          # Git ignored files
└── 📄 README.md           # Project documentation
```

 
---

## 🚀 Future Enhancements

- 📧 Email notifications for ticket updates.
- ⏰ SLA tracking and response-time monitoring.
- 🤖 Improved automatic ticket classification.
- 📱 Responsive mobile-friendly interface.
- 📊 Advanced analytics and reporting.
- ⭐ Customer feedback and satisfaction ratings.

---

## 👨‍💻 Author

**Ayush Kurhade**

🎓 Artificial Intelligence and Data Science  
🏫 P. R. Pote Patil College of Engineering, Amravati

---

## 📜 License

This project was developed for academic and educational purposes as part of a DBMS mini project.