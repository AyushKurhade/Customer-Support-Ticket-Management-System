# Customer Support Ticket Management System
## AI / Data Science Component: Dataset Specification & Documentation (Phase 25)

---

### 1. Overview & Objective

Phase 25 provides the foundation for the AI triage and intelligent routing component of the Customer Support Ticket Management System. In modern enterprise IT and customer service architectures, manual triage of incoming tickets introduces human error and SLA delays. 

The objective of this phase is to construct a balanced, realistic, domain-specific dataset (`ai/dataset/ticket_data.csv`) that captures authentic IT support inquiries across hardware faults, software defects, network outages, identity & access management, billing disputes, and distributed technical issues.

This dataset will be utilized in **Phase 26** to train a lightweight, explainable Natural Language Processing (NLP) classification pipeline (**TF-IDF vectorizer + Multinomial Naive Bayes / Logistic Regression**).

---

### 2. Dataset Synthesis & Reproducibility

The dataset is generated programmatically via [ai/dataset/generate_dataset.py](file:///c:/Users/ASUS/.gemini/antigravity/scratch/CustomerSupportTicketManagementSystem/ai/dataset/generate_dataset.py) using a seeded random state (`seed=42`) ensuring **100% deterministic reproducibility**.

```
ai/
├── dataset/
│   ├── generate_dataset.py     # Deterministic dataset generation script
│   └── ticket_data.csv         # 720 balanced customer support ticket records
```

#### Synthesis Strategy:
1. **Core Domain Archetypes**: 15 distinct, verified technical scenarios curated for each category based on real-world enterprise IT tickets.
2. **Linguistic Variance**: Subject prefixes (`[Issue]`, `Urgent:`, `Help needed:`, `- Request assistance`) and contextual problem modifiers (e.g. impact statements, reproduction steps, hardware symptoms).
3. **Balanced Multiclass Distribution**: Exactly **120 rows per category** across 6 distinct categories, avoiding class-imbalance bias.
4. **Urgency-Aware Priority Labeling**: Issue severity and urgency indicators map to `Critical`, `High`, `Medium`, and `Low` priority classifications.

---

### 3. Attribute Definitions & Schema

The dataset file `ticket_data.csv` contains 720 rows and 6 columns:

| Column Name | Data Type | Constraint | Description | Example |
|---|---|---|---|---|
| `ticket_id` | Integer | `PRIMARY KEY`, `NOT NULL` | Sequential identifier for the ticket record | `1` |
| `subject` | String | `VARCHAR(255)`, `NOT NULL` | Short summary title of the customer inquiry | `External monitor not detected via HDMI` |
| `description` | Text | `TEXT`, `NOT NULL` | Comprehensive problem description and symptoms | `Connected an LG 27-inch monitor to workstation...` |
| `ticket_text` | Text | `TEXT`, `NOT NULL` | Combined subject and description for NLP tokenization | `External monitor not detected... Connected an...` |
| `category` | String | `VARCHAR(50)`, `NOT NULL` | Ground truth target classification label | `Hardware` |
| `priority` | String | `VARCHAR(20)`, `NOT NULL` | Target urgency label (Critical, High, Medium, Low) | `Medium` |

---

### 4. Statistical Distribution

#### Class Distribution (Categories)
Total records: **720** (100% balanced across all 6 classes):

| Category Label | Sample Count | Percentage Share | Typical Technical Keywords |
|---|---|---|---|
| **Hardware** | 120 | 16.67% | screen, battery, fan, monitor, keyboard, motherboard, ram, clicking, overheating |
| **Software** | 120 | 16.67% | crash, freeze, excel, outlook, dll, bsod, update, install, license, memory leak |
| **Network** | 120 | 16.67% | vpn, wifi, dns, latency, bandwidth, packet loss, firewall, port 443, gateway |
| **Account** | 120 | 16.67% | password, locked out, mfa, 2fa, sso, access denied, active directory, onboarding |
| **Payment** | 120 | 16.67% | invoice, refund, charged twice, credit card, vat, stripe, subscription, billing |
| **Technical Issue** | 120 | 16.67% | api, 500 error, database timeout, deadlock, webhook, celery, export, websocket |

#### Priority Distribution

| Priority Level | Sample Count | Percentage Share | SLA Target Reference |
|---|---|---|---|
| **High** | 271 | 37.64% | 24 Hours |
| **Medium** | 186 | 25.83% | 48 Hours |
| **Low** | 150 | 20.83% | 72 Hours |
| **Critical** | 113 | 15.70% | 4 Hours |

---

### 5. Representative Text Samples

#### 1. Hardware
> **Subject**: `Laptop battery swelling and trackpad lifting`  
> **Description**: `Noticeable bulge beneath the trackpad on my ThinkPad. The touchpad is physically displaced. Battery is dangerously swollen and won't hold charge. Urgent assistance required as this is blocking our production workflow.`  
> **Category**: `Hardware` | **Priority**: `Critical`

#### 2. Software
> **Subject**: `Excel crashes when opening large pivot table`  
> **Description**: `Microsoft Excel 365 freezes and abruptly crashes whenever I open our quarterly sales workbook containing 80,000 rows. Event Viewer logs faulting module ntdll.dll. This issue started occurring after the system maintenance yesterday.`  
> **Category**: `Software` | **Priority**: `High`

#### 3. Network
> **Subject**: `Corporate VPN disconnecting every 10 minutes`  
> **Description**: `Connected to the office VPN through Cisco AnyConnect, but the tunnel drops intermittently every 10 to 15 minutes with error: 'Connection terminated locally'. Tested across multiple workstations and the behavior is completely reproducible.`  
> **Category**: `Network` | **Priority**: `High`

#### 4. Account
> **Subject**: `User account locked out after failed password attempts`  
> **Description**: `Entered incorrect password on Monday morning and now my domain account is locked out. Need admin to unlock in Active Directory so I can login. Several other team members in our department are facing the exact same problem.`  
> **Category**: `Account` | **Priority**: `High`

#### 5. Payment
> **Subject**: `Credit card charged twice for annual subscription`  
> **Description**: `Our company credit card was charged $1,200 twice on September 15th for the annual enterprise license. Please reverse the duplicate transaction. This is severely impacting our daily operations and client deliverable deadlines.`  
> **Category**: `Payment` | **Priority**: `High`

#### 6. Technical Issue
> **Subject**: `REST API returning HTTP 500 Internal Server Error`  
> **Description**: `Calls to endpoint /api/v2/orders/batch are consistently failing with HTTP 500 Internal Server Error. Response payload contains uncaught NullPointerException. Logs and system diagnostic details have been captured and can be provided upon request.`  
> **Category**: `Technical Issue` | **Priority**: `Critical`

---

### 6. Preparation for NLP Model Training (Phase 26)

In Phase 26, the dataset will be processed through an scikit-learn training pipeline:
1. **Feature Extraction**: Text normalization, lowercasing, English stop-word removal, and n-gram TF-IDF vectorization (`ngram_range=(1, 2)`).
2. **Model Training**: Multinomial Naive Bayes classifier ($P(c|d) \propto P(c) \prod P(w_k|c)$) for ultra-fast, lightweight text classification.
3. **Artifact Persistence**: Serializing trained vectorizer and classifier using `joblib` into `ai/models/ticket_classifier.joblib`.

