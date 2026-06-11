import requests
import os
from datetime import datetime
import re

def fetch_remotive_jobs():
    """Fetch from Remotive"""
    jobs = []
    target_keywords = [
        "enablement", "operations", "workflow", "implementation", 
        "customer success", "program manager", "documentation",
        "learning", "content operations", "customer education", "product operations"
    ]
    exclude_keywords = [
        "sales", "engineer", "developer", "designer", "support", "retail",
        "delivery", "warehouse", "hospitality", "caretaker", "devops"
    ]
    
    try:
        url = "https://remotive.com/api/remote-jobs"
        response = requests.get(url, params={"limit": 100}, timeout=10)
        data = response.json()
        
        for job in data.get("jobs", []):
            title = (job.get("title") or "").lower()
            has_target = any(keyword in title for keyword in target_keywords)
            has_exclude = any(keyword in title for keyword in exclude_keywords)
            
            if has_target and not has_exclude:
                jobs.append({
                    "title": job.get("title", "N/A"),
                    "company": job.get("company_name", "N/A"),
                    "location": job.get("candidate_required_location", "Remote"),
                    "salary": job.get("salary") or "Not listed",
                    "description": (job.get("description") or "")[:150],
                    "url": job.get("url", "#"),
                    "company_url": job.get("company_url", ""),
                    "source": "Remotive"
                })
    except Exception as e:
        print(f"Remotive error: {e}")
    
    return jobs

def fetch_github_jobs():
    """Fetch from GitHub Jobs API"""
    jobs = []
    target_keywords = [
        "enablement", "operations", "workflow", "implementation", 
        "customer success", "program manager", "documentation",
        "learning", "content operations", "customer education"
    ]
    exclude_keywords = [
        "sales", "engineer", "developer", "designer", "devops", "backend", "frontend"
    ]
    
    try:
        url = "https://api.github.com/repos/github-community/githubjobs/issues"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        for job in data[:50]:  # Get first 50
            title = (job.get("title") or "").lower()
            body = (job.get("body") or "").lower()
            
            has_target = any(keyword in title or keyword in body for keyword in target_keywords)
            has_exclude = any(keyword in title for keyword in exclude_keywords)
            
            if has_target and not has_exclude and "remote" in body.lower():
                jobs.append({
                    "title": job.get("title", "N/A"),
                    "company": "Check listing",
                    "location": "Remote",
                    "salary": "Check listing",
                    "description": body[:150],
                    "url": job.get("html_url", "#"),
