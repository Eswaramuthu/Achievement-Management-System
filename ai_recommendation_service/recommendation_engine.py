"""
AI Achievement Recommendation Engine

Analyzes student achievements and generates personalized recommendations
by comparing with successful alumni profiles.
"""

import sqlite3
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import Counter
import math

from alumni_profiles import (
    ALUMNI_PROFILES,
    CAREER_PATH_WEIGHTS,
    ACHIEVEMENT_SUGGESTIONS,
    STATISTICAL_INSIGHTS,
    get_alumni_by_career_path,
    get_all_career_paths,
    get_suggestions_for_career,
)


# Path to the existing AMS database (read-only access)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ams.db")


@dataclass
class StudentProfile:
    """Analyzed student profile"""
    student_id: str
    name: str
    department: str
    total_achievements: int
    achievement_types: Dict[str, int]
    skills: List[str]
    positions: Dict[str, int]
    recent_activity: List[Dict]
    profile_vector: List[float]
    predicted_career_paths: List[Dict[str, Any]]


@dataclass
class Recommendation:
    """A single recommendation"""
    type: str
    suggestion: str
    reason: str
    priority: str
    skill_gap: List[str]
    statistical_insight: Optional[str]
    similar_alumni: Optional[str]


class RecommendationEngine:
    """Core AI engine for generating achievement recommendations"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.achievement_types = [
            "Hackathon", "Coding", "Paper", "Project", 
            "Symposium", "Internship", "Other"
        ]
        self.position_weights = {
            "1st": 1.0, "First": 1.0, "Winner": 1.0,
            "2nd": 0.8, "Second": 0.8, "Runner-up": 0.8,
            "3rd": 0.6, "Third": 0.6,
            "Finalist": 0.5, "Top 10": 0.5,
            "Participant": 0.2, "Completed": 0.3,
            "Published": 0.9, "Accepted": 0.8,
        }
    
    def get_student_achievements(self, student_id: str) -> List[Dict]:
        """Fetch student achievements from existing database (read-only)"""
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT * FROM achievements 
                WHERE student_id = ?
                ORDER BY achievement_date DESC
            """, (student_id,))
            
            achievements = [dict(row) for row in cursor.fetchall()]
            connection.close()
            return achievements
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_student_info(self, student_id: str) -> Optional[Dict]:
        """Fetch student basic info from existing database (read-only)"""
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT student_name, student_id, student_dept 
                FROM student WHERE student_id = ?
            """, (student_id,))
            
            row = cursor.fetchone()
            connection.close()
            
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def analyze_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        """Analyze student's achievement history and create profile"""
        student_info = self.get_student_info(student_id)
        if not student_info:
            return None
        
        achievements = self.get_student_achievements(student_id)
        
        # Count achievement types
        type_counts = Counter()
        for ach in achievements:
            ach_type = self._normalize_achievement_type(ach.get("achievement_type", "Other"))
            type_counts[ach_type] += 1
        
        # Extract skills from achievements
        skills = self._extract_skills(achievements)
        
        # Count positions
        position_counts = Counter()
        for ach in achievements:
            pos = ach.get("position", "Participant")
            position_counts[pos] += 1
        
        # Create profile vector for similarity matching
        profile_vector = self._create_profile_vector(type_counts, position_counts, len(achievements))
        
        # Predict best career paths
        predicted_paths = self._predict_career_paths(type_counts, skills)
        
        return StudentProfile(
            student_id=student_id,
            name=student_info.get("student_name", "Unknown"),
            department=student_info.get("student_dept", "Unknown"),
            total_achievements=len(achievements),
            achievement_types=dict(type_counts),
            skills=skills,
            positions=dict(position_counts),
            recent_activity=achievements[:5],
            profile_vector=profile_vector,
            predicted_career_paths=predicted_paths
        )
    
    def _normalize_achievement_type(self, ach_type: str) -> str:
        """Normalize achievement type to standard categories"""
        type_lower = ach_type.lower()
        
        if "hack" in type_lower:
            return "Hackathon"
        elif "code" in type_lower or "coding" in type_lower or "program" in type_lower:
            return "Coding"
        elif "paper" in type_lower or "journal" in type_lower or "research" in type_lower:
            return "Paper"
        elif "project" in type_lower:
            return "Project"
        elif "symposium" in type_lower or "conference" in type_lower:
            return "Symposium"
        elif "intern" in type_lower:
            return "Internship"
        else:
            return "Other"
    
    def _extract_skills(self, achievements: List[Dict]) -> List[str]:
        """Extract skills from achievement details"""
        skills = set()
        
        for ach in achievements:
            # From programming language field
            if ach.get("programming_language"):
                skills.add(ach["programming_language"])
            
            # From coding platform
            if ach.get("coding_platform"):
                skills.add(ach["coding_platform"])
            
            # From database type
            if ach.get("database_type"):
                skills.add(ach["database_type"])
            
            # Extract from description
            desc = (ach.get("achievement_description") or "").lower()
            skill_keywords = [
                "python", "java", "javascript", "react", "node", "sql",
                "machine learning", "ml", "ai", "deep learning", "aws",
                "docker", "kubernetes", "flutter", "android", "ios"
            ]
            for kw in skill_keywords:
                if kw in desc:
                    skills.add(kw.title())
        
        return list(skills)
    
    def _create_profile_vector(self, type_counts: Counter, position_counts: Counter, total: int) -> List[float]:
        """Create numerical vector for profile similarity matching"""
        vector = []
        
        # Achievement type distribution
        for ach_type in self.achievement_types:
            vector.append(type_counts.get(ach_type, 0) / max(total, 1))
        
        # Position quality score
        position_score = 0
        for pos, count in position_counts.items():
            weight = self.position_weights.get(pos, 0.1)
            position_score += weight * count
        vector.append(position_score / max(total, 1))
        
        # Total achievements normalized
        vector.append(min(total / 20, 1.0))  # Cap at 20
        
        return vector
    
    def _predict_career_paths(self, type_counts: Counter, skills: List[str]) -> List[Dict[str, Any]]:
        """Predict best career paths based on achievement pattern"""
        path_scores = {}
        
        for career_path, weights in CAREER_PATH_WEIGHTS.items():
            score = 0
            for ach_type, weight in weights.items():
                count = type_counts.get(ach_type, 0)
                score += weight * count
            path_scores[career_path] = score
        
        # Sort by score
        sorted_paths = sorted(path_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 3 with confidence
        results = []
        total_score = sum(path_scores.values()) or 1
        
        for path, score in sorted_paths[:3]:
            confidence = min((score / total_score) * 100, 100)
            results.append({
                "career_path": path,
                "confidence": round(confidence, 1),
                "matching_alumni": len(get_alumni_by_career_path(path))
            })
        
        return results
    
    def find_similar_alumni(self, profile: StudentProfile, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find alumni with similar profiles"""
        similarities = []
        
        for alumni in ALUMNI_PROFILES:
            # Create alumni vector
            alumni_type_counts = Counter(a["type"] for a in alumni["achievements"])
            alumni_vector = []
            
            for ach_type in self.achievement_types:
                alumni_vector.append(alumni_type_counts.get(ach_type, 0) / len(alumni["achievements"]))
            
            # Position score
            position_score = sum(
                self.position_weights.get(a.get("position", "Participant"), 0.1)
                for a in alumni["achievements"]
            ) / len(alumni["achievements"])
            alumni_vector.append(position_score)
            
            # Total achievements
            alumni_vector.append(min(len(alumni["achievements"]) / 20, 1.0))
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(profile.profile_vector, alumni_vector)
            
            similarities.append({
                "alumni": alumni,
                "similarity": round(similarity * 100, 1)
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def generate_recommendations(self, student_id: str, career_goal: str = None) -> Dict[str, Any]:
        """Generate personalized recommendations for a student"""
        profile = self.analyze_student_profile(student_id)
        
        if not profile:
            return {
                "error": "Student not found",
                "student_id": student_id
            }
        
        # Use predicted career path if not specified
        if not career_goal and profile.predicted_career_paths:
            career_goal = profile.predicted_career_paths[0]["career_path"]
        
        career_goal = career_goal or "Software Development"
        
        # Find similar alumni
        similar_alumni = self.find_similar_alumni(profile)
        
        # Get suggestions for career path
        suggestions = get_suggestions_for_career(career_goal)
        
        # Generate recommendations
        recommendations = []
        
        for suggestion in suggestions:
            # Check if student already has this type
            existing_count = profile.achievement_types.get(suggestion["type"], 0)
            
            # Identify skill gaps
            skill_gap = []
            if similar_alumni:
                top_alumni = similar_alumni[0]["alumni"]
                alumni_skills = set(top_alumni.get("skills", []))
                student_skills = set(profile.skills)
                skill_gap = list(alumni_skills - student_skills)[:3]
            
            # Get statistical insight
            insight_key = f"{suggestion['type']}_{suggestion.get('level', 'National')}"
            statistical_insight = STATISTICAL_INSIGHTS.get(insight_key)
            
            # Adjust priority based on current achievements
            priority = suggestion["priority"]
            if existing_count == 0:
                priority = "high"  # Prioritize new types
            elif existing_count >= 3:
                priority = "low"  # Already have enough of this type
            
            # Find similar alumni mention
            similar_mention = None
            if similar_alumni:
                for sa in similar_alumni:
                    alumni = sa["alumni"]
                    for ach in alumni["achievements"]:
                        if ach["type"] == suggestion["type"]:
                            similar_mention = f"{alumni['name']} ({alumni['current_role']}) had similar achievements"
                            break
                    if similar_mention:
                        break
            
            recommendations.append({
                "type": suggestion["type"],
                "suggestion": suggestion["name"],
                "reason": suggestion["reason"],
                "priority": priority,
                "skill_gap": skill_gap,
                "statistical_insight": statistical_insight,
                "similar_alumni": similar_mention,
                "your_current_count": existing_count
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 1))
        
        # Generate insights
        insights = []
        
        if profile.total_achievements == 0:
            insights.append({
                "type": "warning",
                "message": "Start building your achievement portfolio! Even small wins matter."
            })
        elif profile.total_achievements < 3:
            insights.append({
                "type": "tip",
                "message": "Great start! Students with 5+ achievements have 2x higher placement rates."
            })
        
        if len(profile.achievement_types) < 3:
            insights.append({
                "type": "tip",
                "message": "Diversify your achievements! Students with 3+ types get 60% more opportunities."
            })
        
        if similar_alumni:
            top_alumni = similar_alumni[0]["alumni"]
            insights.append({
                "type": "match",
                "message": f"Your profile is {similar_alumni[0]['similarity']}% similar to {top_alumni['name']}, who is now a {top_alumni['current_role']}"
            })
        
        return {
            "student_id": student_id,
            "student_name": profile.name,
            "department": profile.department,
            "total_achievements": profile.total_achievements,
            "achievement_breakdown": profile.achievement_types,
            "skills": profile.skills,
            "predicted_career_paths": profile.predicted_career_paths,
            "career_goal": career_goal,
            "recommendations": recommendations,
            "similar_alumni": [
                {
                    "name": sa["alumni"]["name"],
                    "role": sa["alumni"]["current_role"],
                    "similarity": sa["similarity"],
                    "tips": sa["alumni"]["tips"],
                    "placement_time": f"{sa['alumni']['time_to_placement_months']} months"
                }
                for sa in similar_alumni
            ],
            "insights": insights
        }


# Create singleton instance
engine = RecommendationEngine()


def get_recommendations(student_id: str, career_goal: str = None) -> Dict[str, Any]:
    """Convenience function to get recommendations"""
    return engine.generate_recommendations(student_id, career_goal)


def get_student_profile(student_id: str) -> Optional[StudentProfile]:
    """Convenience function to get student profile"""
    return engine.analyze_student_profile(student_id)
