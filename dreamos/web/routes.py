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
import uuid

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dreamos.agents.terminal_agent import TerminalAgent
from dreamos.utils.logging_utils import get_logger

# Initialize logger
logger = get_logger("web_interface")

# Store agent instances by session ID
terminal_agents = {}
commands_history = {}

@app.route('/')
def index():
    """Render the main interface."""
    # Generate a session ID if not present
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        logger.info(f"New session created: {session['session_id']}")
    
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard."""
    # Ensure session ID exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        logger.info(f"New session created: {session['session_id']}")
        
    return render_template('dashboard.html')

@app.route('/settings')
def settings():
    """Render the settings page."""
    # Ensure session ID exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        logger.info(f"New session created: {session['session_id']}")
        
    return render_template('settings.html')

@app.route('/api/init', methods=['POST'])
def initialize_agent():
    """Initialize the terminal agent."""
    global terminal_agents
    
    try:
        # Ensure session ID exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            logger.info(f"New session created: {session['session_id']}")
            
        session_id = session['session_id']
        data = request.json
        enable_voice = data.get('enable_voice', False)
        enable_dataviz = data.get('enable_dataviz', False)
        enable_dbquery = data.get('enable_dbquery', False)
        
        # Check if agent already exists for this session
        if session_id in terminal_agents and terminal_agents[session_id] is not None:
            logger.info(f"Terminal Agent already initialized for session {session_id}")
            agent = terminal_agents[session_id]
        else:
            logger.info(f"Initializing Terminal Agent for session {session_id}")
            # Always set web_mode=True to prevent server-side speech in web interface
            # The browser will handle speech synthesis
            agent = TerminalAgent(enable_voice=enable_voice, web_mode=True)
            terminal_agents[session_id] = agent
            commands_history[session_id] = []
            logger.info(f"Terminal Agent initialized successfully for session {session_id}")
        
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
    global terminal_agents, commands_history
    
    try:
        # Ensure session ID exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            logger.info(f"New session created: {session['session_id']}")
            
        session_id = session['session_id']
        
        if session_id not in terminal_agents or terminal_agents[session_id] is None:
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
        
        logger.info(f"Processing command for session {session_id}: '{command}'")
        
        # Capture the client's Socket.IO session ID
        client_sid = request.sid
        
        # Process the command asynchronously and emit updates via Socket.IO
        def process_async(command, session_id, client_sid):
            try:
                # Get agent for this session
                agent = terminal_agents[session_id]
                
                # Process the command
                response = agent.process_command(command)
                
                # Store in history
                if session_id not in commands_history:
                    commands_history[session_id] = []
                    
                commands_history[session_id].append({
                    'command': command,
                    'response': response,
                    'timestamp': time.time()
                })
                
                # Emit the response via Socket.IO
                socketio.emit('command_response', {
                    'command': command,
                    'response': response,
                    'status': 'success'
                }, room=client_sid)
            
            except Exception as e:
                logger.error(f"Error processing command: {str(e)}", exc_info=True)
                socketio.emit('command_response', {
                    'command': command,
                    'response': f"Error: {str(e)}",
                    'status': 'error'
                }, room=client_sid)
        
        # Start processing in a background thread
        threading.Thread(target=process_async, args=(command, session_id, client_sid)).start()
        
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
        # Ensure session ID exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            logger.info(f"New session created: {session['session_id']}")
            
        session_id = session['session_id']
        
        if session_id not in commands_history:
            commands_history[session_id] = []
        
        limit = request.args.get('limit', 10, type=int)
        history = commands_history[session_id][-limit:] if limit > 0 else commands_history[session_id]
        
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

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get real-time dashboard statistics."""
    global terminal_agents, commands_history
    
    try:
        # Ensure session ID exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            logger.info(f"New session created: {session['session_id']}")
            
        session_id = session['session_id']
        
        if session_id not in terminal_agents or terminal_agents[session_id] is None:
            return jsonify({
                'status': 'error',
                'message': 'Terminal agent not initialized'
            }), 400
        
        # Get agent for this session
        terminal_agent = terminal_agents[session_id]
        
        # Get memory stats
        memory_count = len(terminal_agent.memory_agent.get_all_memories())
        
        # Get file stats
        files = terminal_agent.file_agent.list_files()
        file_count = len(files)
        
        # Get plugin stats
        tools_used = set(terminal_agent.session_tools_used)
        tools_count = len(tools_used)
        
        # Get recent commands
        if session_id not in commands_history:
            commands_history[session_id] = []
            
        recent_activities = []
        for idx, history_item in enumerate(reversed(commands_history[session_id][-10:])):
            timestamp = history_item.get('timestamp', 0)
            time_ago = get_time_ago(timestamp)
            
            activity_type = "Terminal Command"
            description = f"User executed \"{history_item['command']}\" command"
            
            recent_activities.append({
                'type': activity_type,
                'description': description,
                'time': time_ago
            })
            
            if idx >= 9:  # Limit to 10 activities
                break
        
        # Get memory usage over time
        timestamps = []
        memory_counts = []
        
        # Get data for the last 7 days
        now = time.time()
        day_seconds = 24 * 60 * 60
        
        for i in range(6, -1, -1):
            day_timestamp = now - (i * day_seconds)
            day_label = "Today" if i == 0 else (
                "Yesterday" if i == 1 else f"{i} days ago"
            )
            timestamps.append(day_label)
            
            # Simulate memory growth over time since we don't store historical data
            # In a real implementation, this would pull from actual historical data
            memory_counts.append(max(10, memory_count - (i * 50)))
        
        # Command type distribution (categories count from history)
        command_types = {
            'Terminal': 0,
            'File Operations': 0,
            'Memory': 0,
            'Web Search': 0,
            'Visualization': 0,
            'Database': 0
        }
        
        # Analyze command history to categorize commands
        for item in commands_history[session_id]:
            cmd = item['command'].lower()
            if cmd.startswith(('read', 'write', 'search', 'list files')):
                command_types['File Operations'] += 1
            elif cmd.startswith(('remember', 'recall', 'forget', 'memories')):
                command_types['Memory'] += 1
            elif cmd.startswith(('web', 'search', 'browse', 'open')):
                command_types['Web Search'] += 1
            elif cmd.startswith('viz'):
                command_types['Visualization'] += 1
            elif cmd.startswith('db'):
                command_types['Database'] += 1
            else:
                command_types['Terminal'] += 1
        
        # Ensure there's always at least 1 in each category for visualization
        for key in command_types:
            if command_types[key] == 0:
                command_types[key] = 1
        
        return jsonify({
            'status': 'success',
            'system_status': {
                'memory': {
                    'active': True,
                    'details': f"{memory_count} memories stored"
                },
                'file': {
                    'active': True,
                    'details': f"{file_count} files managed"
                },
                'plugin': {
                    'active': True,
                    'details': f"{tools_count} tools loaded"
                }
            },
            'activities': recent_activities,
            'memory_usage': {
                'labels': timestamps,
                'values': memory_counts
            },
            'command_stats': {
                'labels': list(command_types.keys()),
                'values': list(command_types.values())
            }
        })
    
    except Exception as e:
        logger.error(f"Error retrieving dashboard stats: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f"Error retrieving dashboard stats: {str(e)}"
        }), 500

