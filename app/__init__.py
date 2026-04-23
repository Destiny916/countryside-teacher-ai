from flask import Flask, render_template
from flask_cors import CORS
from app.config import Config
import os
from dotenv import load_dotenv

def create_app(config_class=Config):
    # 加载环境变量
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/')
    def index():
        return render_template('index.html')

    from app.api import register_routes
    register_routes(app)

    return app
