"""
Quality Control module for validating submissions.
"""
import re
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def validate_submission(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a submission and return validation result.
    
    Args:
        data: Submission data dictionary
        
    Returns:
        {
            "valid": bool,
            "errors": List[str]
        }
    """
    errors: List[str] = []
    
    # Check required fields
    required_fields = ['name', 'email', 'course', 'availability', 'study_preference']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate email format
    if 'email' in data and data['email']:
        email = data['email'].strip().lower()  # Normalize to lowercase
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append("Invalid email format")
    
    # Validate availability (must have at least one time block)
    if 'availability' in data:
        availability = data['availability']
        if not isinstance(availability, list):
            errors.append("Availability must be a list")
        elif len(availability) == 0:
            errors.append("At least one availability time block is required")
        else:
            # Validate availability format (should be list of strings)
            for block in availability:
                if not isinstance(block, str) or not block.strip():
                    errors.append("Invalid availability block format")
                    break
    
    # Validate study preference
    valid_preferences = ['PSets', 'Concept Review', 'Discussion', 'Exam Prep', 'Mixed']
    if 'study_preference' in data and data['study_preference']:
        if data['study_preference'] not in valid_preferences:
            errors.append(f"Invalid study preference. Must be one of: {', '.join(valid_preferences)}")
    
    # Validate location preference
    valid_locations = ['In-person', 'Virtual', 'Either']
    if 'location_preference' in data and data['location_preference']:
        if data['location_preference'] not in valid_locations:
            errors.append(f"Invalid location preference. Must be one of: {', '.join(valid_locations)}")
    
    # Validate course (should not be empty)
    if 'course' in data and data['course']:
        course = data['course'].strip()
        if len(course) < 2:
            errors.append("Course code must be at least 2 characters")
    
    # Validate name (should not be empty)
    if 'name' in data and data['name']:
        name = data['name'].strip()
        if len(name) < 2:
            errors.append("Name must be at least 2 characters")
    
    # Check commitment confirmation
    if 'commitment_confirmed' in data:
        if not data['commitment_confirmed']:
            errors.append("Commitment confirmation is required")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def run_attention_checks(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run attention checks on submission data.
    
    Args:
        data: Submission data dictionary
        
    Returns:
        {
            "passed": bool,
            "checks": List[Dict[str, Any]]
        }
    """
    checks = []
    
    # Check 1: Suspiciously short name
    if 'name' in data and data['name']:
        if len(data['name'].strip()) < 3:
            checks.append({
                "type": "name_length",
                "passed": False,
                "message": "Name appears too short"
            })
        else:
            checks.append({
                "type": "name_length",
                "passed": True,
                "message": "Name length acceptable"
            })
    
    # Check 2: Email domain validation
    if 'email' in data and data['email']:
        email = data['email'].strip()
        suspicious_domains = ['test.com', 'example.com', 'fake.com']
        domain = email.split('@')[-1] if '@' in email else ''
        if domain.lower() in suspicious_domains:
            checks.append({
                "type": "email_domain",
                "passed": False,
                "message": f"Suspicious email domain: {domain}"
            })
        else:
            checks.append({
                "type": "email_domain",
                "passed": True,
                "message": "Email domain acceptable"
            })
    
    # Check 3: Availability completeness
    if 'availability' in data:
        availability = data['availability']
        if isinstance(availability, list) and len(availability) < 2:
            checks.append({
                "type": "availability_completeness",
                "passed": False,
                "message": "Very limited availability may indicate low commitment"
            })
        else:
            checks.append({
                "type": "availability_completeness",
                "passed": True,
                "message": "Adequate availability provided"
            })
    
    # Check 4: Commitment confirmation
    if 'commitment_confirmed' in data:
        if not data['commitment_confirmed']:
            checks.append({
                "type": "commitment",
                "passed": False,
                "message": "Commitment not confirmed"
            })
        else:
            checks.append({
                "type": "commitment",
                "passed": True,
                "message": "Commitment confirmed"
            })
    
    # Overall result: passed if all checks passed
    passed = all(check.get("passed", False) for check in checks)
    
    return {
        "passed": passed,
        "checks": checks
    }


def sanitize_submission(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize submission data by trimming strings and normalizing format.
    
    Args:
        data: Raw submission data
        
    Returns:
        Sanitized data dictionary
    """
    sanitized = {}
    
    # Sanitize string fields
    string_fields = ['name', 'email', 'course', 'study_preference']
    for field in string_fields:
        if field in data:
            value = data[field]
            if isinstance(value, str):
                sanitized[field] = value.strip()
            else:
                sanitized[field] = value
    
    # Sanitize availability (ensure it's a list of strings)
    if 'availability' in data:
        availability = data['availability']
        if isinstance(availability, list):
            sanitized['availability'] = [
                str(block).strip() for block in availability if block
            ]
        else:
            sanitized['availability'] = []
    
    # Preserve boolean fields
    if 'commitment_confirmed' in data:
        sanitized['commitment_confirmed'] = bool(data['commitment_confirmed'])
    
    # Sanitize location preference
    if 'location_preference' in data:
        value = data['location_preference']
        if isinstance(value, str):
            sanitized['location_preference'] = value.strip()
        else:
            sanitized['location_preference'] = value
    
    # Preserve any other fields
    for key, value in data.items():
        if key not in sanitized:
            sanitized[key] = value
    
    return sanitized