def get_time_ago(timestamp):
    """Convert timestamp to human-readable time ago format."""
    now = time.time()
    diff = now - timestamp
    
    if diff < 60:
        return "Just now"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = int(diff / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"

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
    global terminal_agents, commands_history
    
    try:
        # Ensure session ID exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            logger.info(f"New session created: {session['session_id']}")
            
        session_id = session['session_id']
        client_sid = request.sid  # Capture client's Socket.IO session ID
        
        if session_id not in terminal_agents or terminal_agents[session_id] is None:
            logger.error("Terminal agent not initialized when processing Socket.IO command")
            socketio.emit('command_response', {
                'status': 'error',
                'message': 'Terminal agent not initialized. Please initialize DreamOS first.',
                'command': data.get('command', '')
            }, room=client_sid)
            return
        
        command = data.get('command', '')
        
        if not command:
            socketio.emit('command_response', {
                'status': 'error',
                'message': 'No command provided',
                'command': ''
            }, room=client_sid)
            return
        
        logger.info(f"Processing Socket.IO command: '{command}' from {client_sid}")
        
        # Process the command asynchronously
        def process_async(command, session_id, client_sid):
            try:
                # Get agent for this session
                agent = terminal_agents[session_id]
                
                response = agent.process_command(command)
                
                # Store in history
                if session_id not in commands_history:
                    commands_history[session_id] = []
                    
                commands_history[session_id].append({
                    'command': command,
                    'response': response,
                    'timestamp': time.time()
                })
                
                # Emit the response
                socketio.emit('command_response', {
                    'command': command,
                    'response': response,
                    'status': 'success'
                }, room=client_sid)
            
            except Exception as e:
                logger.error(f"Error processing Socket.IO command: {str(e)}", exc_info=True)
                socketio.emit('command_response', {
                    'command': command,
                    'response': f"Error: {str(e)}",
                    'status': 'error'
                }, room=client_sid)
        
        # Start processing in a background thread with necessary parameters
        threading.Thread(target=process_async, args=(command, session_id, client_sid)).start()
    
    except Exception as e:
        logger.error(f"Error handling Socket.IO command: {str(e)}", exc_info=True)
        socketio.emit('command_response', {
            'status': 'error',
            'message': f"Error: {str(e)}",
            'command': data.get('command', '')
        }, room=request.sid)

@socketio.on('refresh_dashboard')
def handle_dashboard_refresh():
    """Handle dashboard refresh request via Socket.IO."""
    try:
        client_sid = request.sid  # Capture client's Socket.IO session ID
        
        # Get dashboard stats
        stats_response = get_dashboard_stats()
        
        # If stats_response is a tuple, it means there was an error
        if isinstance(stats_response, tuple):
            response_data = stats_response[0].json
            socketio.emit('dashboard_update', {
                'status': 'error',
                'message': response_data.get('message', 'Unknown error')
            }, room=client_sid)
            return
        
        # Emit the stats to the client
        socketio.emit('dashboard_update', stats_response.json, room=client_sid)
    
    except Exception as e:
        logger.error(f"Error refreshing dashboard: {str(e)}", exc_info=True)
        socketio.emit('dashboard_update', {
            'status': 'error',
            'message': f"Error refreshing dashboard: {str(e)}"
        }, room=request.sid) 