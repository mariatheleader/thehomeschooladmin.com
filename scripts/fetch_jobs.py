import requests
import os
from datetime import datetime

def is_maine_eligible(job_text):
    """Check if job allows Maine workers"""
    job_text_lower = str(job_text).lower()
    
    # Exclude if it says USA only (California, Texas, NY, etc specific states)
    exclude_locations = [
        "california only", "texas only", "new york only", "ny only",
        "west coast only", "east coast only", "pacific time zone",
        "pst only", "pt only", "cst only", "ct only",
        "no maine", "excluding maine"
    ]
    
    for location in exclude_locations:
        if location in job_text_lower:
            return False
    
    return True

def is_async_eligible(job_text):
    """Check if job is truly async/remote friendly"""
    job_text_lower = str(job_text).lower()
    
    # Must have async signals
    async_signals = [
        "asynchronous", "async", "no meeting", "flexible hours",
        "work from home", "distributed", "no time zone requirement",
        "flexible schedule", "self-paced"
    ]
    
    # Exclude real-time signals
    exclude_signals = [
        "real-time collaboration", "same time zone", "synchronous",
        "9-5", "fixed hours", "core hours", "standing meetings"
    ]
    
    has_async = any(signal in job_text_lower for signal in async_signals)
    has_exclude = any(signal in job_text_lower for signal in exclude_signals)
    
    return has_async and not has_exclude

def fetch_remotive_jobs():
    """Fetch from Remotive - filtered for USA async Maine-eligible"""
    jobs = []
    target_keywords = [
        "enablement", "operations", "workflow", "implementation", 
        "customer success", "program manager", "documentation",
        "learning", "content operations", "customer education", "product operations",
        "implementation specialist", "support specialist"
    ]
    exclude_keywords = [
        "sales", "engineer", "developer", "designer", "support", "retail",
        "delivery", "warehouse", "hospitality", "caretaker", "devops",
        "data scientist", "machine learning", "frontend", "backend"
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
            
            # Must have target keywords
            has_target = any(keyword in title or keyword in description for keyword in target_keywords)
            if not has_target:
                continue
            
            # Must not have exclude keywords
            has_exclude = any(keyword in title for keyword in exclude_keywords)
            if has_exclude:
                continue
            
            # Must be Maine eligible
            if not is_maine_eligible(description):
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

def fetch_github_jobs():
    """Fetch from GitHub Jobs - USA async only"""
    jobs = []
    target_keywords = [
        "enablement", "operations", "workflow", "implementation",
        "customer success", "program manager", "documentation",
        "learning", "content operations"
    ]
    
    try:
        url = "https://api.github.com/repos/github-community/githubjobs/issues"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        for job in data[:100]:
            title = (job.get("title") or "").lower()
            body = (job.get("body") or "").lower()
            
            # Must say remote/work from home
            if "remote" not in body and "work from home" not in body:
                continue
            
            # Must be USA
            if "usa" not in body and "united states" not in body and "us only" not in body:
                continue
            
            # Must be async eligible
            if not is_async_eligible(body):
                continue
            
            # Must be Maine eligible
            if not is_maine_eligible(body):
                continue
            
            # Must have target keyword
            has_target = any(keyword in title or keyword in body for keyword in target_keywords)
            if not has_target:
                continue
            
            jobs.append({
                "title": job.get("title", "N/A"),
                "company": "Check listing",
                "location": "Remote - USA",
                "salary": "Check listing",
                "description": body[:200],
                "url": job.get("html_url", "#"),
                "company_url": "",
                "source": "GitHub Jobs"
            })
    except Exception as e:
        print(f"GitHub Jobs error: {e}")
    
    return jobs

def fetch_devto_jobs():
    """Fetch from Dev.to - USA async only"""
    jobs = []
    target_keywords = [
        "enablement", "operations", "workflow", "implementation",
        "customer success", "program manager", "documentation",
        "learning", "content operations"
    ]
    
    try:
        url = "https://dev.to/api/articles"
        params = {"tag": "remote", "per_page": 50}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        for article in data:
            if "job" not in article.get("tag_list", []):
                continue
            
            title = (article.get("title") or "").lower()
            body = (article.get("body_markdown") or "").lower()
            
            # Must be USA
            if not any(region in body for region in ["usa", "united states", "us based", "us only"]):
                continue
            
            # Must be async eligible
            if not is_async_eligible(body):
                continue
            
            # Must be Maine eligible
            if not is_maine_eligible(body):
                continue
            
            # Must have target keyword
            has_target = any(keyword in title or keyword in body for keyword in target_keywords)
            if not has_target:
                continue
            
            jobs.append({
                "title": article.get("title", "N/A"),
                "company": "Check listing",
                "location": "Remote - USA",
                "salary": "Check listing",
                "description": article.get("description", "")[:200],
                "url": article.get("url", "#"),
                "company_url": "",
                "source": "Dev.to"
            })
    except Exception as e:
        print(f"Dev.to error: {e}")
    
    return jobs

def fetch_all_jobs():
    """Fetch and deduplicate"""
    all_jobs = []
    
    print("Fetching USA async remote jobs eligible for Maine...")
    all_jobs.extend(fetch_remotive_jobs())
    all_jobs.extend(fetch_github_jobs())
    all_jobs.extend(fetch_devto_jobs())
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique_jobs.append(job)
    
    return unique_jobs[:25]

def send_email_sendgrid(jobs):
    """Send via SendGrid"""
    
    api_key = os.getenv("SENDGRID_API_KEY")
    sender_email = "maria@thehomeschooladmin.com"
    
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                📧 USA Async Remote Jobs (Maine Eligible)
            </h2>
            <p style="font-size: 16px; color: #555;">
                <strong>{len(jobs)}</strong> qualified opportunities for you today.
            </p>
    """
    
    if jobs:
        for i, job in enumerate(jobs, 1):
            company_link = f'<a href="{job["company_url"]}" style="color: #0645ad;">{job["company"]}</a>' if job["company_url"] else job["company"]
            
            html += f"""
            <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-left: 4px solid #3498db; border-radius: 4px;">
                <p style="margin: 0 0 8px 0;">
                    <strong style="font-size: 16px;">{i}. {job['title']}</strong>
                </p>
                <p style="margin: 0 0 5px 0; color: #555;">
                    <strong>Company:</strong> {company_link}
                </p>
                <p style="margin: 0 0 5px 0; color: #555;">
                    <strong>Location:</strong> {job['location']} | <strong>Salary:</strong> {job['salary']}
                </p>
                <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">
                    {job['description']}
                </p>
                <p style="margin: 0;">
                    <a href="{job['url']}" style="display: inline-block; padding: 8px 14px; background: #3498db; color: white; text-decoration: none; border-radius: 4px;">
                        Apply →
                    </a>
                </p>
                <p style="margin: 5px 0 0 0; font-size: 11px; color: #999;">
                    {job['source']}
                </p>
            </div>
            """
    else:
        html += "<p style='color: #999;'>No matching jobs found today. Try again tomorrow!</p>"
    
    html += """
        </body>
    </html>
    """
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "personalizations": [{
            "to": [{"email": "maria.galyean.work@gmail.com"}]
        }],
        "from": {"email": sender_email},
        "subject": f"🎯 USA Async Remote Jobs - Maine Eligible ({len(jobs)}) - {datetime.now().strftime('%B %d')}",
        "content": [{
            "type": "text/html",
            "value": html
        }]
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 202:
        print(f"✅ Email sent! {len(jobs)} USA async remote jobs (Maine eligible)")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    jobs = fetch_all_jobs()
    send_email_sendgrid(jobs)
