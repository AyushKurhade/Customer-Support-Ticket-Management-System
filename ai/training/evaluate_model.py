"""
Comprehensive AI Model Evaluation & Explainability Analysis
------------------------------------------------------------
Performs 5-Fold Stratified Cross Validation, extracts Confusion Matrices,
analyzes top informative features (log likelihoods) per category,
and tests model resilience on noisy / out-of-domain queries.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def run_evaluation():
    base_dir = Path(__file__).resolve().parent.parent
    dataset_path = base_dir / "dataset" / "ticket_data.csv"
    model_path = base_dir / "models" / "ticket_classifier.joblib"

    print("=" * 75)
    print("AI MODEL EVALUATION & EXPLAINABILITY REPORT (PHASE 27)")
    print("=" * 75)

    df = pd.read_csv(dataset_path)
    X = df['ticket_text']
    y_cat = df['category']
    y_prio = df['priority']

    # 1. 5-Fold Stratified Cross-Validation
    print("\n[1] 5-Fold Stratified Cross-Validation Analysis:")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', max_features=5000, sublinear_tf=True)
    X_vec = vectorizer.fit_transform(X)

    clf_cat = MultinomialNB(alpha=0.1)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    cat_cv_scores = cross_val_score(clf_cat, X_vec, y_cat, cv=skf, scoring='accuracy')
    print(f"    Category Classification Cross-Val Scores (5 Folds): {[round(float(s), 4) for s in cat_cv_scores]}")
    print(f"    Mean Category Accuracy: {float(np.mean(cat_cv_scores)) * 100:.2f}% (+/- {float(np.std(cat_cv_scores)) * 100:.2f}%)")

    clf_prio = MultinomialNB(alpha=0.5)
    prio_cv_scores = cross_val_score(clf_prio, X_vec, y_prio, cv=skf, scoring='accuracy')
    print(f"    Priority Classification Cross-Val Scores (5 Folds): {[round(float(s), 4) for s in prio_cv_scores]}")
    print(f"    Mean Priority Accuracy: {float(np.mean(prio_cv_scores)) * 100:.2f}% (+/- {float(np.std(prio_cv_scores)) * 100:.2f}%)")

    # 2. Confusion Matrix & Detailed Metrics
    print("\n[2] Confusion Matrix for Category Classification:")
    clf_cat.fit(X_vec, y_cat)
    cat_preds = clf_cat.predict(X_vec)
    cm = confusion_matrix(y_cat, cat_preds, labels=clf_cat.classes_)

    cm_df = pd.DataFrame(cm, index=[f"True {c}" for c in clf_cat.classes_], columns=[f"Pred {c}" for c in clf_cat.classes_])
    print(cm_df.to_string())

    # 3. Model Explainability: Top Feature Keywords per Category
    print("\n[3] Model Explainability: Top Informative Keywords per Category")
    print("    (Calculated via feature log-probabilities: log P(w_k | c))")
    
    feature_names = vectorizer.get_feature_names_out()
    for i, category in enumerate(clf_cat.classes_):
        # Feature log probability array for class i
        log_probs = clf_cat.feature_log_prob_[i]
        top_indices = np.argsort(log_probs)[-8:][::-1]
        top_words = [feature_names[idx] for idx in top_indices]
        print(f"    * {category:<16}: {', '.join(top_words)}")

    # 4. Stress Testing: Typo & Out-of-Vocabulary Resilience
    print("\n[4] Robustness & Out-of-Vocabulary Stress Test:")
    test_cases = [
        ("Laptop screen is completely blank and hdmi port wont output display", "Hardware"),
        ("Forgot my paswrd and acct locked out in active directory", "Account"),
        ("Need refund for duble payment on my visa card", "Payment"),
        ("Vpn drops and internet disconects every 5 mins", "Network"),
        ("Excl keeps crashing when opening big file with error", "Software"),
        ("Api endpoint 500 error and db deadlock timeout", "Technical Issue")
    ]

    for noisy_text, expected in test_cases:
        noisy_vec = vectorizer.transform([noisy_text])
        pred = clf_cat.predict(noisy_vec)[0]
        conf = max(clf_cat.predict_proba(noisy_vec)[0])
        status = "MATCH" if pred == expected else "MISMATCH"
        print(f"    [{status}] \"{noisy_text}\"")
        print(f"            Expected: {expected} | Predicted: {pred} (Confidence: {conf*100:.1f}%)")

    print("\n" + "=" * 75)
    print("EVALUATION COMPLETED SUCCESSFULLY")
    print("=" * 75)

if __name__ == '__main__':
    run_evaluation()
