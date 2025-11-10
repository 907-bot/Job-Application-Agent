"""
Test Utility Functions Module
Tests for utils.py
"""

import pytest
from src.utils import UtilityFunctions


class TestUtilityFunctions:
    """Test suite for UtilityFunctions class"""
    
    @pytest.fixture
    def utils(self):
        """Fixture: Create utility functions instance"""
        return UtilityFunctions()
    
    def test_clean_text(self, utils):
        """Test text cleaning"""
        text = "Python Programming!@#$ Expert"
        cleaned = utils.clean_text(text)
        assert cleaned == "python programming expert"
        assert "@#$" not in cleaned
    
    def test_clean_text_empty(self, utils):
        """Test cleaning empty text"""
        result = utils.clean_text("")
        assert result == ""
    
    def test_clean_text_lowercase(self, utils):
        """Test text is converted to lowercase"""
        result = utils.clean_text("PYTHON")
        assert result == "python"
    
    def test_extract_skills(self, utils):
        """Test skill extraction"""
        text = "I know Python, Docker, and Kubernetes"
        skills = utils.extract_skills(text)
        assert 'python' in [s.lower() for s in skills]
        assert 'docker' in [s.lower() for s in skills]
    
    def test_extract_skills_not_found(self, utils):
        """Test extraction when no skills present"""
        text = "I like cats and dogs"
        skills = utils.extract_skills(text)
        assert len(skills) == 0
    
    def test_extract_experience(self, utils):
        """Test experience extraction"""
        text = "I have 5 years of experience"
        years = utils.extract_experience(text)
        assert years == 5
    
    def test_extract_experience_plus(self, utils):
        """Test extraction of 5+ years format"""
        text = "5+ years experience"
        years = utils.extract_experience(text)
        assert years == 5
    
    def test_extract_experience_range(self, utils):
        """Test extraction of range format"""
        text = "2-3 years required"
        years = utils.extract_experience(text)
        assert years == 2
    
    def test_extract_experience_not_found(self, utils):
        """Test extraction when no experience mentioned"""
        text = "Just a random text"
        years = utils.extract_experience(text)
        assert years == 0
    
    def test_tokenize(self, utils):
        """Test text tokenization"""
        text = "Python Docker AWS"
        tokens = utils.tokenize(text)
        assert len(tokens) == 3
        assert 'python' in tokens
        assert 'docker' in tokens
        assert 'aws' in tokens
    
    def test_calculate_similarity(self, utils):
        """Test similarity calculation"""
        text1 = "Python programming"
        text2 = "Python programming"
        similarity = utils.calculate_similarity(text1, text2)
        assert 0 <= similarity <= 1
        assert similarity > 0.5
    
    def test_calculate_similarity_different(self, utils):
        """Test similarity of different texts"""
        text1 = "Python"
        text2 = "Java"
        similarity = utils.calculate_similarity(text1, text2)
        assert 0 <= similarity <= 1
    
    def test_calculate_similarity_empty(self, utils):
        """Test similarity with empty text"""
        similarity = utils.calculate_similarity("", "text")
        assert similarity == 0.0
    
    def test_calculate_skill_match(self, utils):
        """Test skill matching"""
        resume_skills = ['Python', 'Docker', 'AWS']
        job_skills = ['Python', 'Docker', 'Kubernetes']
        match = utils.calculate_skill_match(resume_skills, job_skills)
        assert 0 <= match <= 1
        assert match > 0.5
    
    def test_calculate_skill_match_no_overlap(self, utils):
        """Test skill matching with no overlap"""
        resume_skills = ['Python']
        job_skills = ['Java']
        match = utils.calculate_skill_match(resume_skills, job_skills)
        assert match == 0.0
    
    def test_calculate_skill_match_perfect(self, utils):
        """Test perfect skill match"""
        resume_skills = ['Python', 'Docker']
        job_skills = ['Python', 'Docker']
        match = utils.calculate_skill_match(resume_skills, job_skills)
        assert match == 1.0
    
    def test_extract_email(self, utils):
        """Test email extraction"""
        text = "Contact me at john@example.com"
        email = utils.extract_email(text)
        assert email == "john@example.com"
    
    def test_extract_email_not_found(self, utils):
        """Test when email not found"""
        text = "No email here"
        email = utils.extract_email(text)
        assert email == ""
    
    def test_extract_phone(self, utils):
        """Test phone number extraction"""
        text = "Call me at (555) 123-4567"
        phone = utils.extract_phone(text)
        assert "555" in phone or "123" in phone
    
    def test_validate_resume_valid(self, utils):
        """Test resume validation with valid data"""
        resume = {
            'name': 'John Doe',
            'skills': ['Python', 'Docker'],
            'experience': 5
        }
        is_valid, msg = utils.validate_resume(resume)
        assert is_valid is True
        assert msg == ""
    
    def test_validate_resume_missing_field(self, utils):
        """Test resume validation with missing field"""
        resume = {
            'name': 'John Doe',
            'experience': 5
        }
        is_valid, msg = utils.validate_resume(resume)
        assert is_valid is False
        assert "Missing" in msg
    
    def test_validate_job_valid(self, utils):
        """Test job validation with valid data"""
        job = {
            'title': 'Developer',
            'company': 'Tech Corp',
            'requirements': ['Python', 'Docker']
        }
        is_valid, msg = utils.validate_job(job)
        assert is_valid is True
        assert msg == ""
    
    def test_validate_job_missing_field(self, utils):
        """Test job validation with missing field"""
        job = {
            'title': 'Developer',
            'company': 'Tech Corp'
        }
        is_valid, msg = utils.validate_job(job)
        assert is_valid is False
    
    def test_normalize_score(self, utils):
        """Test score normalization"""
        score = utils.normalize_score(50, 0, 100)
        assert score == 0.5
    
    def test_normalize_score_boundary(self, utils):
        """Test score normalization at boundaries"""
        assert utils.normalize_score(0, 0, 100) == 0.0
        assert utils.normalize_score(100, 0, 100) == 1.0
    
    def test_rank_items(self, utils):
        """Test item ranking"""
        items = [
            {'name': 'A', 'score': 10},
            {'name': 'B', 'score': 30},
            {'name': 'C', 'score': 20},
        ]
        ranked = utils.rank_items(items, 'score', reverse=True)
        assert ranked[0]['name'] == 'B'
        assert ranked[0]['score'] == 30
    
    def test_calculate_match_score(self, utils):
        """Test overall match score calculation"""
        resume = {
            'skills': ['Python', 'Docker', 'AWS'],
            'experience': 5
        }
        job = {
            'requirements': ['Python', 'Docker'],
            'experience_required': 3
        }
        score = utils.calculate_match_score(resume, job)
        assert 0 <= score <= 1
        assert score > 0.5
