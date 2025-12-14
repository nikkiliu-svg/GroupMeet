"""
Matching algorithm for grouping students based on course, availability, and preferences.
"""
import uuid
from typing import Dict, List, Any, Tuple, Set
import logging

logger = logging.getLogger(__name__)


def compute_availability_overlap(avail1: List[str], avail2: List[str]) -> float:
    """
    Compute Jaccard similarity (overlap) between two availability lists.
    
    Args:
        avail1: List of availability time blocks for student 1
        avail2: List of availability time blocks for student 2
    
    Returns:
        Overlap score between 0 and 1
    """
    if not avail1 or not avail2:
        return 0.0
    
    set1 = set(avail1)
    set2 = set(avail2)
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        return 0.0
    
    return intersection / union


def compute_preference_alignment(pref1: str, pref2: str) -> float:
    """
    Compute alignment score between two study preferences.
    
    Args:
        pref1: Study preference for student 1
        pref2: Study preference for student 2
    
    Returns:
        Alignment score (1.0 if same, 0.0 if different)
    """
    if not pref1 or not pref2:
        return 0.0
    
    return 1.0 if pref1.strip() == pref2.strip() else 0.0


def compute_location_alignment(loc1: str, loc2: str) -> float:
    """
    Compute alignment score between two location preferences.
    
    Args:
        loc1: Location preference for student 1 ("In-person", "Virtual", "Either")
        loc2: Location preference for student 2
    
    Returns:
        Alignment score:
        - 1.0 if both are same and not "Either"
        - 0.8 if one is "Either" and other is specific
        - 0.5 if both are "Either"
        - 0.0 if incompatible (In-person vs Virtual)
    """
    if not loc1 or not loc2:
        return 0.0
    
    loc1 = loc1.strip()
    loc2 = loc2.strip()
    
    if loc1 == loc2:
        if loc1 == "Either":
            return 0.5
        return 1.0
    
    if loc1 == "Either" or loc2 == "Either":
        return 0.8
    
    # Incompatible preferences
    return 0.0


def compute_compatibility_score(
    student1: Dict[str, Any],
    student2: Dict[str, Any],
    availability_weight: float = 0.6,
    preference_weight: float = 0.25,
    location_weight: float = 0.15
) -> float:
    """
    Compute overall compatibility score between two students.
    
    Args:
        student1: Student 1 data
        student2: Student 2 data
        availability_weight: Weight for availability overlap (default 0.6)
        preference_weight: Weight for preference alignment (default 0.25)
        location_weight: Weight for location preference alignment (default 0.15)
    
    Returns:
        Compatibility score between 0 and 1
    """
    avail1 = student1.get('availability', [])
    avail2 = student2.get('availability', [])
    pref1 = student1.get('study_preference', '')
    pref2 = student2.get('study_preference', '')
    loc1 = student1.get('location_preference', 'Either')
    loc2 = student2.get('location_preference', 'Either')
    
    availability_overlap = compute_availability_overlap(avail1, avail2)
    preference_alignment = compute_preference_alignment(pref1, pref2)
    location_alignment = compute_location_alignment(loc1, loc2)
    
    score = (availability_weight * availability_overlap) + \
            (preference_weight * preference_alignment) + \
            (location_weight * location_alignment)
    
    return score


