"""
Admin API routes.
"""
from flask import Blueprint, request, jsonify, current_app
from backend.auth.middleware import require_admin
from backend.src.qc.roster_service import RosterService
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/stats', methods=['GET'])
@require_admin
def get_stats():
    """Get platform statistics (admin only)."""
    try:
        firebase_service = current_app.firebase_service
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        # TODO: Calculate statistics
        stats = {
            'total_submissions': 0,
            'total_matches': 0,
            'total_feedback': 0,
            'courses': []
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/submissions', methods=['GET'])
@require_admin
def get_all_submissions():
    """Get all submissions (admin only)."""
    try:
        course = request.args.get('course')
        firebase_service = current_app.firebase_service
        
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        # TODO: Implement get all submissions
        return jsonify({'message': 'Get all submissions - to be implemented'}), 200
        
    except Exception as e:
        logger.error(f"Error getting submissions: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/matches', methods=['GET'])
@require_admin
def get_all_matches():
    """Get all matches (admin only)."""
    try:
        course = request.args.get('course')
        firebase_service = current_app.firebase_service
        
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        matches = firebase_service.get_all_matches(course)
        return jsonify([match.to_dict() for match in matches]), 200
        
    except Exception as e:
        logger.error(f"Error getting matches: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/roster/<course_id>', methods=['POST'])
@require_admin
def upload_roster(course_id: str):
    """Upload/update class roster (admin only)."""
    try:
        data = request.get_json()
        pennkeys = data.get('pennkeys', [])
        
        if not pennkeys:
            return jsonify({'error': 'pennkeys list is required'}), 400
        
        firebase_service = current_app.firebase_service
        if not firebase_service:
            raise Exception('Firebase service not initialized')
        
        roster_service = RosterService(firebase_service)
        success = roster_service.save_roster(course_id, pennkeys)
        
        if success:
            return jsonify({
                'message': f'Roster uploaded for {course_id}',
                'count': len(pennkeys)
            }), 200
        else:
            return jsonify({'error': 'Failed to upload roster'}), 500
        
    except Exception as e:
        logger.error(f"Error uploading roster: {e}")
        return jsonify({'error': str(e)}), 500

