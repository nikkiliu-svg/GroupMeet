"""
Aggregation module for processing feedback and computing statistics.
"""
import statistics
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def aggregate_feedback(feedback_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate feedback ratings and compute statistics.
    
    Args:
        feedback_list: List of feedback dictionaries, each containing:
            - rating: int (1-5 stars)
            - optional: comments, match_id, student_id, etc.
    
    Returns:
        {
            "mean": float,
            "median": float,
            "n": int,
            "confidence_score": float,
            "distribution": Dict[int, int]  # count per rating
        }
    """
    if not feedback_list:
        return {
            "mean": 0.0,
            "median": 0.0,
            "n": 0,
            "confidence_score": 0.0,
            "distribution": {}
        }
    
    # Extract ratings
    ratings = []
    for feedback in feedback_list:
        rating = feedback.get('rating')
        if rating is not None:
            try:
                rating_int = int(rating)
                if 1 <= rating_int <= 5:
                    ratings.append(rating_int)
            except (ValueError, TypeError):
                logger.warning(f"Invalid rating in feedback: {rating}")
                continue
    
    if not ratings:
        return {
            "mean": 0.0,
            "median": 0.0,
            "n": 0,
            "confidence_score": 0.0,
            "distribution": {}
        }
    
    # Compute statistics
    mean = statistics.mean(ratings)
    median = statistics.median(ratings)
    n = len(ratings)
    
    # Compute distribution
    distribution = {}
    for i in range(1, 6):
        distribution[i] = ratings.count(i)
    
    # Compute confidence score
    # Based on sample size and variance
    # Higher n and lower variance = higher confidence
    if n > 1:
        variance = statistics.variance(ratings)
        # Normalize variance (max variance for 1-5 scale is ~4)
        normalized_variance = variance / 4.0
        # Confidence increases with n and decreases with variance
        # Using a simple formula: sqrt(n) * (1 - normalized_variance)
        confidence_score = min(1.0, (n ** 0.5) * (1 - normalized_variance) / 10.0)
    else:
        confidence_score = 0.1  # Low confidence for single data point
    
    return {
        "mean": round(mean, 2),
        "median": round(median, 2),
        "n": n,
        "confidence_score": round(confidence_score, 3),
        "distribution": distribution
    }


def compute_match_quality_score(match_data: Dict[str, Any]) -> float:
    """
    Compute a quality score for a match based on various factors.
    
    Args:
        match_data: Match dictionary containing:
            - availability_overlap: float
            - preference_alignment: float
            - group_size: int
            - feedback_ratings: List[int] (optional)
    
    Returns:
        Quality score between 0 and 1
    """
    score = 0.0
    
    # Factor 1: Availability overlap (40% weight)
    availability_overlap = match_data.get('availability_overlap', 0.0)
    score += 0.4 * availability_overlap
    
    # Factor 2: Preference alignment (30% weight)
    preference_alignment = match_data.get('preference_alignment', 0.0)
    score += 0.3 * preference_alignment
    
    # Factor 3: Group size appropriateness (10% weight)
    group_size = match_data.get('group_size', 0)
    if 3 <= group_size <= 5:
        size_score = 1.0
    elif group_size == 2:
        size_score = 0.5
    else:
        size_score = 0.0
    score += 0.1 * size_score
    
    # Factor 4: Feedback ratings (20% weight, if available)
    feedback_ratings = match_data.get('feedback_ratings', [])
    if feedback_ratings:
        avg_rating = statistics.mean(feedback_ratings)
        # Normalize 1-5 scale to 0-1
        normalized_rating = (avg_rating - 1) / 4.0
        score += 0.2 * normalized_rating
    else:
        # No feedback yet, don't penalize
        score += 0.2 * 0.5  # Neutral score
    
    return min(1.0, max(0.0, score))


def aggregate_match_statistics(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate statistics across multiple matches.
    
    Args:
        matches: List of match dictionaries
    
    Returns:
        Aggregated statistics
    """
    if not matches:
        return {
            "total_matches": 0,
            "avg_group_size": 0.0,
            "avg_availability_overlap": 0.0,
            "avg_preference_alignment": 0.0,
            "avg_quality_score": 0.0
        }
    
    total_matches = len(matches)
    group_sizes = []
    availability_overlaps = []
    preference_alignments = []
    quality_scores = []
    
    for match in matches:
        group_size = match.get('group_size', 0)
        if group_size > 0:
            group_sizes.append(group_size)
        
        availability_overlap = match.get('availability_overlap', 0.0)
        if availability_overlap > 0:
            availability_overlaps.append(availability_overlap)
        
        preference_alignment = match.get('preference_alignment', 0.0)
        if preference_alignment > 0:
            preference_alignments.append(preference_alignment)
        
        quality_score = compute_match_quality_score(match)
        quality_scores.append(quality_score)
    
    return {
        "total_matches": total_matches,
        "avg_group_size": round(statistics.mean(group_sizes) if group_sizes else 0.0, 2),
        "avg_availability_overlap": round(statistics.mean(availability_overlaps) if availability_overlaps else 0.0, 3),
        "avg_preference_alignment": round(statistics.mean(preference_alignments) if preference_alignments else 0.0, 3),
        "avg_quality_score": round(statistics.mean(quality_scores) if quality_scores else 0.0, 3)
    }

