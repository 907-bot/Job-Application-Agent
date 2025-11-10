"""
Test Job Scraper Module
Tests for scraper.py
"""

import pytest
from src.scraper import JobScraper


class TestJobScraper:
    """Test suite for JobScraper class"""
    
    @pytest.fixture
    def scraper(self):
        """Fixture: Create scraper instance"""
        return JobScraper()
    
    def test_scraper_initialization(self, scraper):
        """Test scraper initializes with sample jobs"""
        assert scraper is not None
        assert len(scraper.sample_jobs) > 0
    
    def test_get_job_count(self, scraper):
        """Test getting total job count"""
        count = scraper.get_job_count()
        assert count == len(scraper.sample_jobs)
        assert count >= 5
    
    def test_get_all_jobs(self, scraper):
        """Test retrieving all jobs"""
        jobs = scraper.get_all_jobs()
        assert len(jobs) > 0
        assert isinstance(jobs, list)
    
    def test_search_jobs_keyword(self, scraper):
        """Test searching jobs by keyword"""
        results = scraper.search_jobs(keywords="python")
        assert len(results) > 0
        # At least one should mention Python
        assert any('python' in str(job).lower() for job in results)
    
    def test_search_jobs_no_keyword(self, scraper):
        """Test searching all jobs without keyword"""
        results = scraper.search_jobs(keywords="")
        assert len(results) > 0
    
    def test_search_jobs_location(self, scraper):
        """Test searching jobs by location"""
        results = scraper.search_jobs(location="Remote")
        assert len(results) > 0
        assert all("Remote" in job['location'] for job in results)
    
    def test_search_jobs_limit(self, scraper):
        """Test search result limit"""
        results = scraper.search_jobs(keywords="", limit=3)
        assert len(results) <= 3
    
    def test_search_jobs_no_match(self, scraper):
        """Test search with no matching results"""
        results = scraper.search_jobs(keywords="nonexistent_skill_xyz")
        assert len(results) == 0
    
    def test_get_job_by_id(self, scraper):
        """Test getting specific job by ID"""
        all_jobs = scraper.get_all_jobs()
        job_id = all_jobs[0]['id']
        job = scraper.get_job_by_id(job_id)
        assert job is not None
        assert job['id'] == job_id
    
    def test_get_job_by_id_not_found(self, scraper):
        """Test getting non-existent job"""
        job = scraper.get_job_by_id('nonexistent_id')
        assert job is None
    
    def test_filter_by_experience(self, scraper):
        """Test filtering jobs by experience"""
        all_jobs = scraper.get_all_jobs()
        filtered = scraper.filter_by_experience(all_jobs, 3, 5)
        assert len(filtered) > 0
        assert all(3 <= job['experience_required'] <= 5 for job in filtered)
    
    def test_filter_by_experience_empty(self, scraper):
        """Test filtering with no matches"""
        all_jobs = scraper.get_all_jobs()
        filtered = scraper.filter_by_experience(all_jobs, 20, 30)
        assert len(filtered) == 0
    
    def test_filter_by_skills(self, scraper):
        """Test filtering jobs by skills"""
        all_jobs = scraper.get_all_jobs()
        filtered = scraper.filter_by_skills(all_jobs, ['Python'])
        assert len(filtered) > 0
    
    def test_filter_by_skills_no_match(self, scraper):
        """Test filtering with no matching skills"""
        all_jobs = scraper.get_all_jobs()
        filtered = scraper.filter_by_skills(all_jobs, ['NonexistentSkill123'])
        assert len(filtered) == 0
    
    def test_job_structure(self, scraper):
        """Test job dictionary has required fields"""
        jobs = scraper.get_all_jobs()
        job = jobs[0]
        
        required_fields = ['id', 'title', 'company', 'location', 'requirements']
        for field in required_fields:
            assert field in job
    
    def test_add_sample_job(self, scraper):
        """Test adding sample job"""
        initial_count = scraper.get_job_count()
        
        new_job = {
            'id': 'test_job',
            'title': 'Test Position',
            'company': 'Test Company',
            'location': 'Test Location',
            'requirements': ['Test Skill']
        }
        
        scraper.add_sample_job(new_job)
        assert scraper.get_job_count() == initial_count + 1
    
    def test_repr(self, scraper):
        """Test string representation"""
        repr_str = repr(scraper)
        assert 'JobScraper' in repr_str
        assert str(len(scraper.sample_jobs)) in repr_str
    
    def test_job_immutability(self, scraper):
        """Test that retrieved jobs are copies"""
        job1 = scraper.get_job_by_id(scraper.sample_jobs[0]['id'])
        job1['title'] = 'Modified Title'
        
        job2 = scraper.get_job_by_id(scraper.sample_jobs[0]['id'])
        assert job2['title'] != 'Modified Title'
    
    def test_search_multiple_keywords(self, scraper):
        """Test searching with multiple keywords"""
        results = scraper.search_jobs(keywords="python docker")
        assert len(results) > 0
    
    def test_job_requirements_format(self, scraper):
        """Test job requirements are in correct format"""
        jobs = scraper.get_all_jobs()
        for job in jobs:
            assert isinstance(job['requirements'], list)
            assert len(job['requirements']) > 0
            assert all(isinstance(req, str) for req in job['requirements'])
