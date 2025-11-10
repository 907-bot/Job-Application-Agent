#!/usr/bin/env python3
"""
Example: Classify and Rank Jobs by Relevance
Demonstrates the job classification and ranking functionality of the Job Application Agent.

Usage:
    python examples/example_classify.py
"""

import json
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.classifier import JobRelevanceClassifier
from src.scraper import JobScraper
from src.customizer import ResumeCustomizer
from src.mayini_model import MAYINIModel, MAYINIVocabulary


def main():
    """Main example function."""
    
    print("=" * 70)
    print("Job Application Agent - Job Classification & Ranking Example")
    print("=" * 70)
    print()
    
    # Initialize components
    print("1. Initializing components...")
    classifier = JobRelevanceClassifier(embedding_dim=300, hidden_dim=128)
    scraper = JobScraper()
    vocab = MAYINIVocabulary(vocab_size=5000)
    model = MAYINIModel(vocab_size=5000, hidden_dim=256, num_heads=8, num_layers=4)
    customizer = ResumeCustomizer(model, vocab)
    
    print("   ✓ Classifier initialized")
    print("   ✓ Scraper initialized")
    print("   ✓ Resume customizer ready")
    print()
    
    # Get candidate skills from resume
    print("2. Loading candidate profile...")
    resume = customizer.get_sample_resume()
    candidate_skills = resume['skills']
    print(f"   ✓ Candidate: {resume['name']}")
    print(f"   ✓ Location: {resume['location']}")
    print(f"   ✓ Experience: {resume['experience']}+ years")
    print(f"   ✓ Skills: {len(candidate_skills)} total")
    print(f"   ✓ Top 5 skills: {', '.join(candidate_skills[:5])}")
    print()
    
    # Get all jobs
    print("3. Loading job opportunities...")
    all_jobs = scraper.get_all_jobs()
    print(f"   ✓ Found {len(all_jobs)} job opportunities")
    print()
    
    # Classify each job
    print("4. Classifying job relevance...")
    print("-" * 70)
    
    classification_results = []
    
    for job in all_jobs:
        # Get classification score
        score = classifier.classify_job(job, candidate_skills)
        
        # Get detailed match information
        details = classifier.get_match_details(job, candidate_skills)
        
        classification_results.append({
            'job': job,
            'score': score,
            'details': details
        })
        
        print(f"\n   Job: {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Relevance Score: {score:.1%}")
        print(f"   Recommendation: {details['recommendation']}")
        print(f"   Matching Skills: {', '.join(details['matching_skills'][:3])}")
        if details['missing_skills']:
            print(f"   Missing Skills: {', '.join(details['missing_skills'][:3])}")
    
    print("\n" + "=" * 70)
    
    # Rank jobs by relevance
    print("\n5. Ranking Jobs by Relevance:")
    print("-" * 70)
    
    ranked_jobs = classifier.rank_jobs(all_jobs, candidate_skills)
    
    for rank, (job, score) in enumerate(ranked_jobs, 1):
        match_level = "Excellent" if score >= 0.8 else "Good" if score >= 0.6 else "Fair" if score >= 0.4 else "Poor"
        print(f"\n   {rank}. {job['title']}")
        print(f"      Company: {job['company']}")
        print(f"      Location: {job['location']}")
        print(f"      Relevance: {score:.1%} ({match_level})")
        print(f"      Salary: {job.get('salary_range', 'Not specified')}")
    
    # Filter by relevance threshold
    print("\n6. Filtering Jobs by Relevance Threshold:")
    print("-" * 70)
    
    threshold = 0.5
    relevant_jobs = classifier.filter_relevant_jobs(all_jobs, candidate_skills, threshold=threshold)
    
    print(f"\n   Threshold: {threshold:.0%}")
    print(f"   Jobs meeting threshold: {len(relevant_jobs)}")
    
    for job, score in relevant_jobs:
        print(f"\n   ✓ {job['title']} @ {job['company']}")
        print(f"     Score: {score:.1%}")
    
    # Detailed analysis of top job
    print("\n7. Detailed Analysis of Top Match:")
    print("-" * 70)
    
    if ranked_jobs:
        top_job, top_score = ranked_jobs[0]
        details = classifier.get_match_details(top_job, candidate_skills)
        
        print(f"\n   Job: {top_job['title']}")
        print(f"   Company: {top_job['company']}")
        print(f"   Location: {top_job['location']}")
        print(f"   Experience Required: {top_job['experience_required']} years")
        print()
        
        print(f"   Relevance Score: {details['relevance_score']:.1%}")
        print(f"   Recommendation: {details['recommendation']}")
        print()
        
        print(f"   Matching Skills ({len(details['matching_skills'])}):")
        for skill in details['matching_skills']:
            print(f"   ✓ {skill}")
        
        if details['missing_skills']:
            print()
            print(f"   Missing Skills ({len(details['missing_skills'])}):")
            for skill in details['missing_skills']:
                print(f"   ✗ {skill}")
    
    # Comparison matrix
    print("\n8. Job Comparison Matrix:")
    print("-" * 70)
    print(f"\n   {'Job Title':<30} {'Company':<20} {'Score':<10} {'Rec.':<15}")
    print("   " + "-" * 75)
    
    for job, score in ranked_jobs[:5]:
        details = classifier.get_match_details(job, candidate_skills)
        rec = "Recommended" if score >= 0.6 else "Consider"
        print(f"   {job['title']:<30} {job['company']:<20} {score:>6.0%}    {rec:<15}")
    
    # Statistics and summary
    print("\n9. Classification Summary Statistics:")
    print("-" * 70)
    
    scores = [r['score'] for r in classification_results]
    
    print(f"\n   Total Jobs Analyzed: {len(all_jobs)}")
    print(f"   Average Relevance: {sum(scores) / len(scores):.1%}")
    print(f"   Highest Score: {max(scores):.1%}")
    print(f"   Lowest Score: {min(scores):.1%}")
    print()
    
    # Count by relevance tiers
    excellent = sum(1 for s in scores if s >= 0.8)
    good = sum(1 for s in scores if 0.6 <= s < 0.8)
    fair = sum(1 for s in scores if 0.4 <= s < 0.6)
    poor = sum(1 for s in scores if s < 0.4)
    
    print(f"   Excellent (80%+): {excellent}")
    print(f"   Good (60-80%): {good}")
    print(f"   Fair (40-60%): {fair}")
    print(f"   Poor (<40%): {poor}")
    print()
    
    # Export results
    print("10. Exporting Classification Results:")
    print("-" * 70)
    
    export_data = {
        "classification_timestamp": "2025-11-10T04:17:00Z",
        "candidate": {
            "name": resume['name'],
            "experience_years": resume['experience'],
            "skills_count": len(candidate_skills)
        },
        "analysis": {
            "total_jobs_analyzed": len(all_jobs),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "jobs_recommended": sum(1 for s in scores if s >= 0.6)
        },
        "top_matches": [
            {
                "rank": rank,
                "job_title": job['title'],
                "company": job['company'],
                "location": job['location'],
                "relevance_score": score,
                "matching_skills": classifier.get_match_details(job, candidate_skills)['matching_skills'],
                "missing_skills": classifier.get_match_details(job, candidate_skills)['missing_skills']
            }
            for rank, (job, score) in enumerate(ranked_jobs[:5], 1)
        ]
    }
    
    # Save to file
    output_file = Path("output/classification_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"   ✓ Classification results exported to: {output_file}")
    print()
    
    print("=" * 70)
    print("✓ Job classification example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
