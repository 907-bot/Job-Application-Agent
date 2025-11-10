"""
Job Scraper Module
Search and retrieve job postings
"""

from typing import List, Dict, Optional
import time


class JobScraper:
    """Job scraper for multiple platforms"""
    
    def __init__(self):
        """Initialize job scraper with sample data"""
        
        # Sample job database
        self.sample_jobs = [
            {
                'id': 'job_001',
                'title': 'Senior Python Developer',
                'company': 'Tech Giants Inc',
                'location': 'Remote',
                'description': 'We are looking for an experienced Python developer with 5+ years expertise in Django, FastAPI, and cloud technologies.',
                'requirements': ['Python', 'Django', 'FastAPI', 'Docker', 'AWS', 'PostgreSQL', 'REST API'],
                'experience_required': 5,
                'salary_range': '$120k - $160k',
                'posted_date': '2025-11-01',
                'job_type': 'Full-time',
            },
            {
                'id': 'job_002',
                'title': 'React Frontend Developer',
                'company': 'Innovation Labs',
                'location': 'San Francisco, CA',
                'description': 'Build amazing web applications with React, TypeScript, and modern frontend tools.',
                'requirements': ['React', 'TypeScript', 'JavaScript', 'CSS', 'REST API', 'Git'],
                'experience_required': 3,
                'salary_range': '$100k - $140k',
                'posted_date': '2025-11-03',
                'job_type': 'Full-time',
            },
            {
                'id': 'job_003',
                'title': 'Machine Learning Engineer',
                'company': 'AI Solutions Corp',
                'location': 'Remote',
                'description': 'Develop and deploy machine learning models using TensorFlow, PyTorch, and cloud infrastructure.',
                'requirements': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'SQL', 'AWS', 'Docker'],
                'experience_required': 4,
                'salary_range': '$130k - $180k',
                'posted_date': '2025-11-05',
                'job_type': 'Full-time',
            },
            {
                'id': 'job_004',
                'title': 'DevOps Engineer',
                'company': 'Cloud Systems Ltd',
                'location': 'New York, NY',
                'description': 'Manage cloud infrastructure, CI/CD pipelines, and deployment automation.',
                'requirements': ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Terraform', 'Linux', 'Python'],
                'experience_required': 3,
                'salary_range': '$110k - $150k',
                'posted_date': '2025-11-06',
                'job_type': 'Full-time',
            },
            {
                'id': 'job_005',
                'title': 'Full Stack Developer',
                'company': 'StartUp Co',
                'location': 'Austin, TX',
                'description': 'Build end-to-end web applications using modern tech stack. Startup environment.',
                'requirements': ['React', 'Node.js', 'MongoDB', 'REST API', 'JavaScript', 'Docker'],
                'experience_required': 2,
                'salary_range': '$90k - $130k',
                'posted_date': '2025-11-07',
                'job_type': 'Full-time',
            },
            {
                'id': 'job_006',
                'title': 'Data Engineer',
                'company': 'Data Corp',
                'location': 'Seattle, WA',
                'description': 'Build data pipelines and infrastructure for analytics at scale.',
                'requirements': ['Python', 'SQL', 'Spark', 'Kafka', 'AWS', 'Airflow', 'ETL'],
                'experience_required': 4,
                'salary_range': '$120k - $160k',
                'posted_date': '2025-11-08',
                'job_type': 'Full-time',
            },
            {
                'id': 'job_007',
                'title': 'Backend Engineer',
                'company': 'Microservices Inc',
                'location': 'Remote',
                'description': 'Design and implement scalable microservices architecture.',
                'requirements': ['Java', 'Spring', 'Microservices', 'Kubernetes', 'REST API', 'PostgreSQL'],
                'experience_required': 5,
                'salary_range': '$125k - $170k',
                'posted_date': '2025-11-09',
                'job_type': 'Full-time',
            },
            {
                'id': 'job_008',
                'title': 'Cloud Architect',
                'company': 'Enterprise Tech',
                'location': 'Boston, MA',
                'description': 'Design cloud-native solutions and lead architecture decisions.',
                'requirements': ['AWS', 'Azure', 'Kubernetes', 'Terraform', 'Python', 'Microservices'],
                'experience_required': 7,
                'salary_range': '$150k - $200k',
                'posted_date': '2025-11-10',
                'job_type': 'Full-time',
            },
        ]
    
    def search_jobs(
        self,
        keywords: str = "",
        location: str = "",
        limit: int = 50
    ) -> List[Dict]:
        """
        Search for jobs matching criteria
        
        Args:
            keywords: Search keywords (space-separated)
            location: Job location
            limit: Maximum number of results
            
        Returns:
            List of matching jobs
        """
        keyword_list = keywords.lower().split() if keywords else []
        matched_jobs = []
        
        for job in self.sample_jobs:
            # Create searchable text from job
            job_text = f"{job['title']} {job['description']} {' '.join(job['requirements'])}".lower()
            
            # Check keyword match
            if keyword_list:
                if not any(kw in job_text for kw in keyword_list):
                    continue
            
            # Check location match
            if location and location.lower() not in job['location'].lower():
                continue
            
            matched_jobs.append(job.copy())
        
        return matched_jobs[:limit]
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """
        Get specific job by ID
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job dictionary or None
        """
        for job in self.sample_jobs:
            if job['id'] == job_id:
                return job.copy()
        return None
    
    def filter_by_experience(self, jobs: List[Dict], min_exp: int, max_exp: int) -> List[Dict]:
        """
        Filter jobs by experience requirement
        
        Args:
            jobs: List of jobs
            min_exp: Minimum experience
            max_exp: Maximum experience
            
        Returns:
            Filtered job list
        """
        return [
            job for job in jobs
            if min_exp <= job.get('experience_required', 0) <= max_exp
        ]
    
    def filter_by_skills(self, jobs: List[Dict], required_skills: List[str]) -> List[Dict]:
        """
        Filter jobs by required skills
        
        Args:
            jobs: List of jobs
            required_skills: List of required skills
            
        Returns:
            Filtered job list
        """
        filtered = []
        required_set = set(s.lower() for s in required_skills)
        
        for job in jobs:
            job_skills = set(s.lower() for s in job.get('requirements', []))
            if required_set & job_skills:  # If any overlap
                filtered.append(job)
        
        return filtered
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all available jobs"""
        return [job.copy() for job in self.sample_jobs]
    
    def get_job_count(self) -> int:
        """Get total job count"""
        return len(self.sample_jobs)
    
    def add_sample_job(self, job: Dict):
        """Add a job to sample database"""
        self.sample_jobs.append(job.copy())
    
    def __repr__(self) -> str:
        """String representation"""
        return f"JobScraper(total_jobs={len(self.sample_jobs)})"
