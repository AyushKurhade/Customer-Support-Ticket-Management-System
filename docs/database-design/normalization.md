# Phase 6: Database Normalization (1NF, 2NF, 3NF Proofs & Viva Defense)

## 1. Overview
Normalization is a systematic database design technique that decomposes relations to eliminate **data redundancy** and avoid **data anomalies** (Insertion, Update, and Deletion anomalies) while preserving data integrity and functional dependencies.

In this document, we demonstrate step-by-step how an unnormalized "flat" ticket table is transformed into our normalized **Third Normal Form (3NF)** relational schema.

---

## 2. The Unnormalized State (UNF) & Its Anomalies

Imagine if we did not normalize and created a single "universal" table:

$$\text{Universal\_Ticket\_Table}(\underline{ticket\_id}, customer\_name, customer\_email, category\_name, category\_desc, priority\_name, sla\_hours, status\_name, agent\_name, agent\_email, subject, description, comments\_list, status\_history\_list, created\_at, resolved\_at)$$

### Why this design causes critical database anomalies:
1. **Insertion Anomaly:** We cannot add a new IT category (e.g., "Cybersecurity") into the database until a customer actually files a ticket in that category.
2. **Deletion Anomaly:** If a customer deletes their only support ticket, we unintentionally delete all knowledge of that customer's account and profile from the database.
3. **Update / Modification Anomaly:** If a customer changes their email address, we must update hundreds of rows across every ticket they ever submitted. If one row fails, the database becomes inconsistent.
4. **Non-Atomic Values:** A single ticket has multiple comments and multiple status changes, forcing repeating lists/arrays into a single cell.

---

## 3. Step 1: First Normal Form (1NF)

### What is 1NF?
> A relation is in **1NF** if and only if:
> 1. All attribute values are **atomic** (single, indivisible values; no comma-separated lists, sets, or JSON arrays).
> 2. There are **no repeating groups**.
> 3. Each row is uniquely identifiable by a **Primary Key**.

### Transitioning from UNF to 1NF:
In our initial UNF table, `comments_list` and `status_history_list` contained repeating, multi-valued items per ticket.
* We decompose the repeating groups into separate relations:
  * $\text{Ticket\_Comments}(\underline{comment\_id}, ticket\_id, user\_id, comment\_text, created\_at)$
  * $\text{Ticket\_Status\_History}(\underline{history\_id}, ticket\_id, old\_status\_id, new\_status\_id, changed\_by, changed\_at)$
* Every attribute in every table now holds exactly one scalar value.

**Result:** The schema satisfies **1NF**.

---

## 4. Step 2: Second Normal Form (2NF)

### What is 2NF?
> A relation is in **2NF** if and only if:
> 1. It is in **1NF**.
> 2. It has **NO Partial Functional Dependencies** — every non-key attribute must be **fully functionally dependent** on the entire primary key, not a proper subset of it.

### Why Partial Dependency occurs only with Composite Primary Keys:
A partial dependency can only exist when a table has a **composite primary key** (a primary key made of two or more columns).
For example, if we had defined a table:
$$\text{Ticket\_Assignment}(\underline{ticket\_id, agent\_id}, ticket\_subject, agent\_email)$$
Here:
* $ticket\_id \rightarrow ticket\_subject$ (depends only on part of the PK!)
* $agent\_id \rightarrow agent\_email$ (depends only on part of the PK!)
This violates 2NF because non-key attributes depend on only a portion of the composite key.

### How Our Schema Satisfies 2NF:
In our design, all relations use single-attribute surrogate primary keys:
* $\text{Users}(\underline{user\_id})$
* $\text{Categories}(\underline{category\_id})$
* $\text{Priorities}(\underline{priority\_id})$
* $\text{Ticket\_Status}(\underline{status\_id})$
* $\text{Tickets}(\underline{ticket\_id})$
* $\text{Ticket\_Comments}(\underline{comment\_id})$
* $\text{Ticket\_Status\_History}(\underline{history\_id})$

> **Mathematical Proof:** Since every primary key in our schema consists of exactly **one attribute**, no proper subset of a candidate key exists. Therefore, **no partial dependency can mathematically exist**.

**Result:** The schema strictly satisfies **2NF**.

---

## 5. Step 3: Third Normal Form (3NF)

### What is 3NF?
> A relation is in **3NF** if and only if:
> 1. It is in **2NF**.
> 2. It has **NO Transitive Functional Dependencies** — no non-prime attribute is transitively dependent on the primary key ($X \rightarrow Y$ and $Y \rightarrow Z$, where $Z$ is not a candidate key and $Y$ is not a superkey).

### Eliminating Transitive Dependencies in Our Project:

Consider the `Tickets` relation before isolating reference tables:
$$\text{Tickets\_Temp}(\underline{ticket\_id}, customer\_id, customer\_name, category\_id, category\_name, priority\_id, priority\_name, sla\_hours, status\_id, status\_name)$$

