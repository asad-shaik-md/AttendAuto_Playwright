#!/usr/bin/env python3
"""
Jain University Attendance Checker - Web Application
===================================================

A Flask web application for checking attendance with real-time progress updates.
Features:
- Web-based interface
- Real-time progress updates via WebSocket
- Automated captcha solving with Gemini AI
- Results display and download

Author: Automated Attendance Checker
Date: August 2025
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import asyncio
import threading
import uuid
import os
import json
import socket
from datetime import datetime
import config
from attendance_checker import JainAttendanceChecker

def find_available_port(start_port=5001, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active sessions and their status
active_sessions = {}

class WebSocketLogger:
    """Custom logger that emits messages to WebSocket"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        
    def log(self, message, level='info'):
        """Emit log message to WebSocket"""
        # Send to all connected clients for now (can be improved later)
        socketio.emit('log_message', {
            'message': message,
            'level': level,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })

class WebAttendanceChecker(JainAttendanceChecker):
    """Extended attendance checker with WebSocket logging"""
    
    def __init__(self, session_id, username=None, password=None):
        super().__init__(username, password)
        self.session_id = session_id
        self.logger = WebSocketLogger(session_id)
        self.results = {}
        
    def log(self, message, level='info'):
        """Override logging to use WebSocket"""
        print(message)  # Keep console logging
        self.logger.log(message, level)
        
    async def run_with_websocket(self):
        """Run attendance checker with WebSocket progress updates"""
        try:
            self.log("🚀 Starting Jain University Attendance Checker", "info")
            
            # Update session status
            active_sessions[self.session_id]['status'] = 'running'
            active_sessions[self.session_id]['step'] = 'Setting up'
            
            # Setup Gemini AI
            self.log("🤖 Setting up Gemini AI...", "info")
            self.setup_gemini()
            self.log("✅ Gemini AI setup complete", "success")
            
            # Setup browser
            active_sessions[self.session_id]['step'] = 'Setting up browser'
            self.log("🌐 Setting up browser...", "info")
            await self.setup_browser()
            self.log("✅ Browser setup complete", "success")
            
            # Login
            active_sessions[self.session_id]['step'] = 'Logging in'
            self.log("🔐 Performing automated login... (This may take about 15 seconds.)", "info")
            login_success = await self.automated_login()
            
            if not login_success:
                self.log("❌ Login failed", "error")
                active_sessions[self.session_id]['status'] = 'failed'
                active_sessions[self.session_id]['error'] = 'Login failed'
                return False
                
            self.log("✅ Login successful!", "success")
            
            # Navigate to attendance page
            active_sessions[self.session_id]['step'] = 'Navigating to attendance page'
            self.log("📍 Navigating to attendance page...", "info")
            nav_success = await self.navigate_to_attendance_page()
            
            if not nav_success:
                self.log("❌ Failed to navigate to attendance page", "error")
                active_sessions[self.session_id]['status'] = 'failed'
                active_sessions[self.session_id]['error'] = 'Navigation failed'
                return False
                
            self.log("✅ Attendance page loaded successfully", "success")
            
            # Extract attendance data
            active_sessions[self.session_id]['step'] = 'Extracting attendance data'
            self.log("📊 Extracting attendance data... (This may take about 10 seconds.)", "info")
            await self.extract_attendance_data()
            
            # Calculate results
            active_sessions[self.session_id]['step'] = 'Calculating results'
            self.log("🧮 Calculating attendance results...", "info")
            self.calculate_and_display_results()
            
            # Store results in session
            results = self.prepare_results_for_web()
            active_sessions[self.session_id]['results'] = results
            active_sessions[self.session_id]['status'] = 'completed'
            
            self.log("🎉 Attendance check completed successfully!", "success")
            
            # Send results to frontend
            socketio.emit('attendance_results', results)
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Fatal error: {str(e)}"
            self.log(error_msg, "error")
            active_sessions[self.session_id]['status'] = 'failed'
            active_sessions[self.session_id]['error'] = str(e)
            return False
            
        finally:
            # Cleanup
            self.log("🧹 Cleaning up...", "info")
            await self.cleanup()
            self.log("✅ Cleanup complete", "success")
    
    def prepare_results_for_web(self):
        """Prepare attendance results for web display"""
        if not self.conducted_list or not self.attended_list:
            return None
            
        subjects = []
        for i, (conducted, attended) in enumerate(zip(self.conducted_list, self.attended_list)):
            percentage = (attended / conducted * 100) if conducted > 0 else 0
            
            # Get subject name if available, otherwise use default
            subject_name = "Subject"
            if hasattr(self, 'subject_names') and i < len(self.subject_names):
                subject_name = self.subject_names[i]
            else:
                subject_name = f"Subject {i + 1}"
            
            subjects.append({
                'id': i + 1,
                'name': subject_name,
                'conducted': conducted,
                'attended': attended,
                'percentage': round(percentage, 2)
            })
        
        total_conducted = sum(self.conducted_list)
        total_attended = sum(self.attended_list)
        overall_percentage = (total_attended / total_conducted * 100) if total_conducted > 0 else 0
        
        # Determine status
        if overall_percentage >= config.GOOD_ATTENDANCE_THRESHOLD:
            status = "GOOD"
            status_class = "success"
        elif overall_percentage >= config.WARNING_ATTENDANCE_THRESHOLD:
            status = "WARNING"
            status_class = "warning"
        else:
            status = "CRITICAL"
            status_class = "danger"
        
        return {
            'subjects': subjects,
            'total_conducted': total_conducted,
            'total_attended': total_attended,
            'overall_percentage': round(overall_percentage, 2),
            'status': status,
            'status_class': status_class,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/check-attendance', methods=['POST'])
def check_attendance():
    """Start attendance checking process"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Store session info
        active_sessions[session_id] = {
            'status': 'starting',
            'step': 'Initializing',
            'timestamp': datetime.now().isoformat(),
            'username': username
        }
        
        # Start attendance checking in background
        def run_checker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            checker = WebAttendanceChecker(session_id, username, password)
            loop.run_until_complete(checker.run_with_websocket())
            loop.close()
        
        thread = threading.Thread(target=run_checker)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Attendance checking started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>')
def get_session_status(session_id):
    """Get session status"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(active_sessions[session_id])

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_session')
def handle_join_session(data):
    """Join a specific session room"""
    session_id = data.get('session_id')
    if session_id:
        session['session_id'] = session_id
        # Use request.sid as the room name instead of session_id for simplicity
        # This ensures the client receives messages
        active_sessions[session_id]['socket_id'] = request.sid
        emit('joined_session', {'session_id': session_id})
        print(f"Client {request.sid} joined session {session_id}")

if __name__ == '__main__':
    print("Starting Jain University Attendance Checker Web App...")
    
    # Find an available port
    try:
        available_port = find_available_port(5001)
        print(f"Access the web interface at: http://localhost:{available_port}")
    except RuntimeError as e:
        print(f"Error: {e}")
        exit(1)
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=available_port, allow_unsafe_werkzeug=True)
