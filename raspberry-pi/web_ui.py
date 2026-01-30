#!/usr/bin/env python3
"""
Flask Web UI for BlueZscript Pairing Management
Provides web interface for device pairing and management
"""

from flask import Flask, render_template, jsonify, request, send_file
import qrcode
import io
import json
import logging
from datetime import datetime
from functools import wraps
import time

from pairing_manager import PairingManager
from crypto_utils import CryptoUtils

logger = logging.getLogger(__name__)

# Configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000
DEBUG = False

# Rate limiting (simple in-memory)
pairing_requests = {}  # IP -> last request time
RATE_LIMIT_SECONDS = 60  # 1 pairing request per minute per IP

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = CryptoUtils.generate_secret()  # For session security

# Initialize pairing manager
pairing_manager = PairingManager()


def rate_limit(f):
    """Decorator for rate limiting pairing requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        if client_ip in pairing_requests:
            last_request = pairing_requests[client_ip]
            if current_time - last_request < RATE_LIMIT_SECONDS:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Please wait {RATE_LIMIT_SECONDS} seconds between pairing requests'
                }), 429
        
        pairing_requests[client_ip] = current_time
        return f(*args, **kwargs)
    
    return decorated_function


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


# ============================================================================
# WEB ROUTES (HTML Pages)
# ============================================================================

@app.route('/')
def index():
    """Dashboard - List all paired devices."""
    try:
        devices = pairing_manager.list_devices()
        device_count = pairing_manager.get_device_count()
        
        # Format timestamps for display
        for device in devices:
            device['paired_at_str'] = datetime.fromtimestamp(device['paired_at']).strftime('%Y-%m-%d %H:%M:%S')
            if device['last_used']:
                device['last_used_str'] = datetime.fromtimestamp(device['last_used']).strftime('%Y-%m-%d %H:%M:%S')
            else:
                device['last_used_str'] = 'Never'
        
        return render_template('index.html', 
                             devices=devices, 
                             device_count=device_count)
    
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/pair/new')
@rate_limit
def pair_new():
    """Generate new pairing QR code."""
    try:
        # Generate new device credentials
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        # Store in session for completion
        pairing_data = {
            'device_id': device_id,
            'secret': secret,
            'server_url': request.host_url.rstrip('/')
        }
        
        return render_template('pair.html', 
                             device_id=device_id,
                             pairing_data=json.dumps(pairing_data))
    
    except Exception as e:
        logger.error(f"Error generating pairing: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/help')
def help_page():
    """Help and documentation page."""
    return render_template('help.html')


# ============================================================================
# API ROUTES (JSON Responses)
# ============================================================================

@app.route('/api/devices', methods=['GET'])
def api_list_devices():
    """API: List all paired devices."""
    try:
        devices = pairing_manager.list_devices()
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices)
        })
    
    except Exception as e:
        logger.error(f"API error listing devices: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/devices/<device_id>', methods=['GET'])
def api_get_device(device_id):
    """API: Get device details (without secret)."""
    try:
        if not pairing_manager.device_exists(device_id):
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        device = pairing_manager.get_device(device_id)
        # Remove secret from response
        device.pop('secret_key', None)
        
        return jsonify({
            'success': True,
            'device': device
        })
    
    except Exception as e:
        logger.error(f"API error getting device: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/devices/<device_id>/revoke', methods=['POST'])
def api_revoke_device(device_id):
    """API: Revoke device pairing."""
    try:
        if not pairing_manager.device_exists(device_id):
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        result = pairing_manager.remove_device(device_id)
        
        if result:
            logger.info(f"Device revoked via API: {device_id}")
            return jsonify({
                'success': True,
                'message': 'Device pairing revoked'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to revoke device'
            }), 500
    
    except Exception as e:
        logger.error(f"API error revoking device: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/devices/complete', methods=['POST'])
def api_complete_pairing():
    """API: Complete device pairing with name."""
    try:
        data = request.get_json()
        
        if not data or 'device_id' not in data or 'device_name' not in data or 'secret' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: device_id, device_name, secret'
            }), 400
        
        device_id = data['device_id']
        device_name = data['device_name']
        secret = data['secret']
        
        # Validate device_name
        if not device_name or len(device_name.strip()) == 0:
            return jsonify({
                'success': False,
                'error': 'Device name cannot be empty'
            }), 400
        
        # Add device
        result = pairing_manager.add_device(device_id, device_name.strip(), secret)
        
        if result:
            logger.info(f"Pairing completed: {device_name} ({device_id})")
            return jsonify({
                'success': True,
                'message': 'Device paired successfully',
                'device_id': device_id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Device already paired or database error'
            }), 400
    
    except Exception as e:
        logger.error(f"API error completing pairing: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/qr/<device_id>')
def api_get_qr(device_id):
    """API: Get QR code image for device pairing."""
    try:
        # Get device data from query params (for new pairings)
        secret = request.args.get('secret')
        
        if not secret:
            return jsonify({
                'error': 'Missing secret parameter'
            }), 400
        
        # Create pairing data JSON
        pairing_data = {
            'device_id': device_id,
            'secret': secret,
            'server_url': request.host_url.rstrip('/')
        }
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(pairing_data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes buffer
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
    
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/stats')
def api_stats():
    """API: Get system statistics."""
    try:
        device_count = pairing_manager.get_device_count()
        devices = pairing_manager.list_devices()
        
        # Calculate stats
        recently_used = sum(1 for d in devices if d.get('last_used') and 
                          (time.time() - d['last_used']) < 86400)  # Last 24 hours
        
        return jsonify({
            'success': True,
            'stats': {
                'total_devices': device_count,
                'active_24h': recently_used,
                'server_uptime': time.time()  # Simplified
            }
        })
    
    except Exception as e:
        logger.error(f"API error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    return render_template('error.html', error='Internal server error'), 500


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting BlueZscript Web UI...")
    logger.info(f"Dashboard: http://{HOST}:{PORT}")
    logger.info(f"Paired devices: {pairing_manager.get_device_count()}")
    
    # Run Flask app
    app.run(host=HOST, port=PORT, debug=DEBUG)
