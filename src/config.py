"""
Configuration Module
Manages all application settings and hyperparameters
"""

import os
from typing import Dict, Any
import torch


class Configuration:
    """Central configuration management for the Job Application Agent"""
    
    def __init__(self):
        """Initialize configuration with default values"""
        
        # Device configuration
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Model configuration
        self.model_config = {
            'vocab_size': 5000,
            'hidden_dim': 256,
            'num_heads': 8,
            'num_layers': 4,
            'max_seq_length': 512,
            'dropout_rate': 0.1,
            'embedding_dim': 256,
            'ff_dim': 1024,
        }
        
        # Training configuration
        self.training_config = {
            'learning_rate': 0.0001,
            'batch_size': 32,
            'epochs': 10,
            'weight_decay': 0.01,
            'warmup_steps': 500,
            'gradient_clip': 1.0,
        }
        
        # Job scraper configuration
        self.scraper_config = {
            'timeout': 10,
            'max_jobs': 50,
            'platforms': ['linkedin', 'indeed', 'glassdoor', 'monster'],
            'retry_attempts': 3,
            'delay_between_requests': 1.0,
        }
        
        # Resume customizer configuration
        self.customizer_config = {
            'max_resume_length': 2000,
            'skill_matching_threshold': 0.5,
            'experience_weight': 0.3,
            'skills_weight': 0.5,
            'education_weight': 0.2,
        }
        
        # Job classifier configuration
        self.classifier_config = {
            'embedding_dim': 300,
            'hidden_dim': 128,
            'num_classes': 2,
            'relevance_threshold': 0.5,
            'dropout_rate': 0.1,
        }
        
        # Application agent configuration
        self.agent_config = {
            'max_applications_per_run': 10,
            'min_relevance_score': 0.3,
            'auto_apply': False,
            'save_results': True,
        }
        
        # Logging configuration
        self.logging_config = {
            'log_level': 'INFO',
            'log_file': 'logs/app.log',
            'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'max_log_size': '10MB',
            'backup_count': 5,
        }
        
        # Paths configuration
        self.paths = {
            'models_dir': 'models/',
            'data_dir': 'data/',
            'logs_dir': 'logs/',
            'output_dir': 'output/',
            'cache_dir': 'cache/',
        }
        
        # API configuration (if needed)
        self.api_config = {
            'linkedin_api_key': os.getenv('LINKEDIN_API_KEY', ''),
            'indeed_api_key': os.getenv('INDEED_API_KEY', ''),
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'rate_limit_per_minute': 60,
        }
        
        # Feature flags
        self.features = {
            'use_mayini_model': True,
            'enable_caching': True,
            'use_gpu': torch.cuda.is_available(),
            'enable_logging': True,
            'save_artifacts': True,
        }
        
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return self.model_config
    
    def get_training_config(self) -> Dict[str, Any]:
        """Get training configuration"""
        return self.training_config
    
    def get_scraper_config(self) -> Dict[str, Any]:
        """Get scraper configuration"""
        return self.scraper_config
    
    def get_customizer_config(self) -> Dict[str, Any]:
        """Get customizer configuration"""
        return self.customizer_config
    
    def get_classifier_config(self) -> Dict[str, Any]:
        """Get classifier configuration"""
        return self.classifier_config
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration"""
        return self.agent_config
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            'device': str(self.device),
            'model': self.model_config,
            'training': self.training_config,
            'scraper': self.scraper_config,
            'customizer': self.customizer_config,
            'classifier': self.classifier_config,
            'agent': self.agent_config,
            'logging': self.logging_config,
            'paths': self.paths,
            'api': self.api_config,
            'features': self.features,
        }
    
    def update_config(self, section: str, updates: Dict[str, Any]):
        """
        Update specific configuration section
        
        Args:
            section: Configuration section name
            updates: Dictionary of updates
        """
        if section == 'model':
            self.model_config.update(updates)
        elif section == 'training':
            self.training_config.update(updates)
        elif section == 'scraper':
            self.scraper_config.update(updates)
        elif section == 'customizer':
            self.customizer_config.update(updates)
        elif section == 'classifier':
            self.classifier_config.update(updates)
        elif section == 'agent':
            self.agent_config.update(updates)
        else:
            raise ValueError(f"Unknown configuration section: {section}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.get_all()
    
    def __repr__(self) -> str:
        """String representation"""
        return f"Configuration(device={self.device}, model_hidden_dim={self.model_config['hidden_dim']})"
