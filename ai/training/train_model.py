"""
Customer Support Ticket AI Classification Model Trainer
-------------------------------------------------------
Trains a lightweight, highly explainable text classification pipeline using
TF-IDF (Term Frequency - Inverse Document Frequency) and Multinomial Naive Bayes.
Saves serialized model artifacts to ai/models/ticket_classifier.joblib.
"""

import json
import datetime
from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

def train_and_save_model():
    base_dir = Path(__file__).resolve().parent.parent
    dataset_path = base_dir / "dataset" / "ticket_data.csv"
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    model_file = models_dir / "ticket_classifier.joblib"
    metadata_file = models_dir / "model_metadata.json"

    print("=" * 70)
    print("CUSTOMER SUPPORT TICKET - AI CLASSIFIER TRAINING PIPELINE")
    print("=" * 70)

    # 1. Load Dataset
    print(f"\n[1/6] Loading dataset from: {dataset_path}")
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}. Run generate_dataset.py first.")
    
    df = pd.read_csv(dataset_path)
    print(f"      Total records loaded: {len(df)}")
    print(f"      Classes: {sorted(df['category'].unique())}")

    X = df['ticket_text']
    y_cat = df['category']
    y_prio = df['priority']

    # 2. Train / Test Split (80% Train, 20% Test with Stratification)
    print("\n[2/6] Splitting dataset (80% Train, 20% Test, Stratified)...")
    X_train, X_test, y_cat_train, y_cat_test, y_prio_train, y_prio_test = train_test_split(
        X, y_cat, y_prio, test_size=0.20, random_state=42, stratify=y_cat
    )
    print(f"      Training samples: {len(X_train)}")
    print(f"      Testing samples:  {len(X_test)}")

    # 3. TF-IDF Feature Extraction
    print("\n[3/6] Fitting TF-IDF Vectorizer (ngram_range=(1,2), sublinear_tf=True)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words='english',
        max_features=5000,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    feature_count = len(vectorizer.get_feature_names_out())
    print(f"      Extracted vocabulary features: {feature_count}")

    # 4. Train Classifiers
    print("\n[4/6] Training Multinomial Naive Bayes Classifiers...")
    # Category classifier
    cat_clf = MultinomialNB(alpha=0.1)
    cat_clf.fit(X_train_vec, y_cat_train)
    cat_pred = cat_clf.predict(X_test_vec)
    cat_acc = accuracy_score(y_cat_test, cat_pred)
    print(f"      Category Classification Accuracy: {cat_acc * 100:.2f}%")

    # Priority classifier
    prio_clf = MultinomialNB(alpha=0.5)
    prio_clf.fit(X_train_vec, y_prio_train)
    prio_pred = prio_clf.predict(X_test_vec)
    prio_acc = accuracy_score(y_prio_test, prio_pred)
    print(f"      Priority Classification Accuracy: {prio_acc * 100:.2f}%")

    # Detailed Category Classification Report
    print("\n--- Detailed Category Classification Report ---")
    report_dict = classification_report(y_cat_test, cat_pred, output_dict=True)
    print(classification_report(y_cat_test, cat_pred))

    # 5. Persist Model Bundle
    print(f"\n[5/6] Serializing model bundle to: {model_file}")
    model_bundle = {
        'vectorizer': vectorizer,
        'category_classifier': cat_clf,
        'priority_classifier': prio_clf,
        'categories': list(cat_clf.classes_),
        'priorities': list(prio_clf.classes_),
        'metrics': {
            'category_accuracy': round(float(cat_acc), 4),
            'priority_accuracy': round(float(prio_acc), 4),
            'test_samples': int(len(X_test)),
            'train_samples': int(len(X_train)),
            'vocabulary_size': int(feature_count)
        },
        'metadata': {
            'algorithm': 'Multinomial Naive Bayes + TF-IDF (1, 2) n-grams',
            'trained_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'dataset': 'ticket_data.csv (720 records)'
        }
    }
    joblib.dump(model_bundle, model_file)

    # Save JSON metadata for easy viewing
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            'model_file': str(model_file.name),
            'algorithm': model_bundle['metadata']['algorithm'],
            'trained_at': model_bundle['metadata']['trained_at'],
            'categories': model_bundle['categories'],
            'priorities': model_bundle['priorities'],
            'metrics': model_bundle['metrics']
        }, f, indent=4)
    print(f"      Model metadata saved to: {metadata_file}")

    # 6. Inference Verification on Novel Test Queries
    print("\n[6/6] Live Verification on Novel IT Queries:")
    sample_queries = [
        "External monitor connected with HDMI has no signal and screen is black",
        "Unable to launch Outlook, crashes immediately with missing dll error",
        "Office WiFi disconnects every 10 minutes and VPN drops connection",
        "Account locked out after multiple failed password login attempts",
        "Company credit card charged twice for annual subscription renewal invoice",
        "REST API endpoint /api/orders returning 500 internal server error with database deadlock"
    ]

    for q in sample_queries:
        q_vec = vectorizer.transform([q])
        pred_c = cat_clf.predict(q_vec)[0]
        prob_c = max(cat_clf.predict_proba(q_vec)[0])
        pred_p = prio_clf.predict(q_vec)[0]
        prob_p = max(prio_clf.predict_proba(q_vec)[0])
        print(f"  Query: \"{q[:50]}...\"")
        print(f"    -> Predicted Category: {pred_c:<15} (Conf: {prob_c*100:.1f}%) | Priority: {pred_p} (Conf: {prob_p*100:.1f}%)")

    print("\n" + "=" * 70)
    print("MODEL TRAINING & SERIALIZATION COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == '__main__':
    train_and_save_model()

