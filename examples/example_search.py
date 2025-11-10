#!/usr/bin/env python3
"""
Example: Search for Jobs and Find Matches
Demonstrates the job search and matching functionality of the Job Application Agent.

Usage:
    python examples/example_search.py
"""

import json
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import JobScraper
from src.classifier import JobRelevanceClassifier
from src.utils import UtilityFunctions


def main():
    """Main example function."""
    
    print("=" * 60)
    print("Job Application Agent - Search Example")
    print("=" * 60)
    print()
    
    # Initialize components
    print("1. Initializing components...")
    scraper = JobScraper()
    classifier = JobRelevanceClassifier(embedding_dim=300, hidden_dim=128)
    utils = UtilityFunctions()
    print("   ✓ Scraper initialized with sample jobs")
    print("   ✓ Classifier initialized")
    print()
    
    # Get all available jobs
    print("2. Getting all available jobs...")
    all_jobs = scraper.get_all_jobs()
    print(f"   ✓ Found {len(all_jobs)} total jobs in database")
    print()
    
    # Display available jobs
    print("3. Available Jobs:")
    print("-" * 60)
    for i, job in enumerate(all_jobs, 1):
        print(f"{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Experience Required: {job['experience_required']} years")
        print()
    
    # Search with keywords
    print("4. Searching for Python-related jobs...")
    keyword_results = scraper.search_jobs(keywords="python", limit=5)
    print(f"   ✓ Found {len(keyword_results)} jobs matching 'python'")
    for job in keyword_results[:3]:
        print(f"   - {job['title']} @ {job['company']}")
    print()
    
    # Search by location
    print("5. Searching for Remote jobs...")
    location_results = scraper.search_jobs(location="Remote", limit=5)
    print(f"   ✓ Found {len(location_results)} remote jobs")
    for job in location_results[:2]:
        print(f"   - {job['title']} in {job['location']}")
    print()
    
    # Filter by experience
    print("6. Filtering jobs by experience requirement...")
    experience_filtered = scraper.filter_by_experience(all_jobs, min_years=3, max_years=5)
    print(f"   ✓ Found {len(experience_filtered)} jobs requiring 3-5 years")
    for job in experience_filtered[:2]:
        print(f"   - {job['title']} ({job['experience_required']} years)")
    print()
    
    # Rank jobs by relevance
    print("7. Ranking jobs by relevance...")
    resume_skills = [
        "Python", "Docker", "AWS", "PostgreSQL", 
        "REST API", "Microservices", "Git"
    ]
    
    ranked_jobs = classifier.rank_jobs(all_jobs, resume_skills)
    print(f"   ✓ Ranked {len(ranked_jobs)} jobs by relevance")
    print("   Top 3 matches:")
    for i, (job, score) in enumerate(ranked_jobs[:3], 1):
        print(f"   {i}. {job['title']} - Score: {score:.2%}")
    print()
    
    # Get match details for best job
    if ranked_jobs:
        print("8. Detailed match analysis for top job:")
        best_job, best_score = ranked_jobs[0]
        details = classifier.get_match_details(best_job, resume_skills)
        
        print(f"   Job: {best_job['title']}")
        print(f"   Company: {best_job['company']}")
        print(f"   Relevance Score: {details['relevance_score']:.2%}")
        print(f"   Recommendation: {details['recommendation']}")
        print()
        print(f"   Matching Skills: {', '.join(details['matching_skills'])}")
        print(f"   Missing Skills: {', '.join(details['missing_skills'])}")
        print()
    
    # Statistics
    print("9. Search Statistics:")
    print("-" * 60)
    print(f"   Total jobs in database: {len(all_jobs)}")
    print(f"   Python jobs found: {len(keyword_results)}")
    print(f"   Remote jobs available: {len(location_results)}")
    print(f"   Jobs matching experience (3-5 yrs): {len(experience_filtered)}")
    print()
    
    # Export results
    print("10. Exporting results...")
    results = {
        "search_timestamp": "2025-11-10T04:17:00Z",
        "total_jobs": len(all_jobs),
        "keyword_search": {
            "keyword": "python",
            "results_count": len(keyword_results),
            "jobs": keyword_results[:3]
        },
        "location_search": {
            "location": "Remote",
            "results_count": len(location_results),
            "jobs": location_results[:2]
        },
        "top_matches": [
            {
                "job": job,
                "relevance_score": score
            }
            for job, score in ranked_jobs[:3]
        ]
    }
    
    # Save results
    output_file = Path("output/search_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"   ✓ Results saved to {output_file}")
    print()
    
    print("=" * 60)
    print("✓ Search example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
