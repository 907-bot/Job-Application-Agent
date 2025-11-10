#!/usr/bin/env python3
"""
Example: Customize Resume for Job Applications
Demonstrates the resume customization functionality of the Job Application Agent.

Usage:
    python examples/example_customize.py
"""

import json
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mayini_model import MAYINIModel, MAYINIVocabulary
from src.customizer import ResumeCustomizer
from src.scraper import JobScraper


def main():
    """Main example function."""
    
    print("=" * 70)
    print("Job Application Agent - Resume Customization Example")
    print("=" * 70)
    print()
    
    # Initialize components
    print("1. Initializing components...")
    vocab = MAYINIVocabulary(vocab_size=5000)
    model = MAYINIModel(
        vocab_size=5000,
        hidden_dim=256,
        num_heads=8,
        num_layers=4
    )
    customizer = ResumeCustomizer(model, vocab)
    scraper = JobScraper()
    print("   ✓ MAYINI model initialized")
    print("   ✓ Customizer initialized")
    print()
    
    # Load sample resume
    print("2. Loading sample resume...")
    sample_resume = customizer.get_sample_resume()
    print(f"   ✓ Loaded resume for: {sample_resume['name']}")
    print(f"   ✓ Email: {sample_resume['email']}")
    print(f"   ✓ Experience: {sample_resume['experience']}+ years")
    print(f"   ✓ Total skills: {len(sample_resume['skills'])}")
    print()
    
    # Display original resume
    print("3. Original Resume Summary:")
    print("-" * 70)
    print(f"   Name: {sample_resume['name']}")
    print(f"   Location: {sample_resume['location']}")
    print(f"   Professional Summary (first 100 chars):")
    print(f"   {sample_resume['professional_summary'][:100]}...")
    print()
    print(f"   Top Skills (first 10):")
    for skill in sample_resume['skills'][:10]:
        print(f"   • {skill}")
    print()
    
    # Get sample jobs
    print("4. Retrieving sample jobs for customization...")
    all_jobs = scraper.get_all_jobs()
    print(f"   ✓ Found {len(all_jobs)} jobs")
    print()
    
    # Customize for multiple jobs
    print("5. Customizing resume for different job opportunities:")
    print("=" * 70)
    
    jobs_to_customize = all_jobs[:3]
    customized_resumes = []
    
    for i, job in enumerate(jobs_to_customize, 1):
        print(f"\n   Job {i}: {job['title']} @ {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Requirements: {', '.join(job['requirements'][:5])}")
        
        # Customize resume
        customized = customizer.customize_for_job(job)
        customized_resumes.append(customized)
        
        print(f"   ✓ Resume customized successfully")
        
        # Show key customizations
        if 'customized_for' in customized:
            match_data = customized['customized_for']
            print(f"   ✓ Matching skills: {len(match_data.get('matching_skills', []))}")
            print(f"   ✓ Match score: {match_data.get('match_score', 0):.1%}")
        
        # Show customized summary (first part)
        if 'summary' in customized:
            print(f"   ✓ Customized summary (first 80 chars):")
            print(f"     {customized['summary'][:80]}...")
    
    print("\n" + "=" * 70)
    
    # Detailed customization for first job
    print("\n6. Detailed Customization Analysis (First Job):")
    print("-" * 70)
    
    first_job = jobs_to_customize[0]
    customized = customized_resumes[0]
    
    print(f"   Original Job Requirements:")
    for req in first_job['requirements']:
        print(f"   • {req}")
    
    print()
    print(f"   Customized Resume Skills (prioritized for this job):")
    for skill in customized.get('skills', [])[:10]:
        print(f"   • {skill}")
    
    print()
    print(f"   Customized Summary:")
    print(f"   {customized.get('summary', 'N/A')[:150]}...")
    print()
    
    # Generate cover letters
    print("7. Generating Cover Letters:")
    print("-" * 70)
    
    for i, (job, customized) in enumerate(zip(jobs_to_customize, customized_resumes), 1):
        print(f"\n   Job {i}: {job['title']} @ {job['company']}")
        
        # Generate cover letter
        cover_letter = customizer.generate_cover_letter(job, customized)
        
        print(f"   Cover Letter (first 150 chars):")
        print(f"   {cover_letter[:150]}...")
        print(f"   ✓ Generated successfully")
    
    # Batch customization
    print("\n8. Batch Customization (All Jobs):")
    print("-" * 70)
    
    batch_customized = customizer.batch_customize(all_jobs)
    print(f"   ✓ Successfully customized {len(batch_customized)} resumes")
    print()
    
    # Statistics
    print("9. Customization Statistics:")
    print("-" * 70)
    print(f"   Total jobs processed: {len(all_jobs)}")
    print(f"   Customizations created: {len(customized_resumes)}")
    print(f"   Batch customizations: {len(batch_customized)}")
    print()
    
    # Export customized resumes
    print("10. Exporting Customized Resumes:")
    print("-" * 70)
    
    export_data = {
        "export_timestamp": "2025-11-10T04:17:00Z",
        "original_resume": {
            "name": sample_resume['name'],
            "email": sample_resume['email'],
            "skills_count": len(sample_resume['skills']),
            "experience_years": sample_resume['experience']
        },
        "customizations": []
    }
    
    for job, customized in zip(jobs_to_customize, customized_resumes):
        export_data["customizations"].append({
            "job_title": job['title'],
            "company": job['company'],
            "customized_summary": customized.get('summary', '')[:100],
            "customized_skills": customized.get('skills', [])[:10],
            "match_score": customized.get('customized_for', {}).get('match_score', 0)
        })
    
    # Save to file
    output_file = Path("output/customized_resumes.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"   ✓ Customized resumes exported to: {output_file}")
    print()
    
    print("=" * 70)
    print("✓ Resume customization example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
