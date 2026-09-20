"""
Customer Support Ticket Classifier - Inference Engine
-----------------------------------------------------
Loads the serialized model bundle from ai/models/ticket_classifier.joblib
and provides high-speed, local text classification inference.
"""

from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "ticket_classifier.joblib"
_model_bundle = None

def get_model():
    global _model_bundle
    if _model_bundle is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model artifact not found at {MODEL_PATH}. Run train_model.py first.")
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle

def predict_ticket(text: str):
    """
    Predicts category and recommended priority for raw ticket text.
    Returns:
        dict: {
            'category': str,
            'confidence': float,
            'priority': str,
            'priority_confidence': float
        }
    """
    if not text or not text.strip():
        return {
            'category': 'Other',
            'confidence': 0.0,
            'priority': 'Low',
            'priority_confidence': 0.0
        }

    bundle = get_model()
    vectorizer = bundle['vectorizer']
    cat_clf = bundle['category_classifier']
    prio_clf = bundle['priority_classifier']

    # Vectorize input text
    vec_text = vectorizer.transform([text.strip()])

    # Predict Category
    cat_pred = cat_clf.predict(vec_text)[0]
    cat_probs = cat_clf.predict_proba(vec_text)[0]
    cat_conf = float(max(cat_probs))

    # Predict Priority
    prio_pred = prio_clf.predict(vec_text)[0]
    prio_probs = prio_clf.predict_proba(vec_text)[0]
    prio_conf = float(max(prio_probs))

    return {
        'category': str(cat_pred),
        'confidence': round(cat_conf, 4),
        'priority': str(prio_pred),
        'priority_confidence': round(prio_conf, 4)
    }

if __name__ == '__main__':
    sample = "The screen on my company laptop is flickering and turns off when opened wide."
    print("Testing sample inference:")
    print("Input:", sample)
    result = predict_ticket(sample)
    print("Result:", result)
