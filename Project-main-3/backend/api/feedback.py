"""
Feedback API routes.
"""
from flask import Blueprint, request, jsonify, current_app
from backend.auth.middleware import require_auth, get_current_user
from backend.utils.errors import ValidationError, NotFoundError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')


@feedback_bp.route('', methods=['POST'])
@require_auth
def create_feedback():
    """Submit feedback for a match."""
    try:
        pennkey = get_current_user()
        data = request.get_json()
        
        if not data:
            raise ValidationError('No data provided')
        
        match_id = data.get('match_id')
        rating = data.get('rating')
        comments = data.get('comments', '')
        met_with_group = data.get('met_with_group', False)
        would_meet_again = data.get('would_meet_again', False)
        
        if not match_id:
            raise ValidationError('match_id is required')
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValidationError('rating must be an integer between 1 and 5')
        
        firebase_service = current_app.firebase_service
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        # Verify match exists and user is a member
        match = firebase_service.get_match(match_id)
        if not match:
            raise NotFoundError('Match not found')
        
        if not any(member.pennkey == pennkey for member in match.members):
            raise NotFoundError('You are not a member of this match')
        
        # Create feedback entry
        feedback_data = {
            'match_id': match_id,
            'pennkey': pennkey,
            'rating': rating,
            'comments': comments,
            'met_with_group': met_with_group,
            'would_meet_again': would_meet_again,
            'created_at': datetime.utcnow().isoformat()
        }
        
        feedback_id = firebase_service.create_feedback(feedback_data)
        feedback_data['id'] = feedback_id
        
        logger.info(f"Created feedback {feedback_id} for match {match_id} by user {pennkey}")
        
        return jsonify(feedback_data), 201
        
    except ValidationError as e:
        return jsonify({'error': e.message}), 400
    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except Exception as e:
        logger.error(f"Error creating feedback: {e}")
        return jsonify({'error': str(e)}), 500


@feedback_bp.route('', methods=['GET'])
@require_auth
def get_feedback():
    """Get user's feedback."""
    try:
        pennkey = get_current_user()
        match_id = request.args.get('match_id')
        
        firebase_service = current_app.firebase_service
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        if match_id:
            feedback_list = firebase_service.get_feedback(match_id)
            # Filter to user's feedback only
            user_feedback = [f for f in feedback_list if f.get('pennkey') == pennkey]
            return jsonify(user_feedback), 200
        else:
            # TODO: Get all feedback for user across all matches
            return jsonify({'message': 'Please specify match_id parameter'}), 400
        
    except Exception as e:
        logger.error(f"Error getting feedback: {e}")
        return jsonify({'error': str(e)}), 500

