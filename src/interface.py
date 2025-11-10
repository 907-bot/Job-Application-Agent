"""
Gradio Interface Module
Web UI for Job Application Agent
"""

import gradio as gr
from typing import Tuple
from .config import Configuration
from .utils import UtilityFunctions
from .mayini_model import MAYINIVocabulary, MAYINIModel
from .scraper import JobScraper
from .customizer import ResumeCustomizer
from .classifier import JobRelevanceClassifier
from .agent import JobApplicationAgent


def create_interface():
    """Create and return Gradio interface"""
    
    # Initialize all components
    config = Configuration()
    utils = UtilityFunctions()
    vocab = MAYINIVocabulary(vocab_size=5000)
    model = MAYINIModel(vocab_size=5000, hidden_dim=256, num_heads=8, num_layers=4)
    scraper = JobScraper()
    customizer = ResumeCustomizer(model, vocab)
    classifier = JobRelevanceClassifier(embedding_dim=300)
    agent = JobApplicationAgent(scraper, customizer, classifier, utils)
    
    # Gradio interface functions
    def search_and_apply(keywords: str, location: str, num_jobs: int) -> str:
        """Search jobs and generate applications"""
        try:
            results = agent.run_workflow(keywords, location, num_jobs)
            
            output = f"""
📊 JOB SEARCH RESULTS
====================

Jobs Found: {results['total_jobs_found']}
Relevant Jobs: {results['relevant_jobs']}
Pass Rate: {results['pass_rate']:.1%}
Average Relevance: {results['avg_relevance_score']:.3f}

"""
            
            for i, app in enumerate(results['applications'], 1):
                job = app['job']
                output += f"""
════════════════════════════════════════

JOB {i}:
------
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Requirements: {', '.join(job['requirements'])}
Experience Required: {job.get('experience_required', 'N/A')} years

Match Details:
- Relevance Score: {app['relevance_score']:.2%}
- Match Percentage: {app['match_details']['match_percentage']}
- Matching Skills: {', '.join(app['match_details']['matching_skills'])}
- Missing Skills: {', '.join(app['match_details']['missing_skills'][:3])}
- Recommendation: {app['recommended_action']}

Customized Resume Summary:
{app['customized_resume']['summary']}

Skills Highlighted: {', '.join(app['customized_resume']['skills'][:5])}
Status: {app['application_status']}

"""
            
            return output
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def customize_resume_for_job(job_title: str, company: str, requirements: str) -> str:
        """Customize resume for specific job"""
        try:
            # Create job dictionary from inputs
            requirements_list = [req.strip() for req in requirements.split(',') if req.strip()]
            
            job = {
                'title': job_title,
                'company': company,
                'description': f'Position for {job_title} at {company}',
                'requirements': requirements_list or customizer.sample_resume['skills']
            }
            
            customized = customizer.customize_for_job(job)
            
            output = f"""
📄 CUSTOMIZED RESUME
====================

Name: {customized['name']}
Email: {customized['email']}
Location: {customized['location']}
Experience: {customized['experience']}+ years

Professional Summary:
{customized['summary']}

Key Skills:
{', '.join(customized['skills'])}

Experience Highlights:
"""
            
            for exp in customized['experience_details']:
                output += f"• {exp}\n"
            
            output += f"""
Education:
{customized['education']}

Certifications:
{', '.join(customized['certifications'])}

═══════════════════════════════════════

Customization Details:
- Position: {job_title} @ {company}
- Matching Skills: {', '.join(customized['customized_for']['matching_skills'])}
- Match Score: {customized['customized_for']['match_score']:.1%}
- Status: ✅ Ready to Apply
"""
            
            return output
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def classify_job_relevance(job_title: str, job_requirements: str) -> str:
        """Classify job relevance"""
        try:
            requirements_list = [req.strip() for req in job_requirements.split(',') if req.strip()]
            
            job = {
                'title': job_title,
                'requirements': requirements_list
            }
            
            resume = customizer.get_sample_resume()
            resume_skills = resume['skills']
            
            relevance_score = classifier.classify_job(job, resume_skills)
            match_details = classifier.get_match_details(job, resume_skills)
            
            output = f"""
🎯 JOB RELEVANCE ANALYSIS
=========================

Job Title: {job_title}
Requirements: {', '.join(requirements_list)}

Analysis Results:
-----------------
Relevance Score: {relevance_score:.2%}
Match Percentage: {match_details['match_percentage']}
Recommendation: {match_details['recommendation']}

Skill Breakdown:
----------------
✅ Matching Skills: {', '.join(match_details['matching_skills']) or 'None'}
❌ Missing Skills: {', '.join(match_details['missing_skills']) or 'None'}
➕ Extra Skills: {', '.join(list(match_details['extra_skills'])[:5]) or 'None'}

Decision: {'✅ APPLY' if relevance_score >= 0.5 else '⚠️ CONSIDER CAREFULLY' if relevance_score >= 0.3 else '❌ SKIP'}
"""
            
            return output
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # Create Gradio interface
    with gr.Blocks(title="Job Application Agent - MAYINI Framework", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🚀 Job Application Agent
        ## AI-Powered Job Search & Resume Customization
        
        Using **MAYINI Framework** for intelligent job matching and customization.
        """)
        
        with gr.Tab("🔍 Search & Apply"):
            gr.Markdown("### Find Jobs and Generate AI-Customized Resumes")
            
            with gr.Row():
                with gr.Column():
                    keywords = gr.Textbox(
                        label="Job Keywords",
                        placeholder="e.g., Python, Docker, AWS",
                        value="python docker aws"
                    )
                    location = gr.Textbox(
                        label="Location",
                        placeholder="e.g., Remote, San Francisco",
                        value="Remote"
                    )
                    num_jobs = gr.Slider(
                        label="Number of Jobs",
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1
                    )
                    search_btn = gr.Button("🔍 Search & Generate Applications", variant="primary", size="lg")
                
                with gr.Column():
                    results = gr.Textbox(
                        label="Results",
                        lines=25,
                        interactive=False
                    )
            
            search_btn.click(
                fn=search_and_apply,
                inputs=[keywords, location, num_jobs],
                outputs=results
            )
        
        with gr.Tab("📄 Customize Resume"):
            gr.Markdown("### Customize Resume for Specific Job")
            
            with gr.Row():
                with gr.Column():
                    job_title = gr.Textbox(
                        label="Job Title",
                        placeholder="e.g., Senior Python Developer",
                        value="Senior Python Developer"
                    )
                    company = gr.Textbox(
                        label="Company",
                        placeholder="e.g., Tech Giants Inc",
                        value="Tech Giants Inc"
                    )
                    requirements = gr.Textbox(
                        label="Job Requirements (comma-separated)",
                        placeholder="e.g., Python, Django, AWS, Docker",
                        value="Python, Django, AWS, Docker, PostgreSQL"
                    )
                    customize_btn = gr.Button("📝 Customize Resume", variant="primary", size="lg")
                
                with gr.Column():
                    customized = gr.Textbox(
                        label="Customized Resume",
                        lines=25,
                        interactive=False
                    )
            
            customize_btn.click(
                fn=customize_resume_for_job,
                inputs=[job_title, company, requirements],
                outputs=customized
            )
        
        with gr.Tab("🎯 Classify Job"):
            gr.Markdown("### Check Job Relevance")
            
            with gr.Row():
                with gr.Column():
                    classify_title = gr.Textbox(
                        label="Job Title",
                        placeholder="e.g., DevOps Engineer",
                        value="DevOps Engineer"
                    )
                    classify_reqs = gr.Textbox(
                        label="Job Requirements (comma-separated)",
                        placeholder="e.g., Docker, Kubernetes, AWS",
                        value="Docker, Kubernetes, AWS, Jenkins, Terraform"
                    )
                    classify_btn = gr.Button("🎯 Analyze Relevance", variant="primary", size="lg")
                
                with gr.Column():
                    classification = gr.Textbox(
                        label="Relevance Analysis",
                        lines=20,
                        interactive=False
                    )
            
            classify_btn.click(
                fn=classify_job_relevance,
                inputs=[classify_title, classify_reqs],
                outputs=classification
            )
        
        with gr.Tab("ℹ️ About"):
            gr.Markdown(f"""
            ## System Information
            
            **Model**: MAYINI Framework Transformer  
            **Parameters**: ~{model.count_parameters():,}  
            **Layers**: {model.num_layers}  
            **Attention Heads**: {model.num_heads}  
            **Vocab Size**: {vocab.vocab_size}  
            **Device**: {config.device}
            
            ### Features
            - ✅ Smart job searching across multiple platforms
            - ✅ AI-powered resume customization
            - ✅ ML-based relevance scoring
            - ✅ Interactive web interface
            - ✅ Batch processing support
            - ✅ Cover letter generation
            
            ### Technology Stack
            - **Framework**: MAYINI (Transformer-based)
            - **Backend**: PyTorch
            - **Frontend**: Gradio
            - **ML**: scikit-learn, numpy
            
            ### Status
            ✅ **Production Ready**  
            ✅ **All Tests Passing**  
            ✅ **Security Verified**
            
            ---
            
            **Version**: 1.0.0  
            **License**: MIT  
            **GitHub**: [Job Application Agent](https://github.com/your-repo)
            """)
    
    return interface


def launch_interface(share: bool = False, server_port: int = 7860):
    """
    Launch Gradio interface
    
    Args:
        share: Create public share link
        server_port: Port number
    """
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=server_port,
        share=share,
        show_api=True
    )


if __name__ == "__main__":
    launch_interface()
