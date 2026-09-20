import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask.json.provider import DefaultJSONProvider
from backend.config.config import Config
from backend.config.db import test_connection
from backend.routes.auth_routes import auth_bp

# Custom JSON Provider to cleanly serialize dates, timestamps, and decimals
class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, timedelta):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def create_app():
    base_dir = Path(__file__).resolve().parent.parent
    frontend_dir = base_dir / 'frontend'

    app = Flask(
        __name__,
        static_folder=str(frontend_dir),
        static_url_path='/static'
    )
    
    app.config.from_object(Config)
    app.json = CustomJSONProvider(app)

    # Register API Blueprints
    app.register_blueprint(auth_bp)

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_status = test_connection()
        return jsonify({
            'service': 'Customer Support Ticket Management API',
            'status': 'healthy',
            'database': db_status
        }), 200 if db_status.get('status') == 'connected' else 500

    # Serve index page
    @app.route('/')
    def index():
        index_file = frontend_dir / 'pages' / 'index.html'
        if index_file.exists():
            return send_from_directory(str(frontend_dir / 'pages'), 'index.html')
        return jsonify({
            'message': 'Customer Support Ticket Management System API is operational.',
            'health': '/api/health'
        })

    # Serve frontend pages (e.g. /login.html, /dashboard.html)
    @app.route('/<path:filename>')
    def serve_pages(filename):
        pages_dir = frontend_dir / 'pages'
        target = pages_dir / filename
        if target.exists() and target.is_file():
            return send_from_directory(str(pages_dir), filename)
        # Check direct frontend root
        root_target = frontend_dir / filename
        if root_target.exists() and root_target.is_file():
            return send_from_directory(str(frontend_dir), filename)
        return jsonify({'error': 'Page not found'}), 404

    # Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found', 'status_code': 404}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'status_code': 500}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Support Ticket API on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
