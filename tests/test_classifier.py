"""
Test Job Classifier Module
Tests for classifier.py
"""

import pytest
import torch
from src.classifier import JobRelevanceClassifier


class TestJobRelevanceClassifier:
    """Test suite for JobRelevanceClassifier class"""
    
    @pytest.fixture
    def classifier(self):
        """Fixture: Create classifier instance"""
        return JobRelevanceClassifier(embedding_dim=300, hidden_dim=128)
    
    def test_classifier_initialization(self, classifier):
        """Test classifier initializes"""
        assert classifier is not None
        assert classifier.embedding_dim == 300
        assert classifier.hidden_dim == 128
    
    def test_forward_pass(self, classifier):
        """Test forward pass through classifier"""
        x = torch.randn(2, 300)  # Batch of 2, embedding_dim=300
        output = classifier.forward(x)
        
        assert output.shape == (2, 1)
        assert torch.all((output >= 0) & (output <= 1))  # Sigmoid output
    
    def test_classify_job(self, classifier):
        """Test job classification"""
        job = {
            'title': 'Python Developer',
            'requirements': ['Python', 'Docker', 'AWS']
        }
        resume_skills = ['Python', 'Docker', 'Kubernetes']
        
        score = classifier.classify_job(job, resume_skills)
        assert 0 <= score <= 1
    
    def test_classify_job_perfect_match(self, classifier):
        """Test classification with perfect match"""
        job = {
            'requirements': ['Python', 'Docker']
        }
        resume_skills = ['Python', 'Docker']
        
        score = classifier.classify_job(job, resume_skills)
        assert score == 1.0
    
    def test_classify_job_no_match(self, classifier):
        """Test classification with no match"""
        job = {
            'requirements': ['Java', 'Spring']
        }
        resume_skills = ['Python', 'Django']
        
        score = classifier.classify_job(job, resume_skills)
        assert score == 0.0
    
    def test_classify_job_partial_match(self, classifier):
        """Test classification with partial match"""
        job = {
            'requirements': ['Python', 'Docker', 'Kubernetes']
        }
        resume_skills = ['Python', 'Docker']
        
        score = classifier.classify_job(job, resume_skills)
        assert 0 < score < 1
    
    def test_batch_classify(self, classifier):
        """Test batch classification"""
        jobs = [
            {'requirements': ['Python']},
            {'requirements': ['Java']},
            {'requirements': ['Python', 'Docker']},
        ]
        resume_skills = ['Python', 'Docker']
        
        scores = classifier.batch_classify(jobs, resume_skills)
        assert len(scores) == 3
        assert all(0 <= s <= 1 for s in scores)
    
    def test_filter_relevant_jobs(self, classifier):
        """Test filtering jobs by relevance"""
        jobs = [
            {'title': 'Job 1', 'requirements': ['Python']},
            {'title': 'Job 2', 'requirements': ['Java']},
            {'title': 'Job 3', 'requirements': ['Python', 'Docker']},
        ]
        resume_skills = ['Python', 'Docker']
        
        relevant = classifier.filter_relevant_jobs(jobs, resume_skills, threshold=0.3)
        assert len(relevant) > 0
        assert all(score >= 0.3 for job, score in relevant)
    
    def test_rank_jobs(self, classifier):
        """Test job ranking"""
        jobs = [
            {'requirements': ['Java']},
            {'requirements': ['Python', 'Docker']},
            {'requirements': ['Python']},
        ]
        resume_skills = ['Python', 'Docker']
        
        ranked = classifier.rank_jobs(jobs, resume_skills)
        # First job should have highest score
        assert ranked[0][1] >= ranked[1][1]
        assert ranked[0][1] >= ranked[2][1]
    
    def test_get_match_details(self, classifier):
        """Test getting detailed match information"""
        job = {'requirements': ['Python', 'Docker', 'AWS']}
        resume_skills = ['Python', 'Docker', 'Kubernetes']
        
        details = classifier.get_match_details(job, resume_skills)
        
        assert 'relevance_score' in details
        assert 'matching_skills' in details
        assert 'missing_skills' in details
        assert 'recommendation' in details
    
    def test_match_details_accuracy(self, classifier):
        """Test match details accuracy"""
        job = {'requirements': ['Python', 'Docker']}
        resume_skills = ['Python', 'Kubernetes']
        
        details = classifier.get_match_details(job, resume_skills)
        
        assert 'Python' in details['matching_skills']
        assert 'Docker' in details['missing_skills']
        assert len(details['matching_skills']) == 1
        assert len(details['missing_skills']) == 1
    
    def test_recommendation_high_score(self, classifier):
        """Test recommendation for high score"""
        score = 0.9
        rec = classifier._get_recommendation(score)
        assert 'Highly Recommended' in rec
    
    def test_recommendation_medium_score(self, classifier):
        """Test recommendation for medium score"""
        score = 0.5
        rec = classifier._get_recommendation(score)
        assert 'Recommended' in rec or 'Consider' in rec
    
    def test_recommendation_low_score(self, classifier):
        """Test recommendation for low score"""
        score = 0.1
        rec = classifier._get_recommendation(score)
        assert 'Not Recommended' in rec
    
    def test_repr(self, classifier):
        """Test string representation"""
        repr_str = repr(classifier)
        assert 'JobRelevanceClassifier' in repr_str
        assert '300' in repr_str
