"""
Compatibility scoring for student matching.
"""
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class CompatibilityScorer:
    """Calculates compatibility scores between students."""
    
    # Weights for different compatibility factors
    AVAILABILITY_WEIGHT = 0.4
    STUDY_STYLE_WEIGHT = 0.3
    GOAL_WEIGHT = 0.3
    
    def calculate_compatibility(self, student1: Dict, student2: Dict) -> float:
        """
        Calculate compatibility score between two students.
        
        Args:
            student1: First student's submission data
            student2: Second student's submission data
            
        Returns:
            Compatibility score between 0.0 and 1.0
        """
        score = 0.0
        
        # Availability overlap (40% weight)
        avail_score = self._calculate_availability_score(
            student1.get('availability', []),
            student2.get('availability', [])
        )
        score += self.AVAILABILITY_WEIGHT * avail_score
        
        # Study style match (30% weight)
        style_score = self._calculate_style_score(
            student1.get('study_style', ''),
            student2.get('study_style', '')
        )
        score += self.STUDY_STYLE_WEIGHT * style_score
        
        # Goal alignment (30% weight)
        goal_score = self._calculate_goal_score(
            student1.get('goal', ''),
            student2.get('goal', '')
        )
        score += self.GOAL_WEIGHT * goal_score
        
        return score
    
    def _calculate_availability_score(self, avail1: list, avail2: list) -> float:
        """
        Calculate availability overlap score.
        
        Args:
            avail1: First student's availability slots
            avail2: Second student's availability slots
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not avail1 or not avail2:
            return 0.0
        
        # Calculate overlap
        overlap = len(set(avail1) & set(avail2))
        max_avail = max(len(avail1), len(avail2))
        
        if max_avail == 0:
            return 0.0
        
        # Normalize by maximum availability length
        return min(1.0, overlap / max_avail)
    
    def _calculate_style_score(self, style1: str, style2: str) -> float:
        """
        Calculate study style match score.
        
        Args:
            style1: First student's study style
            style2: Second student's study style
            
        Returns:
            1.0 if match, 0.0 otherwise
        """
        if not style1 or not style2:
            return 0.0
        
        return 1.0 if style1.lower() == style2.lower() else 0.0
    
    def _calculate_goal_score(self, goal1: str, goal2: str) -> float:
        """
        Calculate goal alignment score.
        
        Args:
            goal1: First student's goal
            goal2: Second student's goal
            
        Returns:
            1.0 if match, 0.0 otherwise
        """
        if not goal1 or not goal2:
            return 0.0
        
        return 1.0 if goal1.lower() == goal2.lower() else 0.0

