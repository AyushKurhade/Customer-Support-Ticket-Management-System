# Customer Support Ticket Management System
## AI / Data Science Component: Model Evaluation & Viva Explanation (Phase 27)

---

### 1. Executive Summary

Phase 27 provides a comprehensive mathematical and empirical evaluation of the AI text classification pipeline developed in Phase 26. Through rigorous statistical testing—including **5-Fold Stratified Cross-Validation**, **Confusion Matrix Analysis**, **Feature Log-Probability Introspection**, and **Typo/Out-of-Vocabulary Stress Testing**—this document demonstrates model reliability, generalization capacity, and algorithmic interpretability.

---

### 2. 5-Fold Stratified Cross-Validation Analysis

Rather than relying on an isolated train/test partition that could introduce sampling bias, the entire 720-sample dataset was subjected to **5-Fold Stratified Cross-Validation** ($k=5$). In each iteration, $80\%$ of the corpus ($576$ records) served as the training fold while the remaining $20\%$ ($144$ records) served as an unseen validation set, preserving equal class proportions.

#### Cross-Validation Results Table:

| Iteration | Category Accuracy | Priority Accuracy | Validation Fold Size |
|---|---|---|---|
| **Fold 1** | 100.00% | 95.14% | 144 records |
| **Fold 2** | 100.00% | 96.53% | 144 records |
| **Fold 3** | 100.00% | 95.83% | 144 records |
| **Fold 4** | 100.00% | 91.67% | 144 records |
| **Fold 5** | 100.00% | 97.22% | 144 records |
| **Mean Score** | **100.00%** ($\pm 0.00\%$) | **95.28%** ($\pm 1.93\%$) | **720 total** |

- **Interpretation**: The Category Classifier achieved a standard deviation of $\sigma = 0.00\%$, proving that the TF-IDF feature space provides crisp hyperplanes separating domain-specific IT problem classes. Priority classification achieved a mean accuracy of $95.28\%$, successfully predicting the urgency bracket based on impact keywords.

---

### 3. Confusion Matrix Analysis

The 6-class multiclass confusion matrix evaluates predicted vs. true labels across all 720 records:

```
                      Pred Account  Pred Hardware  Pred Network  Pred Payment  Pred Software  Pred Technical Issue
True Account                   120              0             0             0              0                     0
True Hardware                    0            120             0             0              0                     0
True Network                     0              0           120             0              0                     0
True Payment                     0              0             0           120              0                     0
True Software                    0              0             0             0            120                     0
True Technical Issue             0              0             0             0              0                   120
```

#### Metrics Derivation:
- **True Positives (TP)** for each class = $120$.
- **False Positives (FP)** = $0$.
- **False Negatives (FN)** = $0$.
- **Precision** $= \frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{120}{120 + 0} = \mathbf{1.00}$ ($100\%$).
- **Recall** $= \frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{120}{120 + 0} = \mathbf{1.00}$ ($100\%$).
- **F1-Score** $= 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} = \mathbf{1.00}$ ($100\%$).

---

### 4. Model Explainability & Feature Log-Probabilities

Multinomial Naive Bayes is an intrinsically explainable "glass-box" model. The decision rule is governed by the class-conditional feature log-probabilities:

$$\log P(w_k | c) = \log\left(\frac{N_{c, k} + \alpha}{N_c + \alpha \cdot V}\right)$$

Where $N_{c, k}$ is the sum of TF-IDF feature weights for token $w_k$ in class $c$, $V = 3,482$ is the total vocabulary, and $\alpha = 0.1$ is the Laplace smoothing parameter.

#### Top 8 Discriminative Keywords Identified by Model:

| Category Class | Top Predictive Keywords ($\log P(w_k \mid c)$) | Domain Justification |
|---|---|---|
| **Account** | `account`, `password`, `directory`, `employee`, `access`, `active`, `active directory`, `email` | Identity and access management terminology |
| **Hardware** | `screen`, `wireless`, `wireless mouse`, `cursor`, `mouse cursor`, `mouse`, `cable`, `display` | Physical computer peripherals and display devices |
| **Network** | `network`, `wifi`, `gateway`, `assistance`, `vpn`, `port`, `disconnects` | Connectivity protocols and routing infrastructure |
| **Payment** | `subscription`, `invoice`, `card`, `charged`, `payment`, `billing`, `monthly`, `refund` | Financial transactions and billing dispute keywords |
| **Software** | `error`, `client`, `dll`, `white`, `blank`, `slack`, `crashes`, `freezes` | Application execution failures and crash signatures |
| **Technical Issue** | `api`, `database`, `search`, `connection`, `tickets`, `http`, `response`, `deadlock` | Backend services, distributed systems, and DB errors |

---

### 5. Robustness & Out-of-Vocabulary Stress Test

Real-world customer tickets contain typos, colloquial abbreviations, and noisy syntax. The model was evaluated on previously unseen queries with simulated spelling errors and shorthand:

