from flask import Blueprint, jsonify, request
from src.models.asset_assignment import AssetAssignment, db
from src.models.digital_asset import DigitalAsset
from src.models.beneficiary import Beneficiary
from src.routes.auth import require_auth

assignments_bp = Blueprint('assignments', __name__)

@assignments_bp.route('/assignments', methods=['GET'])
@require_auth
def get_assignments():
    try:
        # Get assignments for user's assets
        assignments = db.session.query(AssetAssignment)\
            .join(DigitalAsset)\
            .filter(DigitalAsset.user_id == request.current_user.id)\
            .all()
        
        result = []
        for assignment in assignments:
            assignment_dict = assignment.to_dict()
            assignment_dict['asset'] = assignment.asset.to_dict()
            assignment_dict['beneficiary'] = assignment.beneficiary.to_dict()
            result.append(assignment_dict)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments', methods=['POST'])
@require_auth
def create_assignment():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('asset_id') or not data.get('beneficiary_id'):
            return jsonify({'error': 'Asset ID and Beneficiary ID are required'}), 400
        
        # Verify asset belongs to current user
        asset = DigitalAsset.query.filter_by(
            id=data['asset_id'], 
            user_id=request.current_user.id
        ).first()
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # Verify beneficiary belongs to current user
        beneficiary = Beneficiary.query.filter_by(
            id=data['beneficiary_id'], 
            user_id=request.current_user.id
        ).first()
        if not beneficiary:
            return jsonify({'error': 'Beneficiary not found'}), 404
        
        # Check if assignment already exists
        existing = AssetAssignment.query.filter_by(
            asset_id=data['asset_id'],
            beneficiary_id=data['beneficiary_id']
        ).first()
        if existing:
            return jsonify({'error': 'Assignment already exists'}), 400
        
        assignment = AssetAssignment(
            asset_id=data['asset_id'],
            beneficiary_id=data['beneficiary_id'],
            instructions=data.get('instructions')
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        # Return assignment with related data
        assignment_dict = assignment.to_dict()
        assignment_dict['asset'] = assignment.asset.to_dict()
        assignment_dict['beneficiary'] = assignment.beneficiary.to_dict()
        
        return jsonify(assignment_dict), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@require_auth
def get_assignment(assignment_id):
    try:
        assignment = db.session.query(AssetAssignment)\
            .join(DigitalAsset)\
            .filter(AssetAssignment.id == assignment_id)\
            .filter(DigitalAsset.user_id == request.current_user.id)\
            .first_or_404()
        
        assignment_dict = assignment.to_dict()
        assignment_dict['asset'] = assignment.asset.to_dict()
        assignment_dict['beneficiary'] = assignment.beneficiary.to_dict()
        
        return jsonify(assignment_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<int:assignment_id>', methods=['PUT'])
@require_auth
def update_assignment(assignment_id):
    try:
        assignment = db.session.query(AssetAssignment)\
            .join(DigitalAsset)\
            .filter(AssetAssignment.id == assignment_id)\
            .filter(DigitalAsset.user_id == request.current_user.id)\
            .first_or_404()
        
        data = request.json
        
        # Update instructions
        assignment.instructions = data.get('instructions', assignment.instructions)
        
        db.session.commit()
        
        # Return assignment with related data
        assignment_dict = assignment.to_dict()
        assignment_dict['asset'] = assignment.asset.to_dict()
        assignment_dict['beneficiary'] = assignment.beneficiary.to_dict()
        
        return jsonify(assignment_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@require_auth
def delete_assignment(assignment_id):
    try:
        assignment = db.session.query(AssetAssignment)\
            .join(DigitalAsset)\
            .filter(AssetAssignment.id == assignment_id)\
            .filter(DigitalAsset.user_id == request.current_user.id)\
            .first_or_404()
        
        db.session.delete(assignment)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/assets/<int:asset_id>/assignments', methods=['GET'])
@require_auth
def get_asset_assignments(asset_id):
    try:
        # Verify asset belongs to current user
        asset = DigitalAsset.query.filter_by(
            id=asset_id, 
            user_id=request.current_user.id
        ).first_or_404()
        
        assignments = AssetAssignment.query.filter_by(asset_id=asset_id).all()
        
        result = []
        for assignment in assignments:
            assignment_dict = assignment.to_dict()
            assignment_dict['beneficiary'] = assignment.beneficiary.to_dict()
            result.append(assignment_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/beneficiaries/<int:beneficiary_id>/assignments', methods=['GET'])
@require_auth
def get_beneficiary_assignments(beneficiary_id):
    try:
        # Verify beneficiary belongs to current user
        beneficiary = Beneficiary.query.filter_by(
            id=beneficiary_id, 
            user_id=request.current_user.id
        ).first_or_404()
        
        assignments = AssetAssignment.query.filter_by(beneficiary_id=beneficiary_id).all()
        
        result = []
        for assignment in assignments:
            assignment_dict = assignment.to_dict()
            assignment_dict['asset'] = assignment.asset.to_dict()
            result.append(assignment_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

