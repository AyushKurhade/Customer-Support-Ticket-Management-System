from flask import Blueprint
from backend.controllers.ai_controller import predict_ticket_category, get_model_info

ai_bp = Blueprint('ai_bp', __name__, url_prefix='/api/ai')

# AI Prediction Endpoint (accessible to authenticated users or during ticket creation)
ai_bp.add_url_rule('/predict-category', view_func=predict_ticket_category, methods=['POST'])
ai_bp.add_url_rule('/model-info', view_func=get_model_info, methods=['GET'])
