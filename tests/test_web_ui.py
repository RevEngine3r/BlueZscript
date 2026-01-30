#!/usr/bin/env python3
"""
Unit tests for web_ui.py
Tests Flask routes, API endpoints, and QR generation
"""

import unittest
import os
import sys
import tempfile
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import raspberry_pi.web_ui as web_ui
from raspberry_pi.crypto_utils import CryptoUtils


class TestWebUI(unittest.TestCase):
    """Test suite for Flask Web UI"""
    
    def setUp(self):
        """Set up test client and temporary database"""
        # Use temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Override pairing manager
        from raspberry_pi.pairing_manager import PairingManager
        web_ui.pairing_manager = PairingManager(self.db_path)
        
        # Set up test client
        web_ui.app.config['TESTING'] = True
        self.client = web_ui.app.test_client()
    
    def tearDown(self):
        """Clean up after tests"""
        web_ui.pairing_manager.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_index_route(self):
        """Test dashboard index route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_pair_new_route(self):
        """Test pair new device route"""
        response = self.client.get('/pair/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pair New Device', response.data)
        self.assertIn(b'qr-code', response.data)
    
    def test_help_route(self):
        """Test help page route"""
        response = self.client.get('/help')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Help', response.data)
    
    def test_api_list_devices_empty(self):
        """Test API list devices when empty"""
        response = self.client.get('/api/devices')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['devices']), 0)
        self.assertEqual(data['count'], 0)
    
    def test_api_complete_pairing(self):
        """Test API complete pairing endpoint"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        response = self.client.post('/api/devices/complete',
            json={
                'device_id': device_id,
                'device_name': 'Test Phone',
                'secret': secret
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('device_id', data)
    
    def test_api_complete_pairing_missing_fields(self):
        """Test API complete pairing with missing fields"""
        response = self.client.post('/api/devices/complete',
            json={'device_id': 'test123'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_api_revoke_device(self):
        """Test API revoke device endpoint"""
        # First add a device
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        web_ui.pairing_manager.add_device(device_id, 'Test Phone', secret)
        
        # Then revoke it
        response = self.client.post(f'/api/devices/{device_id}/revoke')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_api_revoke_nonexistent_device(self):
        """Test API revoke nonexistent device"""
        response = self.client.post('/api/devices/nonexistent/revoke')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_api_get_device(self):
        """Test API get device endpoint"""
        # Add a device
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        device_name = 'Test Phone'
        web_ui.pairing_manager.add_device(device_id, device_name, secret)
        
        # Get device
        response = self.client.get(f'/api/devices/{device_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['device']['device_name'], device_name)
        # Secret should not be in response
        self.assertNotIn('secret_key', data['device'])
    
    def test_api_stats(self):
        """Test API stats endpoint"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('stats', data)
        self.assertIn('total_devices', data['stats'])
    
    def test_api_qr_code(self):
        """Test QR code generation endpoint"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        response = self.client.get(f'/api/qr/{device_id}?secret={secret}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'image/png')
    
    def test_404_error(self):
        """Test 404 error handling"""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_security_headers(self):
        """Test security headers are present"""
        response = self.client.get('/')
        
        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertIn('X-Frame-Options', response.headers)
        self.assertIn('X-XSS-Protection', response.headers)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
