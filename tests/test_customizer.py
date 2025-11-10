"""
Test Resume Customizer Module
Tests for customizer.py
"""

import pytest
from src.mayini_model import MAYINIModel, MAYINIVocabulary
from src.customizer import ResumeCustomizer


class TestResumeCustomizer:
    """Test suite for ResumeCustomizer class"""
    
    @pytest.fixture
    def customizer(self):
        """Fixture: Create customizer instance"""
        vocab = MAYINIVocabulary(vocab_size=5000)
        model = MAYINIModel(vocab_size=5000, hidden_dim=256, num_heads=8, num_layers=4)
        return ResumeCustomizer(model, vocab)
    
    def test_customizer_initialization(self, customizer):
        """Test customizer initializes"""
        assert customizer is not None
        assert customizer.model is not None
        assert customizer.vocab is not None
    
    def test_sample_resume_exists(self, customizer):
        """Test sample resume is loaded"""
        resume = customizer.get_sample_resume()
        assert resume is not None
        assert 'name' in resume
        assert 'skills' in resume
    
    def test_sample_resume_structure(self, customizer):
        """Test sample resume has required fields"""
        resume = customizer.get_sample_resume()
        required_fields = ['name', 'email', 'skills', 'experience', 'education']
        for field in required_fields:
            assert field in resume
    
    def test_customize_for_job(self, customizer):
        """Test customizing resume for job"""
        job = {
            'title': 'Senior Python Developer',
            'company': 'Tech Corp',
            'description': 'Python expert needed',
            'requirements': ['Python', 'Docker', 'AWS']
        }
        customized = customizer.customize_for_job(job)
        
        assert customized is not None
        assert 'skills' in customized
        assert 'summary' in customized
    
    def test_customize_prioritizes_matching_skills(self, customizer):
        """Test customization prioritizes matching skills"""
        job = {
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'requirements': ['Python', 'Docker']
        }
        customized = customizer.customize_for_job(job)
        
        # Check that matching skills are prioritized
        assert len(customized['skills']) > 0
        top_skills_lower = [s.lower() for s in customized['skills'][:2]]
        assert any('python' in s for s in top_skills_lower)
    
    def test_customize_generates_summary(self, customizer):
        """Test that customization generates custom summary"""
        job = {
            'title': 'Developer',
            'company': 'Tech Corp',
            'requirements': ['Python']
        }
        customized = customizer.customize_for_job(job)
        
        assert 'summary' in customized
        assert len(customized['summary']) > 0
        assert 'python' in customized['summary'].lower()
    
    def test_matching_skills(self, customizer):
        """Test skill matching functionality"""
        resume_skills = ['Python', 'Docker', 'AWS']
        job_skills = ['Python', 'Docker', 'Kubernetes']
        
        matching = customizer._get_matching_skills(resume_skills, job_skills)
        assert len(matching) >= 2
        assert 'Python' in matching or 'python' in [s.lower() for s in matching]
    
    def test_generate_cover_letter(self, customizer):
        """Test cover letter generation"""
        job = {
            'title': 'Senior Developer',
            'company': 'Tech Inc'
        }
        resume = {
            'name': 'John Doe',
            'customized_for': {'matching_skills': ['Python']}
        }
        
        cover_letter = customizer.generate_cover_letter(job, resume)
        assert cover_letter is not None
        assert 'Senior Developer' in cover_letter
        assert 'Tech Inc' in cover_letter
        assert 'John Doe' in cover_letter
    
    def test_batch_customize(self, customizer):
        """Test batch customization"""
        jobs = [
            {'title': 'Dev 1', 'company': 'Corp 1', 'requirements': ['Python']},
            {'title': 'Dev 2', 'company': 'Corp 2', 'requirements': ['Java']},
        ]
        
        customized_list = customizer.batch_customize(jobs)
        assert len(customized_list) == 2
        assert all('skills' in c for c in customized_list)
    
    def test_update_sample_resume(self, customizer):
        """Test updating sample resume"""
        original_name = customizer.sample_resume['name']
        
        customizer.update_sample_resume({'name': 'New Name'})
        assert customizer.sample_resume['name'] == 'New Name'
        
        customizer.update_sample_resume({'name': original_name})
    
    def test_experience_selection(self, customizer):
        """Test that relevant experience is selected"""
        job = {
            'title': 'Developer',
            'company': 'Tech',
            'requirements': ['microservices', 'kubernetes']
        }
        customized = customizer.customize_for_job(job)
        
        # Should have experience details
        assert 'experience_details' in customized
        assert len(customized['experience_details']) > 0
    
    def test_customization_metadata(self, customizer):
        """Test customization includes metadata"""
        job = {
            'title': 'Developer',
            'company': 'Tech',
            'requirements': ['Python']
        }
        customized = customizer.customize_for_job(job)
        
        assert 'customized_for' in customized
        assert 'job_title' in customized['customized_for']
        assert 'match_score' in customized['customized_for']
    
    def test_repr(self, customizer):
        """Test string representation"""
        repr_str = repr(customizer)
        assert 'ResumeCustomizer' in repr_str
