from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import jwt

from src.routes.auth import require_auth
from src.models.user import db
from src.models.digital_asset import DigitalAsset
from src.models.beneficiary import Beneficiary
from src.models.asset_assignment import AssetAssignment
from src.models.succession_plan import SuccessionPlan
from src.models.push_subscription import PushSubscription

mobile_bp = Blueprint('mobile', __name__)

JWT_SECRET = 'digital_legacy_secret_key_2024'


@mobile_bp.route('/mobile/dashboard', methods=['GET'])
@require_auth
def mobile_dashboard():
    """Single-request summary for mobile home screen."""
    try:
        user = request.current_user

        assets_count = DigitalAsset.query.filter_by(user_id=user.id).count()
        beneficiaries_count = Beneficiary.query.filter_by(user_id=user.id).count()
        assignments_count = (
            AssetAssignment.query
            .join(DigitalAsset, AssetAssignment.asset_id == DigitalAsset.id)
            .filter(DigitalAsset.user_id == user.id)
            .count()
        )

        plan = SuccessionPlan.query.filter_by(user_id=user.id).first()
        plan_status = None
        if plan:
            if plan.last_activity:
                days_since = (datetime.utcnow() - plan.last_activity).days
                days_remaining = max(0, plan.trigger_days - days_since)
            else:
                days_since = 0
                days_remaining = plan.trigger_days

            plan_status = {
                'status': plan.status,
                'trigger_days': plan.trigger_days,
                'days_since_activity': days_since,
                'days_remaining': days_remaining,
                'is_triggered': days_remaining == 0 and plan.status == 'active',
            }

        return jsonify({
            'user': {
                'id': user.id,
                'name': user.name or user.username,
                'email': user.email,
            },
            'summary': {
                'assets': assets_count,
                'beneficiaries': beneficiaries_count,
                'assignments': assignments_count,
            },
            'succession_plan': plan_status,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/mobile/heartbeat', methods=['POST'])
@require_auth
def heartbeat():
    """Check-in from mobile: updates last_activity and returns quick status."""
    try:
        plan = SuccessionPlan.query.filter_by(user_id=request.current_user.id).first()

        result = {'activity_updated': False, 'succession_plan': None}

        if plan and plan.status == 'active':
            plan.last_activity = datetime.utcnow()
            db.session.commit()
            result['activity_updated'] = True
            result['succession_plan'] = {
                'status': plan.status,
                'days_remaining': plan.trigger_days,
            }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/mobile/auth/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """Issue a 30-day token for mobile apps to avoid frequent re-login."""
    try:
        token = jwt.encode(
            {
                'user_id': request.current_user.id,
                'exp': datetime.utcnow() + timedelta(days=30),
                'mobile': True,
            },
            JWT_SECRET,
            algorithm='HS256',
        )
        return jsonify({
            'token': token,
            'expires_in': 30 * 24 * 3600,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/mobile/push/subscribe', methods=['POST'])
@require_auth
def push_subscribe():
    """Register a Web Push subscription for this device."""
    try:
        data = request.json or {}

        endpoint = data.get('endpoint')
        keys = data.get('keys') or {}
        p256dh = keys.get('p256dh')
        auth_key = keys.get('auth')

        if not endpoint or not p256dh or not auth_key:
            return jsonify({'error': 'endpoint, keys.p256dh and keys.auth are required'}), 400

        existing = PushSubscription.query.filter_by(endpoint=endpoint).first()
        if existing:
            existing.user_id = request.current_user.id
            existing.p256dh = p256dh
            existing.auth = auth_key
            existing.user_agent = request.headers.get('User-Agent', '')[:500]
        else:
            subscription = PushSubscription(
                user_id=request.current_user.id,
                endpoint=endpoint,
                p256dh=p256dh,
                auth=auth_key,
                user_agent=request.headers.get('User-Agent', '')[:500],
            )
            db.session.add(subscription)

        db.session.commit()
        return jsonify({'message': 'Push subscription registered'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/mobile/push/subscribe', methods=['DELETE'])
@require_auth
def push_unsubscribe():
    """Remove a Web Push subscription for this device."""
    try:
        data = request.json or {}
        endpoint = data.get('endpoint')

        if not endpoint:
            return jsonify({'error': 'endpoint is required'}), 400

        subscription = PushSubscription.query.filter_by(
            endpoint=endpoint,
            user_id=request.current_user.id,
        ).first()

        if subscription:
            db.session.delete(subscription)
            db.session.commit()

        return jsonify({'message': 'Push subscription removed'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/mobile/push/subscriptions', methods=['GET'])
@require_auth
def list_push_subscriptions():
    """List all active push subscriptions for the current user."""
    try:
        subscriptions = PushSubscription.query.filter_by(
            user_id=request.current_user.id
        ).all()
        return jsonify([s.to_dict() for s in subscriptions]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
