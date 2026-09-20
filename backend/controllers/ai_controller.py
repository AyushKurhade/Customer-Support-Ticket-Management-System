import json
from pathlib import Path
from flask import request, jsonify
from ai.training.predict import predict_ticket
from backend.config.db import execute_query

METADATA_PATH = Path(__file__).resolve().parent.parent.parent / "ai" / "models" / "model_metadata.json"

def predict_ticket_category():
    """
    POST /api/ai/predict-category
    Takes raw ticket text (or subject + description), passes it through the
    TF-IDF + Multinomial Naive Bayes pipeline, and maps results to database entities.
    """
    data = request.get_json() or {}
    text = data.get('text', '').strip()

    if not text:
        # Check if subject and description were passed separately
        subj = data.get('subject', '').strip()
        desc = data.get('description', '').strip()
        text = f"{subj} {desc}".strip()

    if not text:
        return jsonify({
            'error': 'Text is required for AI categorization',
            'status_code': 400
        }), 400

    # Run local ML inference
    prediction = predict_ticket(text)
    category_name = prediction.get('category', 'Other')
    priority_name = prediction.get('priority', 'Medium')
    confidence = prediction.get('confidence', 0.0)
    priority_confidence = prediction.get('priority_confidence', 0.0)

    # Map to MySQL Category entity
    cat_rows = execute_query(
        "SELECT category_id, category_name FROM Categories WHERE LOWER(category_name) = LOWER(%s) LIMIT 1",
        (category_name,)
    )
    if cat_rows:
        category_id = cat_rows[0]['category_id']
        category_name = cat_rows[0]['category_name']
    else:
        # Fallback to Other
        other_row = execute_query("SELECT category_id FROM Categories WHERE category_name = 'Other' LIMIT 1")
        category_id = other_row[0]['category_id'] if other_row else 7

    # Map to MySQL Priority entity
    prio_rows = execute_query(
        "SELECT priority_id, priority_name, sla_hours FROM Priorities WHERE LOWER(priority_name) = LOWER(%s) LIMIT 1",
        (priority_name,)
    )
    if prio_rows:
        priority_id = prio_rows[0]['priority_id']
        priority_name = prio_rows[0]['priority_name']
        sla_hours = prio_rows[0]['sla_hours']
    else:
        # Fallback to Medium (id=2)
        priority_id = 2
        priority_name = 'Medium'
        sla_hours = 48

    return jsonify({
        'success': True,
        'input_preview': text[:100] + ('...' if len(text) > 100 else ''),
        'category_name': category_name,
        'category_id': category_id,
        'confidence': confidence,
        'priority_name': priority_name,
        'priority_id': priority_id,
        'priority_confidence': priority_confidence,
        'sla_hours': sla_hours
    }), 200

def get_model_info():
    """
    GET /api/ai/model-info
    Returns the active AI model configuration, training metrics, and vocabulary size.
    """
    if METADATA_PATH.exists():
        with open(METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return jsonify({
            'status': 'loaded',
            'model_info': metadata
        }), 200
    else:
        return jsonify({
            'status': 'not_found',
            'message': 'Model metadata file not found. Train model first.'
        }), 404
