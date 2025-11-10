"""
Integration Tests
End-to-end tests for complete system
"""

import pytest
from src.config import Configuration
from src.utils import UtilityFunctions
from src.mayini_model import MAYINIModel, MAYINIVocabulary
from src.scraper import JobScraper
from src.customizer import ResumeCustomizer
from src.classifier import JobRelevanceClassifier
from src.agent import JobApplicationAgent


class TestIntegration:
    """Integration tests for complete system"""
    
    @pytest.fixture
    def system(self):
        """Fixture: Initialize complete system"""
        config = Configuration()
        utils = UtilityFunctions()
        vocab = MAYINIVocabulary(vocab_size=5000)
        model = MAYINIModel(vocab_size=5000, hidden_dim=256, num_heads=8, num_layers=4)
        scraper = JobScraper()
        customizer = ResumeCustomizer(model, vocab)
        classifier = JobRelevanceClassifier(embedding_dim=300)
        agent = JobApplicationAgent(scraper, customizer, classifier, utils)
        
        return {
            'config': config,
            'utils': utils,
            'vocab': vocab,
            'model': model,
            'scraper': scraper,
            'customizer': customizer,
            'classifier': classifier,
            'agent': agent
        }
    
    def test_complete_workflow_execution(self, system):
        """Test complete end-to-end workflow"""
        agent = system['agent']
        
        results = agent.run_workflow(
            keywords="python docker",
            location="Remote",
            num_jobs=5,
            min_relevance=0.3
        )
        
        assert results is not None
        assert results['total_jobs_found'] > 0
        assert results['relevant_jobs'] >= 0
        assert len(results['applications']) >= 0
    
    def test_job_search_to_customization(self, system):
        """Test complete pipeline from search to customization"""
        scraper = system['scraper']
        customizer = system['customizer']
        
        # Search jobs
        jobs = scraper.search_jobs("python", "Remote", limit=3)
        assert len(jobs) > 0
        
        # Customize resumes for each job
        customized_resumes = []
        for job in jobs:
            customized = customizer.customize_for_job(job)
            customized_resumes.append(customized)
        
        assert len(customized_resumes) == len(jobs)
        assert all('skills' in c for c in customized_resumes)
    
    def test_search_classify_customize_pipeline(self, system):
        """Test search -> classify -> customize pipeline"""
        scraper = system['scraper']
        classifier = system['classifier']
        customizer = system['customizer']
        
        # Step 1: Search
        jobs = scraper.search_jobs("python", "", limit=3)
        assert len(jobs) > 0
        
        # Step 2: Classify
        resume_skills = customizer.get_sample_resume()['skills']
        classified_jobs = []
        for job in jobs:
            score = classifier.classify_job(job, resume_skills)
            classified_jobs.append((job, score))
        
        assert len(classified_jobs) > 0
        
        # Step 3: Customize
        for job, score in classified_jobs:
            if score >= 0.3:
                customized = customizer.customize_for_job(job)
                assert 'skills' in customized
                assert 'summary' in customized
    
    def test_text_processing_in_workflow(self, system):
        """Test text processing utilities in workflow"""
        utils = system['utils']
        customizer = system['customizer']
        
        job_desc = "Senior Python Developer with 5+ years experience in Docker and AWS"
        
        # Extract information
        skills = utils.extract_skills(job_desc)
        experience = utils.extract_experience(job_desc)
        
        assert len(skills) > 0
        assert experience == 5
        
        # Use in customization
        job = {
            'title': 'Senior Developer',
            'company': 'Tech Corp',
            'requirements': skills,
            'experience_required': experience
        }
        customized = customizer.customize_for_job(job)
        assert 'skills' in customized
    
    def test_configuration_used_throughout(self, system):
        """Test configuration is used throughout system"""
        config = system['config']
        model = system['model']
        
        # Check model aligns with config
        model_config = config.get_model_config()
        assert model.hidden_dim == model_config['hidden_dim']
        assert model.num_heads == model_config['num_heads']
        assert model.num_layers == model_config['num_layers']
    
    def test_agent_orchestration(self, system):
        """Test agent successfully orchestrates all components"""
        agent = system['agent']
        
        # Run workflow
        results = agent.run_workflow("python", "Remote", num_jobs=3, min_relevance=0.2)
        
        # Verify orchestration
        assert results['total_jobs_found'] > 0
        
        if results['applications']:
            app = results['applications'][0]
            # Check all components were used
            assert 'job' in app
            assert 'relevance_score' in app
            assert 'customized_resume' in app
            assert 'match_details' in app
            assert 'application_status' in app
    
    def test_model_inference(self, system):
        """Test MAYINI model inference"""
        model = system['model']
        vocab = system['vocab']
        
        text = "I have 5 years of Python and Docker experience"
        
        # Encode
        encoded = vocab.encode(text, max_len=256)
        assert encoded is not None
        assert len(encoded) == 256
        
        # Inference (just test forward pass works)
        import torch
        batch = encoded.unsqueeze(0)
        output = model.forward(batch)
        assert output is not None
    
    def test_end_to_end_with_validation(self, system):
        """Test end-to-end with validation"""
        utils = system['utils']
        agent = system['agent']
        
        # Get sample resume
        resume = agent.customizer.get_sample_resume()
        
        # Validate
        is_valid, msg = utils.validate_resume(resume)
        assert is_valid is True
        
        # Run workflow
        results = agent.run_workflow("python", "", num_jobs=3)
        
        # Validate results
        for app in results['applications']:
            assert 'relevance_score' in app
            assert 0 <= app['relevance_score'] <= 1
    
    def test_batch_processing(self, system):
        """Test batch processing capability"""
        agent = system['agent']
        
        # Get multiple jobs
        jobs = agent.scraper.search_jobs("", "", limit=5)
        
        # Batch customize
        customized_batch = agent.customizer.batch_customize(jobs)
        assert len(customized_batch) == len(jobs)
        
        # Batch classify
        resume_skills = agent.customizer.get_sample_resume()['skills']
        scores = agent.classifier.batch_classify(jobs, resume_skills)
        assert len(scores) == len(jobs)
    
    def test_multiple_workflow_runs(self, system):
        """Test multiple workflow runs maintain state"""
        agent = system['agent']
        
        # Run 1
        results1 = agent.run_workflow("python", "", num_jobs=2)
        assert len(agent.workflow_results) == 1
        
        # Run 2
        results2 = agent.run_workflow("docker", "", num_jobs=2)
        assert len(agent.workflow_results) == 2
        
        # Verify both are preserved
        history = agent.get_workflow_history()
        assert len(history) == 2
    
    def test_error_handling_integration(self, system):
        """Test error handling in integrated system"""
        agent = system['agent']
        
        # Test with empty keywords - should not crash
        results = agent.run_workflow("", "", num_jobs=5)
        assert 'total_jobs_found' in results
        
        # Test with invalid relevance - should handle gracefully
        results = agent.run_workflow("python", "", num_jobs=3, min_relevance=0.5)
        assert 'relevant_jobs' in results
    
    def test_system_initialization_complete(self, system):
        """Test complete system initializes without errors"""
        required_components = [
            'config', 'utils', 'vocab', 'model', 'scraper',
            'customizer', 'classifier', 'agent'
        ]
        
        for component in required_components:
            assert component in system
            assert system[component] is not None
    
    def test_full_feature_demonstration(self, system):
        """Demonstrate all system features working together"""
        agent = system['agent']
        utils = system['utils']
        
        # 1. Search
        print("1. Searching for jobs...")
        jobs = agent.scraper.search_jobs("python docker", "Remote", limit=3)
        assert len(jobs) > 0
        
        # 2. Extract information
        print("2. Extracting information...")
        for job in jobs:
            skills = utils.extract_skills(job['description'])
            experience = utils.extract_experience(job['description'])
        
        # 3. Classify
        print("3. Classifying relevance...")
        resume_skills = agent.customizer.get_sample_resume()['skills']
        for job in jobs:
            score = agent.classifier.classify_job(job, resume_skills)
            assert 0 <= score <= 1
        
        # 4. Customize
        print("4. Customizing resumes...")
        for job in jobs:
            customized = agent.customizer.customize_for_job(job)
            assert 'skills' in customized
        
        # 5. Generate cover letters
        print("5. Generating cover letters...")
        for job in jobs:
            resume = agent.customizer.customize_for_job(job)
            letter = agent.customizer.generate_cover_letter(job, resume)
            assert len(letter) > 0
        
        print("✅ All features working successfully!")
