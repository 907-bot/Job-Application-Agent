"""
Application Agent Module
Orchestrates the complete job application workflow
"""

from typing import Dict, List
import numpy as np
from .scraper import JobScraper
from .customizer import ResumeCustomizer
from .classifier import JobRelevanceClassifier
from .utils import UtilityFunctions


class JobApplicationAgent:
    """Main application agent orchestrating the workflow"""
    
    def __init__(
        self,
        scraper: JobScraper,
        customizer: ResumeCustomizer,
        classifier: JobRelevanceClassifier,
        utils: UtilityFunctions
    ):
        """
        Initialize application agent
        
        Args:
            scraper: Job scraper instance
            customizer: Resume customizer instance
            classifier: Job classifier instance
            utils: Utility functions instance
        """
        self.scraper = scraper
        self.customizer = customizer
        self.classifier = classifier
        self.utils = utils
        self.workflow_results = []
    
    def run_workflow(
        self,
        keywords: str,
        location: str = "",
        num_jobs: int = 5,
        min_relevance: float = 0.3
    ) -> Dict:
        """
        Run complete job application workflow
        
        Args:
            keywords: Job search keywords
            location: Job location
            num_jobs: Maximum number of jobs
            min_relevance: Minimum relevance threshold
            
        Returns:
            Dictionary with workflow results
        """
        # Step 1: Search for jobs
        jobs = self.scraper.search_jobs(keywords, location, num_jobs)
        
        if not jobs:
            return {
                'total_jobs_found': 0,
                'relevant_jobs': 0,
                'applications': [],
                'message': 'No jobs found matching criteria'
            }
        
        # Step 2: Get resume skills
        resume = self.customizer.get_sample_resume()
        resume_skills = resume['skills']
        
        # Step 3: Classify jobs and filter by relevance
        applications = []
        
        for job in jobs:
            # Calculate relevance score
            relevance_score = self.classifier.classify_job(job, resume_skills)
            
            # Only process if meets minimum relevance
            if relevance_score >= min_relevance:
                # Customize resume for this job
                customized_resume = self.customizer.customize_for_job(job)
                
                # Get detailed match information
                match_details = self.classifier.get_match_details(job, resume_skills)
                
                # Create application record
                application = {
                    'job': job,
                    'relevance_score': float(relevance_score),
                    'match_details': match_details,
                    'customized_resume': customized_resume,
                    'cover_letter': self.customizer.generate_cover_letter(job, customized_resume),
                    'application_status': 'Ready to Apply',
                    'recommended_action': match_details['recommendation']
                }
                
                applications.append(application)
        
        # Step 4: Rank applications by relevance
        applications.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Step 5: Generate summary statistics
        summary = self._generate_summary(jobs, applications)
        
        # Store results
        workflow_result = {
            'total_jobs_found': len(jobs),
            'relevant_jobs': len(applications),
            'pass_rate': len(applications) / len(jobs) if jobs else 0,
            'avg_relevance_score': np.mean([a['relevance_score'] for a in applications]) if applications else 0,
            'applications': applications,
            'summary': summary
        }
        
        self.workflow_results.append(workflow_result)
        
        return workflow_result
    
    def _generate_summary(self, jobs: List[Dict], applications: List[Dict]) -> Dict:
        """Generate workflow summary statistics"""
        
        if not applications:
            return {
                'message': 'No relevant jobs found',
                'recommendation': 'Try broadening search criteria'
            }
        
        scores = [a['relevance_score'] for a in applications]
        
        return {
            'total_searched': len(jobs),
            'relevant_found': len(applications),
            'pass_rate': f"{(len(applications) / len(jobs)) * 100:.1f}%",
            'avg_score': f"{np.mean(scores):.3f}",
            'max_score': f"{max(scores):.3f}",
            'min_score': f"{min(scores):.3f}",
            'highly_relevant': sum(1 for s in scores if s >= 0.8),
            'moderately_relevant': sum(1 for s in scores if 0.5 <= s < 0.8),
            'weakly_relevant': sum(1 for s in scores if s < 0.5),
        }
    
    def get_top_matches(self, n: int = 5) -> List[Dict]:
        """
        Get top N job matches from last workflow
        
        Args:
            n: Number of top matches
            
        Returns:
            List of top application dictionaries
        """
        if not self.workflow_results:
            return []
        
        last_result = self.workflow_results[-1]
        applications = last_result.get('applications', [])
        
        return applications[:n]
    
    def apply_to_job(self, application: Dict) -> Dict:
        """
        Simulate applying to a job
        
        Args:
            application: Application dictionary
            
        Returns:
            Application result
        """
        job = application['job']
        
        result = {
            'job_id': job.get('id'),
            'job_title': job.get('title'),
            'company': job.get('company'),
            'application_date': '2025-11-10',
            'status': 'Submitted',
            'relevance_score': application['relevance_score'],
            'resume_customized': True,
            'cover_letter_included': True,
            'message': 'Application successfully submitted'
        }
        
        return result
    
    def batch_apply(self, applications: List[Dict], auto_apply_threshold: float = 0.7) -> List[Dict]:
        """
        Apply to multiple jobs automatically
        
        Args:
            applications: List of applications
            auto_apply_threshold: Minimum score for auto-apply
            
        Returns:
            List of application results
        """
        results = []
        
        for app in applications:
            if app['relevance_score'] >= auto_apply_threshold:
                result = self.apply_to_job(app)
                results.append(result)
        
        return results
    
    def get_workflow_history(self) -> List[Dict]:
        """Get history of all workflow runs"""
        return self.workflow_results.copy()
    
    def export_results(self, format: str = 'json') -> str:
        """
        Export workflow results
        
        Args:
            format: Export format ('json', 'csv', 'text')
            
        Returns:
            Exported data as string
        """
        if not self.workflow_results:
            return "No results to export"
        
        last_result = self.workflow_results[-1]
        
        if format == 'json':
            import json
            return json.dumps(last_result, indent=2)
        elif format == 'text':
            return self._format_text_report(last_result)
        else:
            return str(last_result)
    
    def _format_text_report(self, result: Dict) -> str:
        """Format results as text report"""
        
        report = f"""
JOB APPLICATION REPORT
======================

Summary:
--------
Total Jobs Found: {result['total_jobs_found']}
Relevant Jobs: {result['relevant_jobs']}
Pass Rate: {result['pass_rate']:.1%}
Average Relevance: {result['avg_relevance_score']:.3f}

Top Applications:
-----------------
"""
        
        for i, app in enumerate(result['applications'][:5], 1):
            job = app['job']
            report += f"""
{i}. {job['title']} @ {job['company']}
   Relevance: {app['relevance_score']:.2%}
   Match: {app['match_details']['match_percentage']}
   Recommendation: {app['recommended_action']}
"""
        
        return report
    
    def clear_history(self):
        """Clear workflow history"""
        self.workflow_results = []
    
    def __repr__(self) -> str:
        """String representation"""
        return f"JobApplicationAgent(workflows_run={len(self.workflow_results)})"