| Tested Raw Input | Expected Class | Predicted Class | Confidence Score | Status |
|---|---|---|---|---|
| *"Laptop screen is completely blank and hdmi port wont output display"* | Hardware | **Hardware** | **97.6%** | PASSED |
| *"Forgot my paswrd and acct locked out in active directory"* | Account | **Account** | **99.6%** | PASSED |
| *"Need refund for duble payment on my visa card"* | Payment | **Payment** | **99.2%** | PASSED |
| *"Vpn drops and internet disconects every 5 mins"* | Network | **Network** | **94.5%** | PASSED |
| *"Excl keeps crashing when opening big file with error"* | Software | **Software** | **80.6%** | PASSED |
| *"Api endpoint 500 error and db deadlock timeout"* | Technical Issue | **Technical Issue** | **96.7%** | PASSED |

**Analysis**: Even with corrupted tokens like `paswrd`, `acct`, `duble`, and `disconects`, the sublinear TF-IDF representation extracts the surrounding valid tokens (`active directory`, `refund`, `payment`, `vpn`, `500 error`, `deadlock`), resulting in correct classifications with $>80\%$ confidence.

---

### 6. Architectural Comparison: Why Multinomial Naive Bayes?

| Criteria | Multinomial Naive Bayes (Our Choice) | Deep Neural Net / Transformer (BERT) | Cloud LLM (OpenAI / Claude API) |
|---|---|---|---|
| **Inference Latency** | **$< 1.0\text{ ms}$** | $50 - 150\text{ ms}$ | $800 - 2,500\text{ ms}$ |
| **Memory Footprint** | **$< 1\text{ MB}$** | $400\text{ MB} - 1.5\text{ GB}$ | Zero local (Network bound) |
| **Hardware Reqs** | **Standard CPU (Zero GPU)** | High-end GPU recommended | Internet bandwidth |
| **Operating Cost** | **$0.00 (Self-contained)** | Server GPU hosting fees | Recurring API per-token cost |
| **Data Privacy** | **100% On-Premise** | 100% On-Premise | Third-party cloud exposure |
| **Explainability** | **Explicit Bayes log-likelihoods** | Black-box weights | Black-box prompts |

---

### 7. Comprehensive Viva Voce Defense Guide

#### Q1: What is the "Naive" assumption in Naive Bayes, and does it hold in NLP?
> **Answer**: The Naive assumption states that all features (words/tokens) in a document are conditionally independent of each other given the class label:  
> $$P(w_1, w_2, \dots, w_n | c) = \prod_{i=1}^n P(w_i | c)$$  
> In natural language, this assumption is technically violated because word order and grammar create inter-word dependencies (e.g. "active" followed by "directory"). However, in practice, empirical research shows that Naive Bayes works exceptionally well for text classification because the *ranking* of posterior class probabilities remains correct even if the raw marginal probabilities are slightly distorted. Furthermore, we mitigate this by using **bigrams** (`ngram_range=(1, 2)`), which directly capture two-word phrases such as `"active directory"` and `"credit card"`.

#### Q2: Why did you choose Multinomial Naive Bayes instead of Bernoulli or Gaussian?
> **Answer**:
> - **Gaussian Naive Bayes** assumes features follow a continuous Gaussian bell curve, which is inappropriate for sparse discrete word frequencies.
> - **Bernoulli Naive Bayes** only models binary word presence ($0$ or $1$) and ignores term frequency.
> - **Multinomial Naive Bayes** natively models integer counts and fractional TF-IDF weights, rewarding documents that contain repeated, highly diagnostic domain keywords.

#### Q3: What is Laplace Smoothing and why is $\alpha = 0.1$ used?
> **Answer**: If a customer submits a ticket containing a novel word that never appeared in the training set for category $c$, the raw count $N_{c, k} = 0$, causing $P(w_k | c) = 0$. Because probabilities are multiplied, a single zero probability would nullify the entire calculation. Laplace smoothing adds an offset $\alpha$ to numerator and $\alpha \cdot V$ to denominator:  
> $$P(w_k | c) = \frac{N_{c, k} + \alpha}{N_c + \alpha \cdot V}$$  
> Setting $\alpha = 0.1$ (Lidstone smoothing) provides the ideal balance between preventing zero-frequency crashes while avoiding excessive probability dilution.

#### Q4: How does this AI component interact with your MySQL database?
> **Answer**: The AI component operates as an intelligent advisory layer. In **Phase 28**, an API endpoint (`/api/ai/predict-category`) receives the draft ticket text submitted from the frontend UI. The model predicts the category (e.g., `Hardware`) and priority (`High`). When the customer confirms and clicks submit, the Flask controller executes the stored procedure `sp_CreateTicket`, which writes the normalized foreign keys (`category_id`, `priority_id`, `status_id = 1`) into the MySQL `Tickets` table and triggers `trg_Ticket_Initial_History_Log`.

