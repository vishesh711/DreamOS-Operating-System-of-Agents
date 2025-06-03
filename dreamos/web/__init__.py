"""
Web interface for DreamOS
"""
from flask import Flask
from flask_socketio import SocketIO

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
            
# Configure app
app.config['SECRET_KEY'] = 'dreamos-secret-key'

# Initialize SocketIO
socketio = SocketIO(app)

# Import routes
from . import routes 