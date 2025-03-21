from flask import Flask, g
from flask_migrate import Migrate
from models import db
from auth import auth_bp
from routes import routes_bp
from config import Config
from datetime import datetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(routes_bp, url_prefix='')
    
    # Make datetime available globally
    @app.before_request
    def before_request():
        g.datetime = datetime
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True, host='0.0.0.0', port=5001)