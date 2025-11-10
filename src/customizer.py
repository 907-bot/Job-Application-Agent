"""
Resume Customizer Module  
AI-powered resume customization for specific jobs
"""

from typing import Dict, List
from .mayini_model import MAYINIModel, MAYINIVocabulary


class ResumeCustomizer:
    """Customize resumes for specific job applications"""
    
    def __init__(self, model: MAYINIModel, vocab: MAYINIVocabulary):
        """
        Initialize resume customizer
        
        Args:
            model: MAYINI model for text generation
            vocab: Vocabulary for encoding/decoding
        """
        self.model = model
        self.vocab = vocab
        
        # Sample resume template
        self.sample_resume = {
            'name': 'Alex Chen',
            'email': 'alex.chen@email.com',
            'phone': '+1-555-0123',
            'location': 'San Francisco, CA',
            'experience': 6,
            'skills': [
                'Python', 'Java', 'Docker', 'Kubernetes', 'AWS',
                'Machine Learning', 'PostgreSQL', 'REST API', 'Git'
            ],
            'summary': 'Experienced software engineer with 6+ years building scalable distributed systems and machine learning applications',
            'experience_details': [
                'Led team of 8 engineers developing microservices platform serving 10M+ users',
                'Architected and deployed Kubernetes infrastructure reducing deployment time by 70%',
                'Implemented ML pipeline processing 1B+ events daily with 99.9% uptime',
                'Reduced API latency by 60% through query optimization and caching strategies'
            ],
            'education': 'BS Computer Science, Stanford University',
            'certifications': ['AWS Certified Solutions Architect', 'Kubernetes Administrator']
        }
    
    def customize_for_job(self, job: Dict) -> Dict:
        """
        Customize resume for specific job
        
        Args:
            job: Job dictionary with requirements
            
        Returns:
            Customized resume dictionary
        """
        job_desc = job.get('description', '')
        job_title = job.get('title', '')
        job_skills = job.get('requirements', [])
        company = job.get('company', '')
        
        # Extract matching skills
        matching_skills = self._get_matching_skills(self.sample_resume['skills'], job_skills)
        
        # Reorder skills to prioritize job requirements
        prioritized_skills = matching_skills + [
            s for s in self.sample_resume['skills']
            if s not in matching_skills
        ]
        
        # Generate customized summary
        customized_summary = self._generate_custom_summary(
            self.sample_resume,
            job_title,
            company,
            matching_skills
        )
        
        # Select most relevant experience details
        relevant_experience = self._select_relevant_experience(
            self.sample_resume['experience_details'],
            job_skills
        )
        
        # Build customized resume
        customized_resume = {
            'name': self.sample_resume['name'],
            'email': self.sample_resume['email'],
            'phone': self.sample_resume['phone'],
            'location': self.sample_resume['location'],
            'experience': self.sample_resume['experience'],
            'skills': prioritized_skills[:10],  # Top 10 skills
            'summary': customized_summary,
            'experience_details': relevant_experience,
            'education': self.sample_resume['education'],
            'certifications': self.sample_resume['certifications'],
            'customized_for': {
                'job_title': job_title,
                'company': company,
                'matching_skills': matching_skills,
                'match_score': len(matching_skills) / len(job_skills) if job_skills else 0
            }
        }
        
        return customized_resume
    
    def _get_matching_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Find skills that match between resume and job"""
        resume_set = set(s.lower() for s in resume_skills)
        job_set = set(s.lower() for s in job_skills)
        
        matching = resume_set & job_set
        
        # Return original casing from resume
        return [s for s in resume_skills if s.lower() in matching]
    
    def _generate_custom_summary(
        self,
        resume: Dict,
        job_title: str,
        company: str,
        matching_skills: List[str]
    ) -> str:
        """Generate customized professional summary"""
        
        experience_years = resume.get('experience', 0)
        skills_str = ', '.join(matching_skills[:5])
        
        summary = (
            f"Experienced software engineer with {experience_years}+ years of expertise "
            f"specializing in {skills_str}. "
            f"Proven track record in building scalable systems and delivering high-impact solutions. "
            f"Passionate about leveraging technology to solve complex problems."
        )
        
        return summary
    
    def _select_relevant_experience(
        self,
        experience_details: List[str],
        job_skills: List[str]
    ) -> List[str]:
        """Select most relevant experience bullets"""
        
        # Score each experience detail
        scored_experiences = []
        job_skills_lower = set(s.lower() for s in job_skills)
        
        for exp in experience_details:
            exp_lower = exp.lower()
            score = sum(1 for skill in job_skills_lower if skill in exp_lower)
            scored_experiences.append((score, exp))
        
        # Sort by score (descending) and return top experiences
        scored_experiences.sort(reverse=True, key=lambda x: x[0])
        
        return [exp for score, exp in scored_experiences[:4]]
    
    def generate_cover_letter(self, job: Dict, resume: Dict) -> str:
        """
        Generate cover letter for job application
        
        Args:
            job: Job dictionary
            resume: Resume dictionary
            
        Returns:
            Cover letter text
        """
        name = resume.get('name', 'Applicant')
        job_title = job.get('title', 'Position')
        company = job.get('company', 'Company')
        matching_skills = resume.get('customized_for', {}).get('matching_skills', [])
        
        cover_letter = f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. 
With {resume.get('experience', 0)} years of professional experience and expertise in 
{', '.join(matching_skills[:3])}, I am confident I would be a valuable addition to your team.

{resume.get('summary', '')}

I am particularly excited about this opportunity because it aligns perfectly with my 
technical skills and career goals. I look forward to the possibility of discussing how 
my experience and skills can contribute to {company}'s success.

Thank you for considering my application.

Best regards,
{name}
        """.strip()
        
        return cover_letter
    
    def batch_customize(self, jobs: List[Dict]) -> List[Dict]:
        """
        Customize resume for multiple jobs
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of customized resumes
        """
        return [self.customize_for_job(job) for job in jobs]
    
    def get_sample_resume(self) -> Dict:
        """Get the sample resume"""
        return self.sample_resume.copy()
    
    def update_sample_resume(self, updates: Dict):
        """Update sample resume with new information"""
        self.sample_resume.update(updates)
    
    def __repr__(self) -> str:
        """String representation"""
        return f"ResumeCustomizer(resume={self.sample_resume['name']})"
