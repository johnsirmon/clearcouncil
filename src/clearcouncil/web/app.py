"""Flask web application for ClearCouncil."""

from flask import Flask, render_template, request, jsonify, send_file
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json

from ..config.settings import load_council_config, list_available_councils
from ..core.database import VectorDatabase
from .database import init_db, get_db_connection
from .charts import InteractiveChartGenerator
from .routes import api_bp, main_bp
from .insights_api import insights_bp
from .accessibility_integration import init_accessibility_features

logger = logging.getLogger(__name__)


def create_app(config_name='development'):
    """Create and configure the Flask app."""
    app = Flask(__name__)
    
    # Configuration
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        DATABASE_URL=os.environ.get('DATABASE_URL', 'sqlite:///clearcouncil.db'),
        UPLOAD_FOLDER=Path.cwd() / 'data' / 'uploads',
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
        SEND_FILE_MAX_AGE_DEFAULT=timedelta(hours=1)
    )
    
    # Ensure upload directory exists
    app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(insights_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Internal server error"), 500
    
    # Context processors
    @app.context_processor
    def inject_common_data():
        """Inject common data into all templates."""
        return {
            'councils': list_available_councils(),
            'current_year': datetime.now().year,
            'app_version': '2.0.0'
        }
    
    # Template filters
    @app.template_filter('datetime_format')
    def datetime_format(value, format='%Y-%m-%d %H:%M'):
        """Format datetime for display."""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return value
        return value.strftime(format) if value else ''
    
    @app.template_filter('truncate_text')
    def truncate_text(text, length=100):
        """Truncate text to specified length."""
        if len(text) <= length:
            return text
        return text[:length] + '...'
    
    # Initialize accessibility features
    init_accessibility_features(app)
    
    # Initialize logging
    if not app.debug:
        file_handler = logging.FileHandler('clearcouncil_web.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('ClearCouncil web application startup')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)