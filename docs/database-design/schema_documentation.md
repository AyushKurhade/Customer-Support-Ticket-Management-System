# Phase 7 & 8: Database Creation, Schema DDL & Constraints Documentation

## 1. Overview
This document specifies the Data Definition Language (DDL) implementation for the **Customer Support Ticket Management System** in MySQL 8.0 / MariaDB using the **InnoDB** storage engine.

---

## 2. Storage Engine: Why InnoDB?
In MySQL, tables can use different storage engines. We explicitly declare `ENGINE=InnoDB` on all 7 tables because:
1. **Foreign Key Enforcement**: InnoDB strictly checks and enforces referential integrity (`RESTRICT`, `CASCADE`, `SET NULL`). (Older engines like MyISAM silently ignore foreign key constraints).
2. **ACID Transaction Support**: InnoDB provides commit, rollback, and crash-recovery capabilities essential for Phase 16 transactions.
3. **Row-Level Locking**: High concurrency support when multiple agents and customers update different tickets simultaneously.

---

## 3. Constraints Implemented in DDL

| Constraint Type | SQL Implementation | Project Demonstration | Business Purpose |
|---|---|---|---|
| **PRIMARY KEY** | `CONSTRAINT pk_... PRIMARY KEY (col)` | All 7 tables | Guarantees entity integrity and creates clustered index. |
| **FOREIGN KEY** | `CONSTRAINT fk_... FOREIGN KEY ... REFERENCES ...` | `Tickets`, `Comments`, `Status_History` | Enforces referential integrity across related entities. |
| **UNIQUE** | `CONSTRAINT uq_... UNIQUE (col)` | `Users.email`, `Categories.category_name`, `Priorities.priority_name`, `Ticket_Status.status_name` | Prevents duplicate user accounts and duplicate master data entries. |
| **CHECK** | `CONSTRAINT chk_users_role CHECK (role IN ('customer', 'agent', 'admin'))`<br>`CONSTRAINT chk_priorities_sla CHECK (sla_hours > 0)` | `Users`, `Priorities` | Enforces domain integrity at database level; rejects invalid roles and non-positive SLA values. |
| **NOT NULL** | Explicit `NOT NULL` on required columns | Required columns in all tables | Disallows incomplete or missing mandatory records. |
| **DEFAULT** | `DEFAULT CURRENT_TIMESTAMP`, `DEFAULT FALSE`, `DEFAULT 24` | `created_at`, `is_closed`, `sla_hours` | Provides deterministic fallback values on INSERT. |

---

## 4. SQL Scripts Created

1. **[01_create_database.sql](file:///c:/Users/ASUS/.gemini/antigravity/scratch/CustomerSupportTicketManagementSystem/database/schema/01_create_database.sql)**:
   - Creates database `support_ticket_db` with `utf8mb4` encoding and `utf8mb4_unicode_ci` collation.
2. **[02_create_tables.sql](file:///c:/Users/ASUS/.gemini/antigravity/scratch/CustomerSupportTicketManagementSystem/database/schema/02_create_tables.sql)**:
   - Creates all 7 tables with explicit PKs, FKs, Unique constraints, Check constraints, and referential actions.
3. **[schema.sql](file:///c:/Users/ASUS/.gemini/antigravity/scratch/CustomerSupportTicketManagementSystem/database/schema/schema.sql)**:
   - All-in-one consolidated script for single-click execution in MySQL Workbench, CLI, or phpMyAdmin.

---

## 5. How to Execute in MySQL

### Option A: Via MySQL Command Line Client / Terminal
```powershell
# Using MySQL Server 8.0
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database/schema/schema.sql

# OR using XAMPP MySQL (default root with no password)
& "C:\xampp\mysql\bin\mysql.exe" -u root < database/schema/schema.sql
```

### Option B: Via MySQL Workbench
1. Launch **MySQL Workbench**.
2. Connect to your Local MySQL instance.
3. Open File $\rightarrow$ Browse to `database/schema/schema.sql`.
4. Click the **Lightning Bolt (Execute)** icon.
5. In the left Schema panel, right-click and click **Refresh All**; expand `support_ticket_db` $\rightarrow$ `Tables` to view all 7 tables.

---

## 6. Viva Defense Notes

* **Q: Why is character set `utf8mb4` preferred over standard `utf8` in MySQL?**
  * **Answer:** MySQL's legacy `utf8` charset only supports up to 3 bytes per character, failing on modern 4-byte Unicode characters (including emojis, symbols, and diverse language scripts). `utf8mb4` provides full 4-byte UTF-8 support.
* **Q: What is the difference between `ON DELETE CASCADE`, `ON DELETE RESTRICT`, and `ON DELETE SET NULL`?**
  * **Answer:**
    - `CASCADE`: Deleting parent row automatically deletes all matching child rows (e.g., deleting a ticket purges its comments).
    - `RESTRICT`: Prevents deletion of the parent row if any referencing child row exists (e.g., cannot delete a customer while they have active tickets).
    - `SET NULL`: Deleting the parent row automatically sets the foreign key in child rows to `NULL` (e.g., deactivating an agent unassigns their tickets rather than deleting them).

