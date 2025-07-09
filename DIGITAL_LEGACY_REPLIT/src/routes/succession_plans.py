from flask import Blueprint, jsonify, request
from datetime import datetime
from src.models.succession_plan import SuccessionPlan, db
from src.routes.auth import require_auth

succession_plans_bp = Blueprint('succession_plans', __name__)

@succession_plans_bp.route('/succession-plan', methods=['GET'])
@require_auth
def get_succession_plan():
    try:
        plan = SuccessionPlan.query.filter_by(user_id=request.current_user.id).first()
        
        if not plan:
            return jsonify({'message': 'No succession plan found'}), 404
        
        return jsonify(plan.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@succession_plans_bp.route('/succession-plan', methods=['POST'])
@require_auth
def create_succession_plan():
    try:
        data = request.json
        
        # Check if plan already exists
        existing_plan = SuccessionPlan.query.filter_by(user_id=request.current_user.id).first()
        if existing_plan:
            return jsonify({'error': 'Succession plan already exists. Use PUT to update.'}), 400
        
        # Validate trigger_days
        trigger_days = data.get('trigger_days', 90)
        if trigger_days < 1 or trigger_days > 365:
            return jsonify({'error': 'Trigger days must be between 1 and 365'}), 400
        
        plan = SuccessionPlan(
            user_id=request.current_user.id,
            trigger_days=trigger_days,
            instructions=data.get('instructions'),
            status='active'
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify(plan.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@succession_plans_bp.route('/succession-plan', methods=['PUT'])
@require_auth
def update_succession_plan():
    try:
        plan = SuccessionPlan.query.filter_by(user_id=request.current_user.id).first()
        
        if not plan:
            return jsonify({'error': 'No succession plan found'}), 404
        
        data = request.json
        
        # Update fields
        if 'trigger_days' in data:
            trigger_days = data['trigger_days']
            if trigger_days < 1 or trigger_days > 365:
                return jsonify({'error': 'Trigger days must be between 1 and 365'}), 400
            plan.trigger_days = trigger_days
        
        if 'instructions' in data:
            plan.instructions = data['instructions']
        
        if 'status' in data and data['status'] in ['active', 'paused', 'triggered', 'completed']:
            plan.status = data['status']
        
        # Update last activity when user interacts
        plan.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(plan.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@succession_plans_bp.route('/succession-plan', methods=['DELETE'])
@require_auth
def delete_succession_plan():
    try:
        plan = SuccessionPlan.query.filter_by(user_id=request.current_user.id).first()
        
        if not plan:
            return jsonify({'error': 'No succession plan found'}), 404
        
        db.session.delete(plan)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@succession_plans_bp.route('/succession-plan/activity', methods=['POST'])
@require_auth
def update_activity():
    """Update last activity timestamp"""
    try:
        plan = SuccessionPlan.query.filter_by(user_id=request.current_user.id).first()
        
        if plan:
            plan.last_activity = datetime.utcnow()
            db.session.commit()
            return jsonify({'message': 'Activity updated'}), 200
        else:
            return jsonify({'message': 'No succession plan found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@succession_plans_bp.route('/succession-plan/status', methods=['GET'])
@require_auth
def get_plan_status():
    """Get succession plan status with days remaining"""
    try:
        plan = SuccessionPlan.query.filter_by(user_id=request.current_user.id).first()
        
        if not plan:
            return jsonify({'message': 'No succession plan found'}), 404
        
        # Calculate days since last activity
        if plan.last_activity:
            days_since_activity = (datetime.utcnow() - plan.last_activity).days
            days_remaining = max(0, plan.trigger_days - days_since_activity)
        else:
            days_since_activity = 0
            days_remaining = plan.trigger_days
        
        status_info = {
            'plan': plan.to_dict(),
            'days_since_activity': days_since_activity,
            'days_remaining': days_remaining,
            'is_triggered': days_remaining == 0 and plan.status == 'active'
        }
        
        return jsonify(status_info), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

