#!/usr/bin/env python3
"""
ClearCouncil - Simple Working Server
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html><head><title>ClearCouncil</title></head>
    <body style="font-family: Arial; margin: 40px; background: #f5f5f5;">
        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h1 style="color: #2c3e50;">🏛️ ClearCouncil Server</h1>
            <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <strong>✅ Server is running successfully!</strong>
            </div>
            <h3>Available Endpoints:</h3>
            <ul>
                <li><a href="/health">🔍 Health Check</a></li>
                <li><a href="/status">📊 Server Status</a></li>
                <li><a href="/api/info">📡 API Info</a></li>
            </ul>
            <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Port:</strong> 5000<br>
                <strong>Host:</strong> localhost<br>
                <strong>Status:</strong> ✅ Online</p>
            </div>
        </div>
    </body></html>
    """

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'clearcouncil',
        'version': '1.0.0',
        'message': 'All systems operational'
    })

@app.route('/status')
def status():
    return """
    <html><body style="font-family: Arial; margin: 40px;">
        <h2>🔍 Server Status</h2>
        <div style="background: #d4edda; padding: 15px; border-radius: 5px;">
            ✅ All systems operational
        </div>
        <br>
        <p><a href="/">← Back to home</a></p>
    </body></html>
    """

@app.route('/api/info')
def api_info():
    return jsonify({
        'name': 'ClearCouncil API',
        'endpoints': ['/', '/health', '/status', '/api/info'],
        'working': True,
        'message': 'API is functional'
    })

if __name__ == '__main__':
    print("🚀 Starting ClearCouncil server...")
    print("🌐 Server will be available at: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/health")
    print("📊 Status page: http://localhost:5000/status")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