def compute_group_metrics(group: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute aggregate metrics for a group of students.
    
    Args:
        group: List of student dictionaries
    
    Returns:
        Dictionary with group metrics
    """
    if len(group) < 2:
        return {
            "availability_overlap": 0.0,
            "preference_alignment": 0.0,
            "avg_compatibility": 0.0
        }
    
    # Compute pairwise overlaps
    availability_overlaps = []
    preference_alignments = []
    location_alignments = []
    
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            avail_overlap = compute_availability_overlap(
                group[i].get('availability', []),
                group[j].get('availability', [])
            )
            availability_overlaps.append(avail_overlap)
            
            pref_align = compute_preference_alignment(
                group[i].get('study_preference', ''),
                group[j].get('study_preference', '')
            )
            preference_alignments.append(pref_align)
            
            loc_align = compute_location_alignment(
                group[i].get('location_preference', 'Either'),
                group[j].get('location_preference', 'Either')
            )
            location_alignments.append(loc_align)
    
    avg_availability_overlap = sum(availability_overlaps) / len(availability_overlaps) if availability_overlaps else 0.0
    avg_preference_alignment = sum(preference_alignments) / len(preference_alignments) if preference_alignments else 0.0
    avg_location_alignment = sum(location_alignments) / len(location_alignments) if location_alignments else 0.0
    avg_compatibility = (0.6 * avg_availability_overlap) + (0.25 * avg_preference_alignment) + (0.15 * avg_location_alignment)
    
    return {
        "availability_overlap": round(avg_availability_overlap, 3),
        "preference_alignment": round(avg_preference_alignment, 3),
        "location_alignment": round(avg_location_alignment, 3),
        "avg_compatibility": round(avg_compatibility, 3)
    }


def match_students(
    submissions: List[Dict[str, Any]],
    min_group_size: int = 3,
    max_group_size: int = 5
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Match students into groups using a greedy algorithm.
    
    Args:
        submissions: List of student submission dictionaries
        min_group_size: Minimum group size (default 3)
        max_group_size: Maximum group size (default 5)
    
    Returns:
        Tuple of (matched_groups, unmatched_students)
    """
    if not submissions:
        return [], []
    
    # Group by course first
    course_groups: Dict[str, List[Dict[str, Any]]] = {}
    for submission in submissions:
        course = submission.get('course', 'UNKNOWN')
        if course not in course_groups:
            course_groups[course] = []
        course_groups[course].append(submission)
    
    matched_groups = []
    unmatched_students = []
    
    # Process each course separately
    for course, students in course_groups.items():
        logger.info(f"Matching {len(students)} students for course {course}")
        
        # Create a copy to track unmatched
        # Note: Students can be in multiple groups (one per course), so we don't track "used"
        remaining = students.copy()
        
        # Greedy matching: repeatedly form best groups
        while len(remaining) >= min_group_size:
            # Start with the first unmatched student
            if not remaining:
                break
            
            group = [remaining.pop(0)]
            group_ids = {group[0].get('id')}
            
            # Try to add compatible students
            while len(group) < max_group_size and remaining:
                best_candidate = None
                best_score = -1
                best_index = -1
                
                # Find the most compatible remaining student
                for idx, candidate in enumerate(remaining):
                    if candidate.get('id') in group_ids:
                        continue
                    
                    # Compute average compatibility with current group
                    scores = []
                    for member in group:
                        score = compute_compatibility_score(member, candidate)
                        scores.append(score)
                    
                    avg_score = sum(scores) / len(scores) if scores else 0.0
                    
                    if avg_score > best_score:
                        best_score = avg_score
                        best_candidate = candidate
                        best_index = idx
                
                # Add candidate if compatibility is reasonable (threshold: 0.3)
                if best_candidate and best_score >= 0.3:
                    group.append(best_candidate)
                    group_ids.add(best_candidate.get('id'))
                    remaining.pop(best_index)
                else:
                    # No good candidates, stop growing this group
                    break
            
            # If group meets minimum size, save it
            if len(group) >= min_group_size:
                # Compute group metrics
                metrics = compute_group_metrics(group)
                
                # Create match record
                match_record = {
                    "id": str(uuid.uuid4()),
                    "course": course,
                    "student_ids": [s.get('id') for s in group],
                    "group_members": [
                        {
                            "id": s.get('id'),
                            "name": s.get('name'),
                            "email": s.get('email'),
                            "study_preference": s.get('study_preference'),
                            "location_preference": s.get('location_preference', 'Either')
                        }
                        for s in group
                    ],
                    "group_size": len(group),
                    "availability_overlap": metrics["availability_overlap"],
                    "preference_alignment": metrics["preference_alignment"],
                    "location_alignment": metrics.get("location_alignment", 0.0),
                    "avg_compatibility": metrics["avg_compatibility"]
                }
                
                matched_groups.append(match_record)
                logger.info(f"Created group of {len(group)} students for {course}")
            else:
                # Group too small, add back to unmatched
                unmatched_students.extend(group)
        
        # Add remaining unmatched students
        unmatched_students.extend(remaining)
    
    logger.info(f"Matched {len(matched_groups)} groups, {len(unmatched_students)} unmatched students")
    
    return matched_groups, unmatched_students

