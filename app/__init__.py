from flask import Flask
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    # db.init_app(app)  # Uncomment if using database
    
    # Register blueprints
    from .routes import repo_routes
    app.register_blueprint(repo_routes.bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
        
    return app
