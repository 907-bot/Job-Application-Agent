"""
Job Application Agent Package
AI-Powered Job Search & Resume Customization Platform
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main components for easy access
from .config import Configuration
from .utils import UtilityFunctions
from .mayini_model import MAYINIVocabulary, MAYINIModel
from .scraper import JobScraper
from .customizer import ResumeCustomizer
from .classifier import JobRelevanceClassifier
from .agent import JobApplicationAgent

__all__ = [
    "Configuration",
    "UtilityFunctions",
    "MAYINIVocabulary",
    "MAYINIModel",
    "JobScraper",
    "ResumeCustomizer",
    "JobRelevanceClassifier",
    "JobApplicationAgent",
]
