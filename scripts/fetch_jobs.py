def fetch_remotive_jobs():
    """Fetch from Remotive - STRICT filtering for YOUR roles"""
    jobs = []
    
    # EXACT roles you want
    target_keywords = [
        "enablement specialist",
        "customer enablement",
        "product operations",
        "operations manager",
        "implementation specialist",
        "implementation manager",
        "program manager",
        "learning operations",
        "content operations",
        "customer education",
        "customer success manager",
        "customer success engineer",
        "workflow architect",
        "workflow designer",
        "documentation specialist",
        "technical writer"
    ]
    
    # EXCLUDE these STRICTLY
    exclude_keywords = [
        "data analyst", "data science", "data labeling", "data entry",
        "engineer", "developer", "designer", "devops",
        "sales", "account executive", "business development",
        "support agent", "customer support", "help desk",
        "warehouse", "delivery", "retail", "hospitality",
        "caretaker", "postie", "driver", "apprentice",
        "spanish speaker", "bilingual", "translator"
    ]
    
    try:
        url = "https://remotive.com/api/remote-jobs"
        response = requests.get(url, params={"limit": 100}, timeout=10)
        data = response.json()
        
        for job in data.get("jobs", []):
            title = (job.get("title") or "").lower()
            description = (job.get("description") or "").lower()
            location = job.get("candidate_required_location", "").lower()
            
            # Must be USA/North America
            if not any(region in location for region in ["usa", "united states", "north america", "anywhere"]):
                continue
            
            # MUST have one of YOUR target keywords (not loose match)
            has_target = any(target in title for target in target_keywords)
            if not has_target:
                continue
            
            # MUST NOT have exclude keywords
            has_exclude = any(exclude in title or exclude in description for exclude in exclude_keywords)
            if has_exclude:
                continue
            
            # Must be Maine eligible
            if not is_maine_eligible(description):
                continue
            
            # Must be async eligible
            if not is_async_eligible(description):
                continue
            
            jobs.append({
                "title": job.get("title", "N/A"),
                "company": job.get("company_name", "N/A"),
                "location": location,
                "salary": job.get("salary") or "Not listed",
                "description": (job.get("description") or "")[:200],
                "url": job.get("url", "#"),
                "company_url": job.get("company_url", ""),
                "source": "Remotive"
            })
    except Exception as e:
        print(f"Remotive error: {e}")
    
    return jobs