Here, the following functional dependencies exist:
* $ticket\_id \rightarrow customer\_id \rightarrow customer\_name$ ($customer\_name$ transitively depends on $ticket\_id$ through $customer\_id$).
* $ticket\_id \rightarrow category\_id \rightarrow category\_name$ ($category\_name$ transitively depends on $ticket\_id$ through $category\_id$).
* $ticket\_id \rightarrow priority\_id \rightarrow sla\_hours$ ($sla\_hours$ transitively depends on $ticket\_id$ through $priority\_id$).
* $ticket\_id \rightarrow status\_id \rightarrow status\_name$ ($status\_name$ transitively depends on $ticket\_id$ through $status\_id$).

### 3NF Decomposition:
We decompose the transitive dependencies into distinct reference tables where each non-key attribute depends directly on its own candidate/primary key:
1. $\text{Users}(\underline{\mathbf{user\_id}}, name, email, password\_hash, role, contact\_number, created\_at)$
   * $user\_id \rightarrow \{name, email, password\_hash, role, contact\_number, created\_at\}$
2. $\text{Categories}(\underline{\mathbf{category\_id}}, category\_name, description, created\_at)$
   * $category\_id \rightarrow \{category\_name, description, created\_at\}$
3. $\text{Priorities}(\underline{\mathbf{priority\_id}}, priority\_name, sla\_hours, created\_at)$
   * $priority\_id \rightarrow \{priority\_name, sla\_hours, created\_at\}$
4. $\text{Ticket\_Status}(\underline{\mathbf{status\_id}}, status\_name, is\_closed)$
   * $status\_id \rightarrow \{status\_name, is\_closed\}$
5. $\text{Tickets}(\underline{\mathbf{ticket\_id}}, customer\_id, category\_id, priority\_id, status\_id, assigned\_agent\_id, subject, description, created\_at, updated\_at, resolved\_at)$
   * $ticket\_id \rightarrow \{customer\_id, category\_id, priority\_id, status\_id, assigned\_agent\_id, subject, description, created\_at, updated\_at, resolved\_at\}$

In `Tickets`, all non-key attributes depend directly on `ticket_id` and nothing else.

**Result:** The schema strictly satisfies **3NF**.

---

## 6. Functional Dependency (FD) Summary

| Relation | Primary Key | Functional Dependencies (FDs) | Normal Form Achieved |
|---|---|---|:---:|
| **Users** | `user_id` | $user\_id \rightarrow name, email, password\_hash, role, contact\_number, created\_at$<br>$email \rightarrow user\_id$ | **3NF / BCNF** |
| **Categories** | `category_id` | $category\_id \rightarrow category\_name, description, created\_at$<br>$category\_name \rightarrow category\_id$ | **3NF / BCNF** |
| **Priorities** | `priority_id` | $priority\_id \rightarrow priority\_name, sla\_hours, created\_at$<br>$priority\_name \rightarrow priority\_id$ | **3NF / BCNF** |
| **Ticket_Status** | `status_id` | $status\_id \rightarrow status\_name, is\_closed$<br>$status\_name \rightarrow status\_id$ | **3NF / BCNF** |
| **Tickets** | `ticket_id` | $ticket\_id \rightarrow customer\_id, category\_id, priority\_id, status\_id, assigned\_agent\_id, subject, description, created\_at, updated\_at, resolved\_at$ | **3NF / BCNF** |
| **Ticket_Comments** | `comment_id` | $comment\_id \rightarrow ticket\_id, user\_id, comment\_text, is\_internal, created\_at$ | **3NF / BCNF** |
| **Ticket_Status_History** | `history_id` | $history\_id \rightarrow ticket\_id, old\_status\_id, new\_status\_id, changed\_by, remarks, changed\_at$ | **3NF / BCNF** |

---

## 7. Viva Defense Q&A

* **Q: What is Normalization and why did you perform it in this project?**
  * **Answer:** Normalization is the process of structuring relational tables to eliminate redundant data and avoid insert, update, and delete anomalies. In this project, it ensures that changes to customer profiles, categories, or SLAs are modified in exactly one place without duplicating data across thousands of ticket records.
* **Q: Why is your schema guaranteed to be in 2NF?**
  * **Answer:** A 2NF violation requires a partial dependency, which can only happen if a relation has a composite primary key. Because every table in our schema uses a single-column primary key (`user_id`, `ticket_id`, etc.), no attribute can depend on a subset of the key. Hence, partial dependency is impossible and 2NF is guaranteed.
* **Q: What is a Transitive Dependency and how did you resolve it?**
  * **Answer:** A transitive dependency occurs when non-key attribute $A$ determines non-key attribute $B$ ($PK \rightarrow A \rightarrow B$). For instance, if `Tickets` had stored `category_name`, then `ticket_id -> category_id -> category_name`. We resolved this by extracting `Categories` into its own relation with primary key `category_id`, storing only the foreign key `category_id` in `Tickets`.
* **Q: What is BCNF (Boyce-Codd Normal Form) and does your project satisfy it?**
  * **Answer:** A relation is in BCNF if for every functional dependency $X \rightarrow Y$, $X$ is a superkey. In all 7 relations in our project, every determinant is a superkey (either the primary key or a candidate key like `email` or `category_name`). Therefore, our database satisfies both 3NF and BCNF.
