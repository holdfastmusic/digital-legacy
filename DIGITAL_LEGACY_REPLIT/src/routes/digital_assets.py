from flask import Blueprint, jsonify, request
from src.models.digital_asset import DigitalAsset, db
from src.routes.auth import require_auth
from cryptography.fernet import Fernet
import os

digital_assets_bp = Blueprint('digital_assets', __name__)

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"WARNING: No ENCRYPTION_KEY set. Generated ephemeral key. "
          f"Set ENCRYPTION_KEY={ENCRYPTION_KEY} in environment to persist.")
cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_credentials(credentials):
    """Encrypt sensitive credentials"""
    if not credentials:
        return None
    return cipher_suite.encrypt(credentials.encode()).decode()

def decrypt_credentials(encrypted_credentials):
    """Decrypt sensitive credentials"""
    if not encrypted_credentials:
        return None
    return cipher_suite.decrypt(encrypted_credentials.encode()).decode()

@digital_assets_bp.route('/digital-assets', methods=['GET'])
@require_auth
def get_digital_assets():
    try:
        assets = DigitalAsset.query.filter_by(user_id=request.current_user.id).all()
        return jsonify([asset.to_dict() for asset in assets]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@digital_assets_bp.route('/digital-assets', methods=['POST'])
@require_auth
def create_digital_asset():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name') or not data.get('asset_type'):
            return jsonify({'error': 'Name and asset_type are required'}), 400
        
        # Encrypt credentials if provided
        encrypted_credentials = None
        if data.get('credentials'):
            encrypted_credentials = encrypt_credentials(data['credentials'])
        
        asset = DigitalAsset(
            user_id=request.current_user.id,
            name=data['name'],
            asset_type=data['asset_type'],
            url=data.get('url'),
            username=data.get('username'),
            credentials_encrypted=encrypted_credentials,
            instructions=data.get('instructions')
        )
        
        db.session.add(asset)
        db.session.commit()
        
        return jsonify(asset.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@digital_assets_bp.route('/digital-assets/<int:asset_id>', methods=['GET'])
@require_auth
def get_digital_asset(asset_id):
    try:
        asset = DigitalAsset.query.filter_by(
            id=asset_id, 
            user_id=request.current_user.id
        ).first_or_404()
        
        asset_dict = asset.to_dict()
        
        # Decrypt credentials for owner
        if asset.credentials_encrypted:
            asset_dict['credentials'] = decrypt_credentials(asset.credentials_encrypted)
        
        return jsonify(asset_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@digital_assets_bp.route('/digital-assets/<int:asset_id>', methods=['PUT'])
@require_auth
def update_digital_asset(asset_id):
    try:
        asset = DigitalAsset.query.filter_by(
            id=asset_id, 
            user_id=request.current_user.id
        ).first_or_404()
        
        data = request.json
        
        # Update fields
        asset.name = data.get('name', asset.name)
        asset.asset_type = data.get('asset_type', asset.asset_type)
        asset.url = data.get('url', asset.url)
        asset.username = data.get('username', asset.username)
        asset.instructions = data.get('instructions', asset.instructions)
        
        # Update credentials if provided
        if 'credentials' in data:
            if data['credentials']:
                asset.credentials_encrypted = encrypt_credentials(data['credentials'])
            else:
                asset.credentials_encrypted = None
        
        db.session.commit()
        
        return jsonify(asset.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@digital_assets_bp.route('/digital-assets/<int:asset_id>', methods=['DELETE'])
@require_auth
def delete_digital_asset(asset_id):
    try:
        asset = DigitalAsset.query.filter_by(
            id=asset_id, 
            user_id=request.current_user.id
        ).first_or_404()
        
        db.session.delete(asset)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@digital_assets_bp.route('/digital-assets/types', methods=['GET'])
@require_auth
def get_asset_types():
    """Get available asset types"""
    asset_types = [
        {'value': 'social_media', 'label': 'Social Media'},
        {'value': 'email', 'label': 'Email Account'},
        {'value': 'cloud_storage', 'label': 'Cloud Storage'},
        {'value': 'financial', 'label': 'Financial Account'},
        {'value': 'cryptocurrency', 'label': 'Cryptocurrency'},
        {'value': 'domain', 'label': 'Domain/Website'},
        {'value': 'subscription', 'label': 'Subscription Service'},
        {'value': 'gaming', 'label': 'Gaming Account'},
        {'value': 'other', 'label': 'Other'}
    ]
    
    return jsonify(asset_types), 200

