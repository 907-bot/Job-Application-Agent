"""
Utility Functions Module
Text processing and helper functions
"""

import re
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class UtilityFunctions:
    """Collection of utility functions for text processing and data manipulation"""
    
    # Common tech skills for matching
    TECH_SKILLS = {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift',
        'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'fastapi', 'spring',
        'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'terraform', 'ansible',
        'aws', 'azure', 'gcp', 'cloud', 'serverless', 'lambda',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
        'rest', 'graphql', 'grpc', 'api', 'microservices', 'kafka', 'rabbitmq',
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'scikit-learn',
        'git', 'agile', 'scrum', 'ci/cd', 'devops', 'linux', 'bash', 'shell'
    }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and alphanumeric
        text = re.sub(r'[^a-z0-9\s+#]', '', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """
        Extract tech skills from text
        
        Args:
            text: Input text (resume, job description)
            
        Returns:
            List of found skills
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in UtilityFunctions.TECH_SKILLS:
            if skill in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))
    
    @staticmethod
    def extract_experience(text: str) -> int:
        """
        Extract years of experience from text
        
        Args:
            text: Input text
            
        Returns:
            Number of years of experience
        """
        # Pattern to match "5 years", "3+ years", "2-3 years"
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*-\s*\d+\s*(?:years?|yrs?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return int(matches[0])
        
        return 0
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Simple tokenization
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        return UtilityFunctions.clean_text(text).split()
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    @staticmethod
    def calculate_skill_match(resume_skills: List[str], job_skills: List[str]) -> float:
        """
        Calculate skill match percentage
        
        Args:
            resume_skills: List of skills from resume
            job_skills: List of required skills from job
            
        Returns:
            Match percentage (0-1)
        """
        if not job_skills:
            return 1.0
        
        if not resume_skills:
            return 0.0
        
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        
        matching = len(resume_set & job_set)
        total = len(job_set)
        
        return matching / total if total > 0 else 0.0
    
    @staticmethod
    def extract_email(text: str) -> str:
        """
        Extract email address from text
        
        Args:
            text: Input text
            
        Returns:
            Email address or empty string
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""
    
    @staticmethod
    def extract_phone(text: str) -> str:
        """
        Extract phone number from text
        
        Args:
            text: Input text
            
        Returns:
            Phone number or empty string
        """
        phone_pattern = r'(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}'
        matches = re.findall(phone_pattern, text)
        return matches[0] if matches else ""
    
    @staticmethod
    def create_resume_summary(resume: Dict) -> str:
        """
        Create a summary from resume dictionary
        
        Args:
            resume: Resume dictionary with keys: name, experience, skills, etc.
            
        Returns:
            Formatted resume summary
        """
        name = resume.get('name', 'N/A')
        experience = resume.get('experience', 0)
        skills = resume.get('skills', [])
        education = resume.get('education', 'N/A')
        
        summary = f"""
        Name: {name}
        Experience: {experience} years
        Skills: {', '.join(skills[:5])}
        Education: {education}
        """
        
        return summary.strip()
    
    @staticmethod
    def format_job_description(job: Dict) -> str:
        """
        Format job dictionary into readable description
        
        Args:
            job: Job dictionary
            
        Returns:
            Formatted job description
        """
        title = job.get('title', 'N/A')
        company = job.get('company', 'N/A')
        location = job.get('location', 'N/A')
        requirements = job.get('requirements', [])
        
        formatted = f"""
        Title: {title}
        Company: {company}
        Location: {location}
        Requirements: {', '.join(requirements)}
        """
        
        return formatted.strip()
    
    @staticmethod
    def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """
        Normalize score to range [0, 1]
        
        Args:
            score: Input score
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            Normalized score
        """
        if max_val == min_val:
            return 0.0
        
        normalized = (score - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    @staticmethod
    def rank_items(items: List[Dict], score_key: str = 'score', reverse: bool = True) -> List[Dict]:
        """
        Rank items by score
        
        Args:
            items: List of dictionaries
            score_key: Key to use for sorting
            reverse: Sort in descending order
            
        Returns:
            Sorted list of items
        """
        return sorted(items, key=lambda x: x.get(score_key, 0), reverse=reverse)
    
    @staticmethod
    def calculate_match_score(resume: Dict, job: Dict) -> float:
        """
        Calculate overall match score between resume and job
        
        Args:
            resume: Resume dictionary
            job: Job dictionary
            
        Returns:
            Match score (0-1)
        """
        resume_skills = resume.get('skills', [])
        job_skills = job.get('requirements', [])
        
        resume_exp = resume.get('experience', 0)
        job_exp = job.get('experience_required', 0)
        
        # Skill match (weight: 0.6)
        skill_score = UtilityFunctions.calculate_skill_match(resume_skills, job_skills)
        
        # Experience match (weight: 0.4)
        if job_exp > 0:
            exp_score = min(1.0, resume_exp / job_exp)
        else:
            exp_score = 1.0
        
        # Weighted average
        total_score = (skill_score * 0.6) + (exp_score * 0.4)
        
        return total_score
    
    @staticmethod
    def validate_resume(resume: Dict) -> Tuple[bool, str]:
        """
        Validate resume dictionary
        
        Args:
            resume: Resume dictionary
            
        Returns:
            (is_valid, error_message)
        """
        required_keys = ['name', 'skills', 'experience']
        
        for key in required_keys:
            if key not in resume:
                return False, f"Missing required field: {key}"
        
        if not resume['name']:
            return False, "Name cannot be empty"
        
        if not isinstance(resume['skills'], list):
            return False, "Skills must be a list"
        
        if not isinstance(resume['experience'], (int, float)):
            return False, "Experience must be a number"
        
        return True, ""
    
    @staticmethod
    def validate_job(job: Dict) -> Tuple[bool, str]:
        """
        Validate job dictionary
        
        Args:
            job: Job dictionary
            
        Returns:
            (is_valid, error_message)
        """
        required_keys = ['title', 'company', 'requirements']
        
        for key in required_keys:
            if key not in job:
                return False, f"Missing required field: {key}"
        
        if not job['title']:
            return False, "Title cannot be empty"
        
        if not job['company']:
            return False, "Company cannot be empty"
        
        if not isinstance(job['requirements'], list):
            return False, "Requirements must be a list"
        
        return True, ""
