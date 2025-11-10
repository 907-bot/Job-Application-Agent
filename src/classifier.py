"""
Job Relevance Classifier Module
ML-based job relevance classification
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple


class JobRelevanceClassifier(nn.Module):
    """Neural network for job relevance classification"""
    
    def __init__(self, embedding_dim: int = 300, hidden_dim: int = 128, dropout: float = 0.1):
        """
        Initialize classifier
        
        Args:
            embedding_dim: Input embedding dimension
            hidden_dim: Hidden layer dimension
            dropout: Dropout rate
        """
        super().__init__()
        
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        
        # Classification network
        self.classifier = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Input tensor [batch, embedding_dim]
            
        Returns:
            Relevance scores [batch, 1]
        """
        return self.classifier(x)
    
    def classify_job(self, job: Dict, resume_skills: List[str]) -> float:
        """
        Classify job relevance based on skill matching
        
        Args:
            job: Job dictionary
            resume_skills: List of skills from resume
            
        Returns:
            Relevance score (0-1)
        """
        job_skills = job.get('requirements', [])
        job_experience = job.get('experience_required', 0)
        
        if not job_skills:
            return 0.5  # Neutral if no requirements
        
        # Skill matching score
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        
        matching_skills = len(resume_set & job_set)
        total_required = len(job_set)
        
        skill_score = matching_skills / total_required if total_required > 0 else 0
        
        # Experience matching (simplified)
        # This would normally use the neural network
        
        return min(skill_score, 1.0)
    
    def batch_classify(self, jobs: List[Dict], resume_skills: List[str]) -> List[float]:
        """
        Classify multiple jobs
        
        Args:
            jobs: List of job dictionaries
            resume_skills: Resume skills
            
        Returns:
            List of relevance scores
        """
        return [self.classify_job(job, resume_skills) for job in jobs]
    
    def filter_relevant_jobs(
        self,
        jobs: List[Dict],
        resume_skills: List[str],
        threshold: float = 0.5
    ) -> List[Tuple[Dict, float]]:
        """
        Filter jobs by relevance threshold
        
        Args:
            jobs: List of jobs
            resume_skills: Resume skills
            threshold: Minimum relevance score
            
        Returns:
            List of (job, score) tuples for relevant jobs
        """
        relevant = []
        
        for job in jobs:
            score = self.classify_job(job, resume_skills)
            if score >= threshold:
                relevant.append((job, score))
        
        # Sort by score (descending)
        relevant.sort(key=lambda x: x[1], reverse=True)
        
        return relevant
    
    def rank_jobs(self, jobs: List[Dict], resume_skills: List[str]) -> List[Tuple[Dict, float]]:
        """
        Rank all jobs by relevance
        
        Args:
            jobs: List of jobs
            resume_skills: Resume skills
            
        Returns:
            Sorted list of (job, score) tuples
        """
        scored_jobs = [(job, self.classify_job(job, resume_skills)) for job in jobs]
        scored_jobs.sort(key=lambda x: x[1], reverse=True)
        return scored_jobs
    
    def get_match_details(self, job: Dict, resume_skills: List[str]) -> Dict:
        """
        Get detailed match information
        
        Args:
            job: Job dictionary
            resume_skills: Resume skills
            
        Returns:
            Dictionary with match details
        """
        job_skills = job.get('requirements', [])
        
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        
        matching = resume_set & job_set
        missing = job_set - resume_set
        extra = resume_set - job_set
        
        score = len(matching) / len(job_set) if job_set else 0
        
        return {
            'relevance_score': score,
            'matching_skills': list(matching),
            'missing_skills': list(missing),
            'extra_skills': list(extra),
            'match_percentage': f"{score * 100:.1f}%",
            'recommendation': self._get_recommendation(score)
        }
    
    def _get_recommendation(self, score: float) -> str:
        """Get application recommendation based on score"""
        if score >= 0.8:
            return "Highly Recommended - Strong match"
        elif score >= 0.6:
            return "Recommended - Good match"
        elif score >= 0.4:
            return "Consider - Moderate match"
        elif score >= 0.2:
            return "Possible - Weak match"
        else:
            return "Not Recommended - Poor match"
    
    def __repr__(self) -> str:
        """String representation"""
        return f"JobRelevanceClassifier(embedding_dim={self.embedding_dim}, hidden_dim={self.hidden_dim})"
