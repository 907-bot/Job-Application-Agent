"""
Test Application Agent Module
Tests for agent.py
"""

import pytest
from src.scraper import JobScraper
from src.customizer import ResumeCustomizer
from src.classifier import JobRelevanceClassifier
from src.utils import UtilityFunctions
from src.mayini_model import MAYINIModel, MAYINIVocabulary
from src.agent import JobApplicationAgent


class TestJobApplicationAgent:
    """Test suite for JobApplicationAgent class"""
    
    @pytest.fixture
    def agent(self):
        """Fixture: Create agent instance with all components"""
        vocab = MAYINIVocabulary(vocab_size=5000)
        model = MAYINIModel(vocab_size=5000, hidden_dim=256, num_heads=8, num_layers=4)
        scraper = JobScraper()
        customizer = ResumeCustomizer(model, vocab)
        classifier = JobRelevanceClassifier(embedding_dim=300)
        utils = UtilityFunctions()
        
        return JobApplicationAgent(scraper, customizer, classifier, utils)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with all components"""
        assert agent is not None
        assert agent.scraper is not None
        assert agent.customizer is not None
        assert agent.classifier is not None
        assert agent.utils is not None
    
    def test_run_workflow(self, agent):
        """Test complete workflow execution"""
        results = agent.run_workflow("python", "Remote", num_jobs=5)
        
        assert results is not None
        assert 'total_jobs_found' in results
        assert 'relevant_jobs' in results
        assert 'applications' in results
    
    def test_workflow_returns_valid_data(self, agent):
        """Test workflow returns properly structured data"""
        results = agent.run_workflow("python docker", "Remote", num_jobs=5)
        
        assert results['total_jobs_found'] >= 0
        assert results['relevant_jobs'] >= 0
        assert isinstance(results['applications'], list)
        assert 0 <= results['pass_rate'] <= 1
    
    def test_workflow_no_jobs_found(self, agent):
        """Test workflow when no jobs found"""
        results = agent.run_workflow("nonexistent_xyz", "", num_jobs=5)
        
        assert results['total_jobs_found'] == 0
        assert results['relevant_jobs'] == 0
        assert len(results['applications']) == 0
    
    def test_get_top_matches(self, agent):
        """Test getting top matches"""
        agent.run_workflow("python", "", num_jobs=5)
        top_matches = agent.get_top_matches(n=3)
        
        assert len(top_matches) <= 3
    
    def test_top_matches_ordered(self, agent):
        """Test top matches are ordered by relevance"""
        agent.run_workflow("python", "", num_jobs=5)
        top_matches = agent.get_top_matches(n=5)
        
        # Check if ordered (each score >= next score)
        for i in range(len(top_matches) - 1):
            assert top_matches[i]['relevance_score'] >= top_matches[i+1]['relevance_score']
    
    def test_apply_to_job(self, agent):
        """Test applying to a single job"""
        results = agent.run_workflow("python", "", num_jobs=5, min_relevance=0.3)
        
        if results['applications']:
            application = results['applications'][0]
            result = agent.apply_to_job(application)
            
            assert 'status' in result
            assert result['status'] == 'Submitted'
            assert 'job_id' in result
    
    def test_batch_apply(self, agent):
        """Test batch application"""
        results = agent.run_workflow("python", "", num_jobs=5, min_relevance=0.5)
        
        if results['applications']:
            batch_results = agent.batch_apply(results['applications'], threshold=0.6)
            assert isinstance(batch_results, list)
    
    def test_workflow_history(self, agent):
        """Test workflow history tracking"""
        agent.run_workflow("python", "", num_jobs=3)
        agent.run_workflow("docker", "", num_jobs=3)
        
        history = agent.get_workflow_history()
        assert len(history) == 2
    
    def test_export_results_json(self, agent):
        """Test exporting results as JSON"""
        agent.run_workflow("python", "", num_jobs=3)
        export = agent.export_results(format='json')
        
        assert export is not None
        assert isinstance(export, str)
        assert len(export) > 0
    
    def test_export_results_text(self, agent):
        """Test exporting results as text"""
        agent.run_workflow("python", "", num_jobs=3)
        export = agent.export_results(format='text')
        
        assert export is not None
        assert 'JOB APPLICATION REPORT' in export
    
    def test_clear_history(self, agent):
        """Test clearing workflow history"""
        agent.run_workflow("python", "", num_jobs=3)
        assert len(agent.workflow_results) > 0
        
        agent.clear_history()
        assert len(agent.workflow_results) == 0
    
    def test_workflow_with_relevance_threshold(self, agent):
        """Test workflow with minimum relevance threshold"""
        results_low = agent.run_workflow("python", "", num_jobs=5, min_relevance=0.1)
        results_high = agent.run_workflow("python", "", num_jobs=5, min_relevance=0.9)
        
        # Higher threshold should return fewer results
        assert results_low['relevant_jobs'] >= results_high['relevant_jobs']
    
    def test_application_includes_customization(self, agent):
        """Test that applications include customized resumes"""
        results = agent.run_workflow("python", "", num_jobs=3, min_relevance=0.3)
        
        if results['applications']:
            app = results['applications'][0]
            assert 'customized_resume' in app
            assert 'summary' in app['customized_resume']
    
    def test_application_includes_match_details(self, agent):
        """Test that applications include match details"""
        results = agent.run_workflow("python", "", num_jobs=3, min_relevance=0.3)
        
        if results['applications']:
            app = results['applications'][0]
            assert 'match_details' in app
            assert 'matching_skills' in app['match_details']
    
    def test_repr(self, agent):
        """Test string representation"""
        repr_str = repr(agent)
        assert 'JobApplicationAgent' in repr_str
    
    def test_workflow_results_preservation(self, agent):
        """Test that workflow results are preserved"""
        results1 = agent.run_workflow("python", "", num_jobs=3)
        results2 = agent.run_workflow("docker", "", num_jobs=3)
        
        history = agent.get_workflow_history()
        assert results1 in history
        assert results2 in history
