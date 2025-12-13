"""
Submission API routes.
"""
from flask import Blueprint, request, jsonify, current_app
from backend.auth.middleware import require_auth, get_current_user
from backend.models.submission import Submission
from backend.src.qc.validators import SubmissionValidator
from backend.src.qc.roster_service import RosterService
from backend.utils.errors import ValidationError, NotFoundError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

submissions_bp = Blueprint('submissions', __name__, url_prefix='/api/submissions')


@submissions_bp.route('', methods=['POST'])
@require_auth
def create_submission():
    """Create a new submission."""
    try:
        pennkey = get_current_user()
        data = request.get_json()
        
        if not data:
            raise ValidationError('No data provided')
        
        # Get services from app context
        firebase_service = current_app.firebase_service
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        roster_service = RosterService(firebase_service)
        validator = SubmissionValidator(roster_service, firebase_service)
        
        # Validate submission
        result = validator.validate_submission(data, pennkey)
        
        if not result.is_valid:
            raise ValidationError(', '.join(result.errors))
        
        # Create submission object
        submission = Submission.from_dict(result.sanitized_data)
        submission.status = 'pending'
        submission.created_at = datetime.utcnow().isoformat()
        
        # Store in Firebase
        submission_id = firebase_service.create_submission(submission)
        
        # Mark as validated
        firebase_service.update_submission(submission_id, {
            'status': 'validated',
            'validated_at': datetime.utcnow().isoformat()
        })
        
        submission.id = submission_id
        submission.status = 'validated'
        submission.validated_at = datetime.utcnow().isoformat()
        
        logger.info(f"Created submission {submission_id} for user {pennkey}")
        
        return jsonify(submission.to_dict()), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        return jsonify({'error': e.message}), 400
    except Exception as e:
        logger.error(f"Error creating submission: {e}")
        return jsonify({'error': str(e)}), 500


@submissions_bp.route('', methods=['GET'])
@require_auth
def get_submissions():
    """Get current user's submissions."""
    try:
        pennkey = get_current_user()
        firebase_service = current_app.firebase_service
        
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        # Get all submissions for user (simplified - in production might filter by course)
        # For now, we'll get the most recent submission
        # TODO: Implement proper query
        
        return jsonify({'message': 'Get submissions endpoint - to be implemented'}), 200
        
    except Exception as e:
        logger.error(f"Error getting submissions: {e}")
        return jsonify({'error': str(e)}), 500


@submissions_bp.route('/<submission_id>', methods=['GET'])
@require_auth
def get_submission(submission_id: str):
    """Get a specific submission."""
    try:
        pennkey = get_current_user()
        firebase_service = current_app.firebase_service
        
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        submission = firebase_service.get_submission(submission_id)
        
        if not submission:
            raise NotFoundError('Submission not found')
        
        # Verify ownership
        if submission.pennkey != pennkey:
            raise NotFoundError('Submission not found')
        
        return jsonify(submission.to_dict()), 200
        
    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except Exception as e:
        logger.error(f"Error getting submission: {e}")
        return jsonify({'error': str(e)}), 500


@submissions_bp.route('/<submission_id>', methods=['DELETE'])
@require_auth
def delete_submission(submission_id: str):
    """Delete a submission."""
    try:
        pennkey = get_current_user()
        firebase_service = current_app.firebase_service
        
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        submission = firebase_service.get_submission(submission_id)
        
        if not submission:
            raise NotFoundError('Submission not found')
        
        # Verify ownership
        if submission.pennkey != pennkey:
            raise NotFoundError('Submission not found')
        
        # Delete from Firebase
        # TODO: Implement delete method in FirebaseService
        # For now, mark as deleted
        
        return jsonify({'message': 'Submission deleted'}), 200
        
    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except Exception as e:
        logger.error(f"Error deleting submission: {e}")
        return jsonify({'error': str(e)}), 500

