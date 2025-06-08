import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env if available
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Loaded environment variables from {dotenv_path}")
else:
    print("No .env file found, using environment variables from Vercel")
    
# Ensure SECRET_KEY is set
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'dreamos-vercel-deployment-secret'
    print("Warning: Using default SECRET_KEY. Set a proper SECRET_KEY in environment variables.")
    
# Set environment flag to disable audio features in Vercel environment
os.environ["DISABLE_AUDIO"] = "true"
print("Audio features disabled in Vercel environment")
    
# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create necessary directories (note: these operations may fail in Vercel environment)
try:
    os.makedirs("dreamos/memory", exist_ok=True)
    os.makedirs("dreamos/plugins", exist_ok=True)
    os.makedirs("dreamos/memory/visualizations", exist_ok=True)
    os.makedirs("dreamos/memory/databases", exist_ok=True)
    os.makedirs("dreamos/memory/metrics", exist_ok=True)
    os.makedirs("dreamos/logs", exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create directories: {e}")
    # This is expected in Vercel's read-only filesystem

# Import Flask app and socket.io
from dreamos.web import app, socketio

# Configure Socket.IO for Vercel
# Use long polling as primary transport method since WebSockets may not be supported
socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet', ping_timeout=10, ping_interval=5, 
                 transports=['polling', 'websocket'])

# This is for Vercel serverless functions
app.debug = False

# For Vercel deployment
if __name__ == "__main__":
    app.run()
    
# For serverless function handler
def handler(event, context):
    return app(event.get('body', {}), context) 