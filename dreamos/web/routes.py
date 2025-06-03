"""
Routes for DreamOS web interface
"""
from flask import render_template, request, jsonify, session
from . import app, socketio
import os
import sys
import threading
import json
import time

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dreamos.agents.terminal_agent import TerminalAgent
from dreamos.utils.logging_utils import get_logger

# Initialize logger
logger = get_logger("web_interface")

# Store agent instance
terminal_agent = None
commands_history = []

@app.route('/')
def index():
    """Render the main interface."""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard."""
    return render_template('dashboard.html')

@app.route('/settings')
def settings():
    """Render the settings page."""
    return render_template('settings.html')

@app.route('/api/init', methods=['POST'])
def initialize_agent():
    """Initialize the terminal agent."""
    global terminal_agent
    
    try:
        data = request.json
        enable_voice = data.get('enable_voice', False)
        enable_dataviz = data.get('enable_dataviz', False)
        enable_dbquery = data.get('enable_dbquery', False)
        
        if terminal_agent is None:
            logger.info("Initializing Terminal Agent for web interface")
            terminal_agent = TerminalAgent(enable_voice=enable_voice)
            logger.info("Terminal Agent initialized successfully")
        
        return jsonify({
            'status': 'success',
            'message': 'Terminal agent initialized successfully',
            'features': {
                'voice': enable_voice,
                'dataviz': enable_dataviz,
                'dbquery': enable_dbquery
            }
        })
    
    except Exception as e:
        logger.error(f"Error initializing agent: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f"Error initializing agent: {str(e)}"
        }), 500

@app.route('/api/command', methods=['POST'])
def process_command():
    """Process a command through the terminal agent."""
    global terminal_agent, commands_history
    
    try:
        if terminal_agent is None:
            return jsonify({
                'status': 'error',
                'message': 'Terminal agent not initialized'
            }), 400
        
        data = request.json
        command = data.get('command', '')
        
        if not command:
            return jsonify({
                'status': 'error',
                'message': 'No command provided'
            }), 400
        
        logger.info(f"Processing command: '{command}'")
        
        # Process the command asynchronously and emit updates via Socket.IO
        def process_async():
            try:
                # Process the command
                response = terminal_agent.process_command(command)
                
                # Store in history
                commands_history.append({
                    'command': command,
                    'response': response,
                    'timestamp': time.time()
                })
                
                # Emit the response via Socket.IO
                socketio.emit('command_response', {
                    'command': command,
                    'response': response,
                    'status': 'success'
                })
            
            except Exception as e:
                logger.error(f"Error processing command: {str(e)}", exc_info=True)
                socketio.emit('command_response', {
                    'command': command,
                    'response': f"Error: {str(e)}",
                    'status': 'error'
                })
        
        # Start processing in a background thread
        threading.Thread(target=process_async).start()
        
        return jsonify({
            'status': 'processing',
            'message': 'Command is being processed'
        })
    
    except Exception as e:
        logger.error(f"Error in command API: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f"Error in command API: {str(e)}"
        }), 500

@app.route('/api/history')
def get_history():
    """Get command history."""
    global commands_history
    
    try:
        limit = request.args.get('limit', 10, type=int)
        history = commands_history[-limit:] if limit > 0 else commands_history
        
        return jsonify({
            'status': 'success',
            'history': history
        })
    
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f"Error retrieving history: {str(e)}"
        }), 500

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('command')
def handle_command(data):
    """Handle command via Socket.IO."""
    global terminal_agent
    
    try:
        if terminal_agent is None:
            logger.error("Terminal agent not initialized when processing Socket.IO command")
            socketio.emit('command_response', {
                'status': 'error',
                'message': 'Terminal agent not initialized. Please initialize DreamOS first.',
                'command': data.get('command', '')
            }, room=request.sid)
            return
        
        command = data.get('command', '')
        
        if not command:
            socketio.emit('command_response', {
                'status': 'error',
                'message': 'No command provided',
                'command': ''
            }, room=request.sid)
            return
        
        # Store the session ID in a local variable to use in the thread
        session_id = request.sid
        
        logger.info(f"Processing Socket.IO command: '{command}' from {session_id}")
        
        # Process the command asynchronously
        def process_async():
            try:
                response = terminal_agent.process_command(command)
                
                # Store in history
                commands_history.append({
                    'command': command,
                    'response': response,
                    'timestamp': time.time()
                })
                
                # Emit the response
                socketio.emit('command_response', {
                    'command': command,
                    'response': response,
                    'status': 'success'
                }, room=session_id)
            
            except Exception as e:
                logger.error(f"Error processing Socket.IO command: {str(e)}", exc_info=True)
                socketio.emit('command_response', {
                    'command': command,
                    'response': f"Error: {str(e)}",
                    'status': 'error'
                }, room=session_id)
        
        # Start processing in a background thread
        threading.Thread(target=process_async).start()
    
    except Exception as e:
        logger.error(f"Error handling Socket.IO command: {str(e)}", exc_info=True)
        socketio.emit('command_response', {
            'status': 'error',
            'message': f"Error: {str(e)}",
            'command': data.get('command', '')
        }, room=request.sid) 