"""
Group clustering and matching logic.
"""
from typing import List, Dict
import numpy as np
from sklearn.cluster import AgglomerativeClustering
import logging
from backend.models.submission import Submission
from backend.src.aggregation.scoring import CompatibilityScorer

logger = logging.getLogger(__name__)


class GroupMatcher:
    """Matches students into optimal study groups."""
    
    def __init__(self, scorer: CompatibilityScorer, min_group_size: int = 3, max_group_size: int = 5):
        """
        Initialize group matcher.
        
        Args:
            scorer: Compatibility scorer instance
            min_group_size: Minimum group size
            max_group_size: Maximum group size
        """
        self.scorer = scorer
        self.min_group_size = min_group_size
        self.max_group_size = max_group_size
    
    def match_students(self, validated_submissions: List[Submission], course_id: str) -> List[Dict]:
        """
        Match students into groups.
        
        Args:
            validated_submissions: List of validated submissions
            course_id: Course identifier
            
        Returns:
            List of match dictionaries
        """
        if len(validated_submissions) < self.min_group_size:
            logger.warning(f"Insufficient participants: {len(validated_submissions)} < {self.min_group_size}")
            return []
        
        # Build compatibility matrix
        n = len(validated_submissions)
        compatibility_matrix = np.zeros((n, n))
        
        submission_dicts = [sub.to_dict() for sub in validated_submissions]
        
        for i in range(n):
            for j in range(i+1, n):
                compat = self.scorer.calculate_compatibility(
                    submission_dicts[i],
                    submission_dicts[j]
                )
                compatibility_matrix[i][j] = compat
                compatibility_matrix[j][i] = compat
        
        # Calculate number of clusters based on desired group size
        n_clusters = max(1, n // self.max_group_size)
        
        # Use hierarchical clustering with compatibility as similarity
        # Convert to distance matrix (1 - similarity)
        distance_matrix = 1 - compatibility_matrix
        
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage='average',
            affinity='precomputed'
        )
        
        try:
            labels = clustering.fit_predict(distance_matrix)
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            # Fallback: simple grouping
            labels = self._simple_grouping(n, self.max_group_size)
        
        # Group by cluster
        groups = {}
        for idx, label in enumerate(labels):
            if label not in groups:
                groups[label] = []
            groups[label].append(validated_submissions[idx])
        
        # Adjust group sizes
        final_groups = self._adjust_group_sizes(groups)
        
        # Format groups
        formatted_groups = []
        for group_id, group_members in enumerate(final_groups, start=1):
            formatted_group = self._format_group(group_members, course_id, group_id)
            formatted_groups.append(formatted_group)
        
        return formatted_groups
    
    def _simple_grouping(self, n: int, max_size: int) -> np.ndarray:
        """Simple grouping fallback."""
        labels = []
        for i in range(n):
            labels.append(i // max_size)
        return np.array(labels)
    
    def _adjust_group_sizes(self, groups: Dict[int, List[Submission]]) -> List[List[Submission]]:
        """
        Adjust group sizes to fit within min/max constraints.
        
        Args:
            groups: Dictionary mapping cluster labels to submissions
            
        Returns:
            List of adjusted groups
        """
        final_groups = []
        all_students = []
        
        # Separate groups that are too small or too large
        for cluster_id, members in groups.items():
            if len(members) < self.min_group_size:
                # Too small - add to pool for redistribution
                all_students.extend(members)
            elif len(members) <= self.max_group_size:
                # Good size
                final_groups.append(members)
            else:
                # Too large - split into multiple groups
                num_splits = (len(members) + self.max_group_size - 1) // self.max_group_size
                split_size = len(members) // num_splits
                
                for i in range(num_splits):
                    start = i * split_size
                    end = start + split_size if i < num_splits - 1 else len(members)
                    final_groups.append(members[start:end])
        
        # Redistribute students from small groups
        if all_students:
            # Try to add to existing groups or create new ones
            for student in all_students:
                added = False
                # Try to add to existing groups that are below max size
                for group in final_groups:
                    if len(group) < self.max_group_size:
                        group.append(student)
                        added = True
                        break
                
                # If not added, create new group
                if not added:
                    final_groups.append([student])
        
        # Remove groups that are still too small
        final_groups = [g for g in final_groups if len(g) >= self.min_group_size]
        
        return final_groups
    
    def _format_group(self, members: List[Submission], course_id: str, group_id: int) -> Dict:
        """
        Format a group of submissions into a match dictionary.
        
        Args:
            members: List of submission objects
            course_id: Course identifier
            group_id: Group identifier
            
        Returns:
            Formatted match dictionary
        """
        from backend.models.match import Match, Member
        
        # Calculate average compatibility
        compat_scores = []
        for i in range(len(members)):
            for j in range(i+1, len(members)):
                score = self.scorer.calculate_compatibility(
                    members[i].to_dict(),
                    members[j].to_dict()
                )
                compat_scores.append(score)
        
        avg_compat = sum(compat_scores) / len(compat_scores) if compat_scores else 0.0
        
        # Find common availability slot
        all_availabilities = [set(m.availability) for m in members]
        common_slots = set.intersection(*all_availabilities) if all_availabilities else set()
        suggested_time = list(common_slots)[0] if common_slots else (members[0].availability[0] if members[0].availability else '')
        
        # Create member objects
        match_members = []
        for member in members:
            match_members.append(Member(
                pennkey=member.pennkey,
                email=f"{member.pennkey}@upenn.edu",  # TODO: Get real email
                name=None  # TODO: Get real name
            ))
        
        match = Match(
            group_id=group_id,
            course=course_id,
            members=match_members,
            compatibility_score=avg_compat,
            suggested_meeting_time=suggested_time
        )
        
        return match.to_dict()

