"""
Test Configuration Module
Tests for config.py
"""

import pytest
import torch
from src.config import Configuration


class TestConfiguration:
    """Test suite for Configuration class"""
    
    @pytest.fixture
    def config(self):
        """Fixture: Create configuration instance"""
        return Configuration()
    
    def test_config_initialization(self, config):
        """Test config initializes correctly"""
        assert config is not None
        assert config.device is not None
        assert isinstance(config.device, torch.device)
    
    def test_model_config(self, config):
        """Test model configuration"""
        model_config = config.get_model_config()
        assert model_config['vocab_size'] == 5000
        assert model_config['hidden_dim'] == 256
        assert model_config['num_heads'] == 8
        assert model_config['num_layers'] == 4
        assert model_config['max_seq_length'] == 512
    
    def test_training_config(self, config):
        """Test training configuration"""
        training_config = config.get_training_config()
        assert training_config['learning_rate'] == 0.0001
        assert training_config['batch_size'] == 32
        assert training_config['epochs'] == 10
    
    def test_scraper_config(self, config):
        """Test scraper configuration"""
        scraper_config = config.get_scraper_config()
        assert scraper_config['timeout'] == 10
        assert scraper_config['max_jobs'] == 50
        assert len(scraper_config['platforms']) > 0
    
    def test_customizer_config(self, config):
        """Test customizer configuration"""
        customizer_config = config.get_customizer_config()
        assert customizer_config['max_resume_length'] == 2000
        assert customizer_config['skill_matching_threshold'] == 0.5
    
    def test_classifier_config(self, config):
        """Test classifier configuration"""
        classifier_config = config.get_classifier_config()
        assert classifier_config['embedding_dim'] == 300
        assert classifier_config['num_classes'] == 2
        assert classifier_config['relevance_threshold'] == 0.5
    
    def test_agent_config(self, config):
        """Test agent configuration"""
        agent_config = config.get_agent_config()
        assert agent_config['max_applications_per_run'] == 10
        assert agent_config['min_relevance_score'] == 0.3
        assert agent_config['auto_apply'] is False
    
    def test_logging_config(self, config):
        """Test logging configuration"""
        assert 'log_level' in config.logging_config
        assert 'log_file' in config.logging_config
        assert config.logging_config['log_level'] == 'INFO'
    
    def test_get_all_config(self, config):
        """Test get_all returns full config"""
        all_config = config.get_all()
        assert 'model' in all_config
        assert 'training' in all_config
        assert 'scraper' in all_config
        assert 'customizer' in all_config
        assert 'classifier' in all_config
        assert 'agent' in all_config
    
    def test_update_config(self, config):
        """Test updating configuration"""
        config.update_config('training', {'learning_rate': 0.0005})
        assert config.training_config['learning_rate'] == 0.0005
    
    def test_update_invalid_section(self, config):
        """Test updating invalid section raises error"""
        with pytest.raises(ValueError):
            config.update_config('invalid_section', {})
    
    def test_to_dict(self, config):
        """Test converting config to dictionary"""
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert len(config_dict) > 0
    
    def test_repr(self, config):
        """Test string representation"""
        repr_str = repr(config)
        assert 'Configuration' in repr_str
        assert 'device' in repr_str
    
    def test_device_detection(self, config):
        """Test device is CPU or CUDA"""
        device_str = str(config.device)
        assert device_str in ['cpu', 'cuda']
    
    def test_feature_flags(self, config):
        """Test feature flags"""
        assert config.features['use_mayini_model'] is True
        assert config.features['enable_caching'] is True
        assert config.features['enable_logging'] is True
    
    def test_paths_config(self, config):
        """Test paths configuration"""
        assert 'models_dir' in config.paths
        assert 'data_dir' in config.paths
        assert 'logs_dir' in config.paths
        assert 'output_dir' in config.paths
    
    def test_config_immutability_option(self, config):
        """Test that we can get copy of config"""
        model_config1 = config.get_model_config()
        model_config2 = config.get_model_config()
        assert model_config1 == model_config2
