"""
Match API routes.
"""
from flask import Blueprint, request, jsonify, current_app
from backend.auth.middleware import require_auth, get_current_user, require_admin
from backend.utils.errors import NotFoundError
import logging

logger = logging.getLogger(__name__)

matches_bp = Blueprint('matches', __name__, url_prefix='/api/matches')


@matches_bp.route('', methods=['GET'])
@require_auth
def get_matches():
    """Get current user's matches."""
    try:
        pennkey = get_current_user()
        course = request.args.get('course')
        
        firebase_service = current_app.firebase_service
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        if course:
            match = firebase_service.get_user_match(pennkey, course)
            if match:
                return jsonify(match.to_dict()), 200
            else:
                return jsonify({'message': 'No match found for this course'}), 404
        else:
            # Get all matches for user (across all courses)
            # TODO: Implement this properly
            return jsonify({'message': 'Please specify a course parameter'}), 400
        
    except Exception as e:
        logger.error(f"Error getting matches: {e}")
        return jsonify({'error': str(e)}), 500


@matches_bp.route('/<match_id>', methods=['GET'])
@require_auth
def get_match(match_id: str):
    """Get a specific match."""
    try:
        pennkey = get_current_user()
        firebase_service = current_app.firebase_service
        
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        match = firebase_service.get_match(match_id)
        
        if not match:
            raise NotFoundError('Match not found')
        
        # Verify user is a member
        if not any(member.pennkey == pennkey for member in match.members):
            raise NotFoundError('Match not found')
        
        return jsonify(match.to_dict()), 200
        
    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except Exception as e:
        logger.error(f"Error getting match: {e}")
        return jsonify({'error': str(e)}), 500


@matches_bp.route('/trigger', methods=['POST'])
@require_admin
def trigger_matching():
    """Trigger matching for a course (admin only)."""
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'error': 'course_id is required'}), 400
        
        # Import here to avoid circular imports
        from backend.src.services.email_service import EmailService
        from backend.src.aggregation.scoring import CompatibilityScorer
        from backend.src.aggregation.clustering import GroupMatcher
        from backend.src.aggregation.matcher import MatchOrchestrator
        
        firebase_service = current_app.firebase_service
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        # Initialize services
        email_service = EmailService(
            api_key=current_app.config.get('SENDGRID_API_KEY'),
            from_email=current_app.config.get('FROM_EMAIL')
        )
        
        # Initialize matcher
        scorer = CompatibilityScorer()
        matcher = GroupMatcher(
            scorer=scorer,
            min_group_size=current_app.config.get('MIN_GROUP_SIZE', 3),
            max_group_size=current_app.config.get('MAX_GROUP_SIZE', 5)
        )
        
        orchestrator = MatchOrchestrator(firebase_service, email_service, matcher)
        result = orchestrator.run_matching(course_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error triggering matching: {e}")
        return jsonify({'error': str(e)}), 500

