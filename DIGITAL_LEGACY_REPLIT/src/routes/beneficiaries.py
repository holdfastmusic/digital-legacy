from flask import Blueprint, jsonify, request
from src.models.beneficiary import Beneficiary, db
from src.routes.auth import require_auth

beneficiaries_bp = Blueprint('beneficiaries', __name__)

@beneficiaries_bp.route('/beneficiaries', methods=['GET'])
@require_auth
def get_beneficiaries():
    try:
        beneficiaries = Beneficiary.query.filter_by(user_id=request.current_user.id).all()
        return jsonify([beneficiary.to_dict() for beneficiary in beneficiaries]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@beneficiaries_bp.route('/beneficiaries', methods=['POST'])
@require_auth
def create_beneficiary():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name') or not data.get('email'):
            return jsonify({'error': 'Name and email are required'}), 400
        
        beneficiary = Beneficiary(
            user_id=request.current_user.id,
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            relationship=data.get('relationship')
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        return jsonify(beneficiary.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@beneficiaries_bp.route('/beneficiaries/<int:beneficiary_id>', methods=['GET'])
@require_auth
def get_beneficiary(beneficiary_id):
    try:
        beneficiary = Beneficiary.query.filter_by(
            id=beneficiary_id, 
            user_id=request.current_user.id
        ).first_or_404()
        
        return jsonify(beneficiary.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@beneficiaries_bp.route('/beneficiaries/<int:beneficiary_id>', methods=['PUT'])
@require_auth
def update_beneficiary(beneficiary_id):
    try:
        beneficiary = Beneficiary.query.filter_by(
            id=beneficiary_id, 
            user_id=request.current_user.id
        ).first_or_404()
        
        data = request.json
        
        # Update fields
        beneficiary.name = data.get('name', beneficiary.name)
        beneficiary.email = data.get('email', beneficiary.email)
        beneficiary.phone = data.get('phone', beneficiary.phone)
        beneficiary.relationship = data.get('relationship', beneficiary.relationship)
        
        db.session.commit()
        
        return jsonify(beneficiary.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@beneficiaries_bp.route('/beneficiaries/<int:beneficiary_id>', methods=['DELETE'])
@require_auth
def delete_beneficiary(beneficiary_id):
    try:
        beneficiary = Beneficiary.query.filter_by(
            id=beneficiary_id, 
            user_id=request.current_user.id
        ).first_or_404()
        
        db.session.delete(beneficiary)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@beneficiaries_bp.route('/beneficiaries/relationships', methods=['GET'])
@require_auth
def get_relationship_types():
    """Get available relationship types"""
    relationships = [
        {'value': 'spouse', 'label': 'Coniuge'},
        {'value': 'child', 'label': 'Figlio/a'},
        {'value': 'parent', 'label': 'Genitore'},
        {'value': 'sibling', 'label': 'Fratello/Sorella'},
        {'value': 'friend', 'label': 'Amico/a'},
        {'value': 'lawyer', 'label': 'Avvocato'},
        {'value': 'executor', 'label': 'Esecutore testamentario'},
        {'value': 'other', 'label': 'Altro'}
    ]
    
    return jsonify(relationships), 200

